"""Processing service for managing analysis pipeline.

@feature F005 - Pose Estimation Processing

Implements:
- AC-025: Video processed with 33-joint XYZ coordinate extraction
- AC-026: Selected subject tracked across frames via bounding box
- AC-027: Successful pose data stored in structured JSON
- AC-028: Over 20% frame failure marks analysis as failed with guidance
- AC-029: Processing progress logged and retrievable via status endpoint
"""
import logging
import os
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import get_settings
from api.models.analysis import Analysis, AnalysisStatus
from api.models.body_specs import BodySpecs
from api.models.subject import Subject
from api.models.upload import Video

logger = logging.getLogger(__name__)


class ProcessingError(Exception):
    """Base exception for processing errors."""

    pass


class VideoNotFoundError(ProcessingError):
    """Video not found or user doesn't have access."""

    pass


class SubjectNotFoundError(ProcessingError):
    """Subject not found."""

    pass


class BodySpecsNotFoundError(ProcessingError):
    """Body specs not found."""

    pass


class AnalysisNotFoundError(ProcessingError):
    """Analysis not found."""

    pass


class AnalysisNotReadyError(ProcessingError):
    """Analysis prerequisites not met (subject/body_specs missing)."""

    pass


class AnalysisAlreadyExistsError(ProcessingError):
    """Analysis already exists for this video."""

    pass


# Error codes for user-facing messages
ERROR_CODES = {
    "POSE_QUALITY_LOW": {
        "message": "Unable to track subject clearly in video",
        "user_action": "Please upload video with better lighting or camera angle",
    },
    "SUBJECT_LOST": {
        "message": "Subject was lost during tracking",
        "user_action": "Please ensure the subject stays visible throughout the video",
    },
    "VIDEO_TOO_DARK": {
        "message": "Video is too dark for accurate analysis",
        "user_action": "Please upload a video with better lighting",
    },
    "PROCESSING_TIMEOUT": {
        "message": "Processing took too long",
        "user_action": "Please try again or upload a shorter video",
    },
}

# Failure threshold for pose estimation
POSE_FAILURE_THRESHOLD = 0.20  # 20%


