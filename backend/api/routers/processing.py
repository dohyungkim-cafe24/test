"""Processing router for analysis pipeline endpoints.

@feature F005 - Pose Estimation Processing

Implements:
- POST /api/v1/analysis/start/{video_id} - Start analysis
- POST /api/v1/analysis/run/{video_id} - Run analysis synchronously (free tier)
- GET /api/v1/processing/status/{analysis_id} - Get status

Acceptance Criteria:
- AC-029: Processing progress logged and retrievable via status endpoint
"""
import logging
from datetime import datetime, timezone
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel
from sqlalchemy import select

from api.routers.auth import get_current_user_or_guest
from api.schemas.analysis import (
    ProcessingStatusResponse,
    StartAnalysisRequest,
    StartAnalysisResponse,
)
from api.services.database import get_db_session
from api.services.processing_service import (
    AnalysisAlreadyExistsError,
    AnalysisNotFoundError,
    BodySpecsNotFoundError,
    SubjectNotFoundError,
    VideoNotFoundError,
    processing_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["processing"])


@router.post(
    "/analysis/start/{video_id}",
    response_model=StartAnalysisResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Video, subject, or body specs not found"},
        409: {"description": "Analysis already exists for this video"},
    },
)
async def start_analysis(
    video_id: Annotated[UUID, Path(description="Video ID to analyze")],
    request: StartAnalysisRequest,
    current_user: Annotated[dict, Depends(get_current_user_or_guest)],
):
    """Start analysis pipeline for a video.

    Requires:
    - Valid video owned by current user
    - Subject selected for the video
    - Body specs submitted for the video

    Returns:
    - analysis_id: Unique identifier for tracking
    - websocket_url: URL for real-time status updates
    - estimated_minutes: Estimated processing time

    AC-029: Processing progress logged and retrievable via status endpoint
    """
    user_id = UUID(current_user["id"])

    try:
        subject_id = UUID(request.subject_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid subject_id format",
        )

    try:
        body_specs_id = UUID(request.body_specs_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid body_specs_id format",
        )

    try:
        async with get_db_session() as session:
            result = await processing_service.start_analysis(
                session=session,
                video_id=video_id,
                user_id=user_id,
                subject_id=subject_id,
                body_specs_id=body_specs_id,
            )
        return StartAnalysisResponse(**result)

    except VideoNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    except SubjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found for this video",
        )
    except BodySpecsNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Body specs not found for this video",
        )
    except AnalysisAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Analysis already exists for this video",
        )


@router.get(
    "/processing/status/{analysis_id}",
    response_model=ProcessingStatusResponse,
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Analysis not found"},
    },
)
async def get_processing_status(
    analysis_id: Annotated[UUID, Path(description="Analysis ID")],
    current_user: Annotated[dict, Depends(get_current_user_or_guest)],
):
    """Get current processing status for an analysis.

    Returns detailed status including:
    - Overall status (queued, processing, completed, failed)
    - Current processing stage
    - Progress percentage for each stage
    - Estimated completion time
    - Error details if failed

    AC-029: Processing progress logged and retrievable via status endpoint
    """
    user_id = UUID(current_user["id"])

    try:
        async with get_db_session() as session:
            result = await processing_service.get_status(
                session=session,
                analysis_id=analysis_id,
                user_id=user_id,
            )
        return ProcessingStatusResponse(**result)

    except AnalysisNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )


# --- Synchronous Analysis (Free Tier) ---


class RunAnalysisResponse(BaseModel):
    """Response for synchronous analysis."""
    report_id: str
    video_id: str
    performance_score: int
    message: str