class ProcessingService:
    """Service for managing the analysis processing pipeline.

    Handles:
    - Starting new analyses
    - Updating processing progress
    - Getting processing status
    - Handling failures
    """

    def __init__(self):
        """Initialize processing service."""
        self.settings = get_settings()
        self.websocket_base_url = os.getenv(
            "WEBSOCKET_BASE_URL", "wss://api.punchanalytics.com"
        )

    async def start_analysis(
        self,
        session: AsyncSession,
        video_id: UUID,
        user_id: UUID,
        subject_id: UUID,
        body_specs_id: UUID,
    ) -> dict:
        """Start analysis pipeline for a video.

        AC-029: Processing progress logged and retrievable via status endpoint

        Args:
            session: Database session
            video_id: Video to analyze
            user_id: User ID for ownership verification
            subject_id: Selected subject ID
            body_specs_id: Body specs ID

        Returns:
            Analysis start response with analysis_id and websocket_url

        Raises:
            VideoNotFoundError: If video doesn't exist or user doesn't own it
            SubjectNotFoundError: If subject doesn't exist or isn't for this video
            BodySpecsNotFoundError: If body specs don't exist
            AnalysisAlreadyExistsError: If analysis already exists for video
        """
        # Verify video ownership
        video = await self._get_video(session, video_id, user_id)

        # Verify subject exists and belongs to video
        subject = await self._get_subject(session, subject_id, video_id)

        # Verify body specs exist
        body_specs = await self._get_body_specs(session, body_specs_id, user_id, video_id)

        # Check for existing analysis
        existing = await self._get_existing_analysis(session, video_id)
        if existing and existing.status not in [AnalysisStatus.FAILED]:
            raise AnalysisAlreadyExistsError(
                f"Analysis already exists for video {video_id}"
            )

        # Delete failed analysis if exists
        if existing and existing.status == AnalysisStatus.FAILED:
            await session.delete(existing)
            await session.flush()

        # Create new analysis
        analysis = Analysis(
            video_id=video_id,
            user_id=user_id,
            subject_id=subject_id,
            body_specs_id=body_specs_id,
            status=AnalysisStatus.QUEUED,
            progress_percent=0,
            total_frames=video.total_frames,
        )
        session.add(analysis)
        await session.flush()
        await session.refresh(analysis)

        logger.info(
            "analysis.started",
            extra={
                "analysis_id": str(analysis.id),
                "video_id": str(video_id),
                "user_id": str(user_id),
            },
        )

        return {
            "analysis_id": str(analysis.id),
            "video_id": str(video_id),
            "status": "queued",
            "estimated_minutes": self._estimate_processing_time(video.total_frames),
            "websocket_url": f"{self.websocket_base_url}/ws/status/{analysis.id}",
        }

    async def get_status(
        self,
        session: AsyncSession,
        analysis_id: UUID,
        user_id: UUID,
    ) -> dict:
        """Get analysis processing status.

        AC-029: Processing progress logged and retrievable via status endpoint

        Args:
            session: Database session
            analysis_id: Analysis ID
            user_id: User ID for ownership verification

        Returns:
            Processing status response

        Raises:
            AnalysisNotFoundError: If analysis doesn't exist or user doesn't own it
        """
        analysis = await self._get_analysis(session, analysis_id, user_id)

        # Build base response
        response = {
            "analysis_id": str(analysis.id),
            "status": analysis.status.value
            if isinstance(analysis.status, AnalysisStatus)
            else analysis.status,
        }

        # Add status-specific fields
        if analysis.status == AnalysisStatus.COMPLETED:
            response.update(
                {
                    "report_id": str(analysis.report_id) if analysis.report_id else None,
                    "completed_at": analysis.completed_at.isoformat()
                    if analysis.completed_at
                    else None,
                    "total_duration_seconds": self._calculate_duration(
                        analysis.queued_at, analysis.completed_at
                    ),
                }
            )

        elif analysis.status == AnalysisStatus.FAILED:
            error_info = ERROR_CODES.get(
                analysis.error_code or "",
                {
                    "message": analysis.error_message or "Unknown error",
                    "user_action": "Please try again or contact support",
                },
            )
            response.update(
                {
                    "failed_stage": analysis.current_stage,
                    "error": {
                        "code": analysis.error_code or "UNKNOWN_ERROR",
                        "message": error_info["message"],
                        "user_action": error_info["user_action"],
                    },
                    "failed_at": analysis.failed_at.isoformat()
                    if analysis.failed_at
                    else None,
                }
            )

        else:
            # In progress
            response.update(
                {
                    "current_stage": analysis.current_stage,
                    "stages": self._build_stages_status(analysis),
                    "estimated_completion": self._estimate_completion(analysis),
                }
            )

        return response

    async def update_progress(
        self,
        session: AsyncSession,
        analysis_id: UUID,
        stage: str,
        progress_percent: int,
        frames_processed: Optional[int] = None,
        frames_failed: Optional[int] = None,
    ) -> dict:
        """Update analysis progress.

        AC-029: Processing progress logged and retrievable via status endpoint

        Args:
            session: Database session
            analysis_id: Analysis ID
            stage: Current processing stage
            progress_percent: Progress percentage (0-100)
            frames_processed: Frames processed so far
            frames_failed: Frames that failed processing

        Returns:
            Updated analysis dict

        Raises:
            AnalysisNotFoundError: If analysis doesn't exist
        """
        result = await session.execute(
            select(Analysis).where(Analysis.id == analysis_id)
        )
        analysis = result.scalar_one_or_none()

        if analysis is None:
            raise AnalysisNotFoundError(f"Analysis not found: {analysis_id}")

        # Update status based on stage
        stage_status_map = {
            "pose_estimation": AnalysisStatus.POSE_ESTIMATION,
            "stamp_generation": AnalysisStatus.STAMP_GENERATION,
            "llm_analysis": AnalysisStatus.LLM_ANALYSIS,
            "report_generation": AnalysisStatus.REPORT_GENERATION,
        }

        new_status = stage_status_map.get(stage, AnalysisStatus.PROCESSING)

        # Update analysis
        analysis.status = new_status
        analysis.current_stage = stage
        analysis.progress_percent = progress_percent

        if frames_processed is not None:
            analysis.frames_processed = frames_processed
        if frames_failed is not None:
            analysis.frames_failed = frames_failed

        # Set stage timestamps
        now = datetime.now(timezone.utc)
        if stage == "pose_estimation" and analysis.pose_started_at is None:
            analysis.pose_started_at = now
            analysis.started_at = analysis.started_at or now
        elif stage == "stamp_generation" and analysis.stamps_started_at is None:
            analysis.stamps_started_at = now
            if analysis.pose_completed_at is None:
                analysis.pose_completed_at = now
        elif stage == "llm_analysis" and analysis.llm_started_at is None:
            analysis.llm_started_at = now
            if analysis.stamps_completed_at is None:
                analysis.stamps_completed_at = now

        await session.flush()

        # Check for failure threshold
        # AC-028: Over 20% frame failure marks analysis as failed with guidance
        if analysis.should_fail_for_quality(POSE_FAILURE_THRESHOLD):
            await self.mark_failed(
                session,
                analysis_id,
                "POSE_QUALITY_LOW",
                f"Frame failure rate exceeded {POSE_FAILURE_THRESHOLD * 100}%",
            )

        logger.info(
            "analysis.progress",
            extra={
                "analysis_id": str(analysis_id),
                "stage": stage,
                "progress_percent": progress_percent,
            },
        )

        return analysis.to_dict()

    async def mark_completed(
        self,
        session: AsyncSession,
        analysis_id: UUID,
        report_id: UUID,
        pose_data_key: Optional[str] = None,
    ) -> dict:
        """Mark analysis as completed.

        Args:
            session: Database session
            analysis_id: Analysis ID
            report_id: Generated report ID
            pose_data_key: S3 key for stored pose data

        Returns:
            Updated analysis dict

        Raises:
            AnalysisNotFoundError: If analysis doesn't exist
        """
        result = await session.execute(
            select(Analysis).where(Analysis.id == analysis_id)
        )
        analysis = result.scalar_one_or_none()

        if analysis is None:
            raise AnalysisNotFoundError(f"Analysis not found: {analysis_id}")

        now = datetime.now(timezone.utc)

        analysis.status = AnalysisStatus.COMPLETED
        analysis.completed_at = now
        analysis.report_id = report_id
        analysis.pose_data_key = pose_data_key
        analysis.progress_percent = 100

        # Set any missing timestamps
        analysis.llm_completed_at = analysis.llm_completed_at or now

        await session.flush()

        logger.info(
            "analysis.completed",
            extra={
                "analysis_id": str(analysis_id),
                "report_id": str(report_id),
                "duration_seconds": self._calculate_duration(
                    analysis.queued_at, now
                ),
            },
        )

        return analysis.to_dict()

    async def mark_failed(
        self,
        session: AsyncSession,
        analysis_id: UUID,
        error_code: str,
        error_message: str,
    ) -> dict:
        """Mark analysis as failed.

        AC-028: Over 20% frame failure marks analysis as failed with guidance

        Args:
            session: Database session
            analysis_id: Analysis ID
            error_code: Error code for categorization
            error_message: Detailed error message

        Returns:
            Updated analysis dict

        Raises:
            AnalysisNotFoundError: If analysis doesn't exist
        """
        result = await session.execute(
            select(Analysis).where(Analysis.id == analysis_id)
        )
        analysis = result.scalar_one_or_none()

        if analysis is None:
            raise AnalysisNotFoundError(f"Analysis not found: {analysis_id}")

        analysis.status = AnalysisStatus.FAILED
        analysis.failed_at = datetime.now(timezone.utc)
        analysis.error_code = error_code
        analysis.error_message = error_message

        await session.flush()

        logger.error(
            "analysis.failed",
            extra={
                "analysis_id": str(analysis_id),
                "error_code": error_code,
                "error_message": error_message,
                "stage": analysis.current_stage,
            },
        )

        return analysis.to_dict()

    # --- Private Helper Methods ---

    async def _get_video(
        self,
        session: AsyncSession,
        video_id: UUID,
        user_id: UUID,
    ) -> Video:
        """Get video with ownership verification."""
        result = await session.execute(select(Video).where(Video.id == video_id))
        video = result.scalar_one_or_none()

        if video is None or video.user_id != user_id:
            raise VideoNotFoundError(f"Video not found: {video_id}")

        return video

    async def _get_subject(
        self,
        session: AsyncSession,
        subject_id: UUID,
        video_id: UUID,
    ) -> Subject:
        """Get subject with video validation."""
        result = await session.execute(
            select(Subject).where(Subject.id == subject_id)
        )
        subject = result.scalar_one_or_none()

        if subject is None or subject.video_id != video_id:
            raise SubjectNotFoundError(f"Subject not found: {subject_id}")

        return subject

    async def _get_body_specs(
        self,
        session: AsyncSession,
        body_specs_id: UUID,
        user_id: UUID,
        video_id: UUID,
    ) -> BodySpecs:
        """Get body specs with ownership verification."""
        result = await session.execute(
            select(BodySpecs).where(BodySpecs.id == body_specs_id)
        )
        body_specs = result.scalar_one_or_none()

        if body_specs is None:
            raise BodySpecsNotFoundError(f"Body specs not found: {body_specs_id}")

        # Verify ownership
        if body_specs.user_id != user_id or body_specs.video_id != video_id:
            raise BodySpecsNotFoundError(f"Body specs not found: {body_specs_id}")

        return body_specs

    async def _get_existing_analysis(
        self,
        session: AsyncSession,
        video_id: UUID,
    ) -> Optional[Analysis]:
        """Get existing analysis for video."""
        result = await session.execute(
            select(Analysis).where(Analysis.video_id == video_id)
        )
        return result.scalar_one_or_none()

    async def _get_analysis(
        self,
        session: AsyncSession,
        analysis_id: UUID,
        user_id: UUID,
    ) -> Analysis:
        """Get analysis with ownership verification."""
        result = await session.execute(
            select(Analysis).where(Analysis.id == analysis_id)
        )
        analysis = result.scalar_one_or_none()

        if analysis is None or analysis.user_id != user_id:
            raise AnalysisNotFoundError(f"Analysis not found: {analysis_id}")

        return analysis

    def _estimate_processing_time(self, total_frames: Optional[int]) -> int:
        """Estimate processing time in minutes."""
        if not total_frames:
            return 3  # Default estimate

        # Rough estimate: ~1000 frames per minute
        minutes = max(1, min(10, total_frames // 1000 + 1))
        return minutes

    def _calculate_duration(
        self,
        start: Optional[datetime],
        end: Optional[datetime],
    ) -> Optional[int]:
        """Calculate duration in seconds."""
        if not start or not end:
            return None
        return int((end - start).total_seconds())

    def _build_stages_status(self, analysis: Analysis) -> list[dict]:
        """Build stages status list for response."""
        stages = []

        # Pose estimation stage
        pose_status = "pending"
        if analysis.pose_started_at:
            if analysis.pose_completed_at:
                pose_status = "completed"
            elif analysis.current_stage == "pose_estimation":
                pose_status = "processing"

        stages.append(
            {
                "name": "pose_estimation",
                "status": pose_status,
                "started_at": analysis.pose_started_at.isoformat()
                if analysis.pose_started_at
                else None,
                "completed_at": analysis.pose_completed_at.isoformat()
                if analysis.pose_completed_at
                else None,
                "progress_percent": analysis.progress_percent
                if pose_status == "processing"
                else None,
                "frames_processed": analysis.frames_processed,
                "total_frames": analysis.total_frames,
            }
        )

        # Stamp generation stage
        stamps_status = "pending"
        if analysis.stamps_started_at:
            if analysis.stamps_completed_at:
                stamps_status = "completed"
            elif analysis.current_stage == "stamp_generation":
                stamps_status = "processing"

        stages.append(
            {
                "name": "stamp_generation",
                "status": stamps_status,
                "started_at": analysis.stamps_started_at.isoformat()
                if analysis.stamps_started_at
                else None,
                "completed_at": analysis.stamps_completed_at.isoformat()
                if analysis.stamps_completed_at
                else None,
            }
        )

        # LLM analysis stage
        llm_status = "pending"
        if analysis.llm_started_at:
            if analysis.llm_completed_at:
                llm_status = "completed"
            elif analysis.current_stage == "llm_analysis":
                llm_status = "processing"

        stages.append(
            {
                "name": "llm_analysis",
                "status": llm_status,
                "started_at": analysis.llm_started_at.isoformat()
                if analysis.llm_started_at
                else None,
                "completed_at": analysis.llm_completed_at.isoformat()
                if analysis.llm_completed_at
                else None,
            }
        )

        return stages

    def _estimate_completion(self, analysis: Analysis) -> Optional[str]:
        """Estimate completion time."""
        if not analysis.started_at or not analysis.total_frames:
            return None

        # Estimate based on current progress
        if analysis.progress_percent > 0:
            elapsed = (datetime.now(timezone.utc) - analysis.started_at).total_seconds()
            estimated_total = elapsed / (analysis.progress_percent / 100)
            remaining = estimated_total - elapsed
            completion = datetime.now(timezone.utc).replace(
                microsecond=0
            ) + __import__("datetime").timedelta(seconds=int(remaining))
            return completion.isoformat()

        return None


# Singleton instance
processing_service = ProcessingService()