@router.post(
    "/analysis/run/{video_id}",
    response_model=RunAnalysisResponse,
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Video not found"},
        500: {"description": "Analysis failed"},
    },
)
async def run_analysis_sync(
    video_id: Annotated[UUID, Path(description="Video ID to analyze")],
    current_user: Annotated[dict, Depends(get_current_user_or_guest)],
):
    """Run analysis synchronously (for free tier without background jobs).

    This endpoint:
    1. Extracts frames from the video
    2. Runs MediaPipe pose estimation
    3. Calls GPT for boxing analysis
    4. Creates and returns a report

    Note: This may take 30-60 seconds depending on video length.
    """
    from api.models.analysis import Analysis, AnalysisStatus
    from api.models.body_specs import BodySpecs
    from api.models.report import Report
    from api.models.subject import Subject, Thumbnail
    from api.models.upload import Video
    from api.services.video_processor import video_processor, VideoProcessingError
    from api.services.gpt_analyzer import gpt_analyzer

    user_id = UUID(current_user["id"])

    try:
        async with get_db_session() as session:
            # Get video
            result = await session.execute(
                select(Video).where(Video.id == video_id, Video.user_id == user_id)
            )
            video = result.scalar_one_or_none()

            if not video:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Video not found",
                )

            # Get body specs (most recent for this user)
            result = await session.execute(
                select(BodySpecs)
                .where(BodySpecs.user_id == user_id)
                .order_by(BodySpecs.created_at.desc())
                .limit(1)
            )
            body_specs = result.scalar_one_or_none()

            if not body_specs:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Body specs required before analysis",
                )

            body_specs_dict = {
                "height_cm": body_specs.height_cm,
                "weight_kg": body_specs.weight_kg,
                "experience_level": body_specs.experience_level,
                "stance": body_specs.stance,
            }

            # Step 1: Process video (frame extraction + pose estimation)
            logger.info(f"Starting video processing for {video_id}")
            pose_data = await video_processor.process_video(session, video_id, user_id)

            # Step 2: GPT analysis
            logger.info(f"Starting GPT analysis for {video_id}")
            analysis_result = await gpt_analyzer.analyze_boxing_session(
                pose_data, body_specs_dict
            )

            # Step 3: Create necessary records for foreign key constraints
            # Create synthetic Thumbnail (for free tier - skipped subject selection)
            thumbnail = Thumbnail(
                video_id=video_id,
                frame_number=0,
                timestamp_seconds=0.0,
                storage_key=f"synthetic/{video_id}/thumbnail_0.jpg",
                detected_persons=[{"person_id": "person_0", "confidence": 1.0, "bounding_box": {"x": 0, "y": 0, "width": 100, "height": 100}}],
            )
            session.add(thumbnail)
            await session.flush()

            # Create synthetic Subject
            subject = Subject(
                video_id=video_id,
                thumbnail_id=thumbnail.id,
                person_id="person_0",
                initial_bbox={"x": 0, "y": 0, "width": 100, "height": 100},
            )
            session.add(subject)
            await session.flush()

            # Create Analysis record
            analysis = Analysis(
                video_id=video_id,
                user_id=user_id,
                subject_id=subject.id,
                body_specs_id=body_specs.id,
            )
            analysis.status = AnalysisStatus.COMPLETED
            analysis.progress_percent = 100
            analysis.total_frames = pose_data.get("total_frames_analyzed", 0)
            analysis.frames_processed = pose_data.get("successful_detections", 0)
            session.add(analysis)
            await session.flush()

            # Step 4: Create report
            report = Report(
                analysis_id=analysis.id,
                video_id=video_id,
                user_id=user_id,
                performance_score=analysis_result.get("performance_score", 50),
                overall_assessment=analysis_result.get("overall_assessment", ""),
                strengths=analysis_result.get("strengths", []),
                weaknesses=analysis_result.get("weaknesses", []),
                recommendations=analysis_result.get("recommendations", []),
                metrics=pose_data.get("aggregated_metrics", {}),
                llm_model=analysis_result.get("llm_model"),
                prompt_tokens=analysis_result.get("prompt_tokens"),
                completion_tokens=analysis_result.get("completion_tokens"),
            )
            session.add(report)
            await session.flush()
            await session.refresh(report)

            logger.info(f"Analysis complete for {video_id}, report_id={report.id}")

            return RunAnalysisResponse(
                report_id=str(report.id),
                video_id=str(video_id),
                performance_score=report.performance_score or 50,
                message="Analysis complete! View your report.",
            )

    except VideoProcessingError as e:
        logger.error(f"Video processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video processing failed: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )
