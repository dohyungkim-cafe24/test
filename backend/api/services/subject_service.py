"""Subject selection service for handling thumbnail and subject operations.

@feature F003 - Subject Selection

Implements:
- AC-013: Thumbnail grid displays after upload completes
- AC-014: Tap on person highlights with selection indicator
- AC-015: Confirm selection stores bounding box for tracking
- AC-016: Selection can be changed before confirmation
- AC-017: Single person auto-selected with confirm option
"""
import os
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import get_settings
from api.models.subject import Subject, Thumbnail
from api.models.upload import Video


class SubjectError(Exception):
    """Base exception for subject selection errors."""

    pass


class VideoNotFoundError(SubjectError):
    """Video not found or user doesn't have access."""

    pass


class ThumbnailNotFoundError(SubjectError):
    """Thumbnail not found."""

    pass


class PersonNotFoundError(SubjectError):
    """Person ID not found in thumbnail's detected persons."""

    pass


class SubjectService:
    """Service for managing subject selection."""

    def __init__(self):
        """Initialize subject service."""
        self.settings = get_settings()
        # Base URL for generating thumbnail URLs
        self.storage_base_url = os.getenv(
            "STORAGE_BASE_URL", "https://storage.example.com"
        )

    async def get_thumbnails(
        self,
        session: AsyncSession,
        video_id: UUID,
        user_id: UUID,
    ) -> dict:
        """Get thumbnails for a video.

        AC-013: Thumbnail grid displays after upload completes
        AC-017: Single person auto-selected with confirm option

        Args:
            session: Database session
            video_id: Video ID to get thumbnails for
            user_id: User ID for ownership verification

        Returns:
            Thumbnails response with status, frames, and detected persons

        Raises:
            VideoNotFoundError: If video doesn't exist or user doesn't own it
        """
        video = await self._get_video(session, video_id, user_id)

        # Check processing status
        if video.upload_status == "processing_thumbnails":
            return {
                "video_id": str(video_id),
                "status": "processing",
                "total_persons_detected": 0,
                "thumbnails": [],
                "auto_select": None,
                "message": "Extracting frames...",
            }

        if video.upload_status == "failed":
            return {
                "video_id": str(video_id),
                "status": "failed",
                "total_persons_detected": 0,
                "thumbnails": [],
                "auto_select": None,
                "message": "Failed to process video. Please try uploading again.",
            }

        # Get thumbnails
        thumbnails = await self._get_thumbnails(session, video_id)

        # Build response
        thumbnail_responses = []
        all_person_ids: set[str] = set()

        for thumb in thumbnails:
            detected = thumb.detected_persons or []

            # Track unique persons across all thumbnails
            for person in detected:
                all_person_ids.add(person.get("person_id", ""))

            thumbnail_responses.append(
                {
                    "thumbnail_id": str(thumb.id),
                    "frame_number": thumb.frame_number,
                    "timestamp_seconds": thumb.timestamp_seconds,
                    "image_url": await self._get_image_url(thumb.storage_key),
                    "detected_persons": [
                        {
                            "person_id": p.get("person_id"),
                            "bounding_box": p.get("bounding_box"),
                            "confidence": p.get("confidence"),
                        }
                        for p in detected
                    ],
                }
            )

        total_persons = len(all_person_ids)

        # Determine status and message
        if total_persons == 0:
            return {
                "video_id": str(video_id),
                "status": "no_subjects",
                "total_persons_detected": 0,
                "thumbnails": thumbnail_responses,
                "auto_select": None,
                "message": "We couldn't identify any people in your video. Please upload a video with clear visibility.",
            }

        # AC-017: Single person auto-selected
        if total_persons == 1:
            # Find the first thumbnail with the person
            first_person_id = next(iter(all_person_ids))
            auto_select_info = None

            for thumb_resp in thumbnail_responses:
                for person in thumb_resp["detected_persons"]:
                    if person["person_id"] == first_person_id:
                        auto_select_info = {
                            "thumbnail_id": thumb_resp["thumbnail_id"],
                            "person_id": first_person_id,
                            "bounding_box": person["bounding_box"],
                        }
                        break
                if auto_select_info:
                    break

            return {
                "video_id": str(video_id),
                "status": "ready",
                "total_persons_detected": 1,
                "thumbnails": thumbnail_responses,
                "auto_select": auto_select_info,
                "message": "We detected one person. Is this you?",
            }

        # Multiple persons detected
        return {
            "video_id": str(video_id),
            "status": "ready",
            "total_persons_detected": total_persons,
            "thumbnails": thumbnail_responses,
            "auto_select": None,
            "message": None,
        }

    async def select_subject(
        self,
        session: AsyncSession,
        video_id: UUID,
        user_id: UUID,
        thumbnail_id: UUID,
        person_id: str,
    ) -> dict:
        """Select analysis subject from a thumbnail.

        AC-015: Confirm selection stores bounding box for tracking
        AC-016: Selection can be changed before confirmation

        Args:
            session: Database session
            video_id: Video ID
            user_id: User ID for ownership verification
            thumbnail_id: Thumbnail where selection was made
            person_id: ID of selected person

        Returns:
            Subject selection response with bounding box

        Raises:
            VideoNotFoundError: If video doesn't exist or user doesn't own it
            ThumbnailNotFoundError: If thumbnail doesn't exist
            PersonNotFoundError: If person_id not found in thumbnail
        """
        # Verify video ownership
        video = await self._get_video(session, video_id, user_id)

        # Get thumbnail
        thumbnail = await self._get_thumbnail(session, thumbnail_id, video_id)

        # Find person in detected_persons
        detected = thumbnail.detected_persons or []
        selected_person = None
        for person in detected:
            if person.get("person_id") == person_id:
                selected_person = person
                break

        if selected_person is None:
            raise PersonNotFoundError(
                f"Person {person_id} not found in thumbnail {thumbnail_id}"
            )

        bounding_box = selected_person.get("bounding_box", {})

        # Check for existing subject (AC-016: can change selection)
        existing_subject = await self._get_existing_subject(session, video_id)

        if existing_subject:
            # Update existing subject
            existing_subject.thumbnail_id = thumbnail_id
            existing_subject.person_id = person_id
            existing_subject.initial_bbox = bounding_box
            await session.flush()

            return {
                "subject_id": str(existing_subject.id),
                "video_id": str(video_id),
                "person_id": person_id,
                "bounding_box": bounding_box,
                "auto_selected": False,
            }

        # Create new subject
        subject = Subject(
            video_id=video_id,
            thumbnail_id=thumbnail_id,
            person_id=person_id,
            initial_bbox=bounding_box,
        )
        session.add(subject)
        await session.flush()
        await session.refresh(subject)

        return {
            "subject_id": str(subject.id),
            "video_id": str(video_id),
            "person_id": person_id,
            "bounding_box": bounding_box,
            "auto_selected": False,
        }

    async def _get_video(
        self,
        session: AsyncSession,
        video_id: UUID,
        user_id: UUID,
    ) -> Video:
        """Get video by ID with ownership verification.

        Args:
            session: Database session
            video_id: Video ID
            user_id: User ID for ownership verification

        Returns:
            Video model

        Raises:
            VideoNotFoundError: If video doesn't exist or user doesn't own it
        """
        result = await session.execute(
            select(Video).where(Video.id == video_id)
        )
        video = result.scalar_one_or_none()

        if video is None:
            raise VideoNotFoundError(f"Video not found: {video_id}")

        # Verify ownership - same error to prevent enumeration
        if video.user_id != user_id:
            raise VideoNotFoundError(f"Video not found: {video_id}")

        return video

    async def _get_thumbnails(
        self,
        session: AsyncSession,
        video_id: UUID,
    ) -> list[Thumbnail]:
        """Get all thumbnails for a video.

        Args:
            session: Database session
            video_id: Video ID

        Returns:
            List of thumbnails ordered by timestamp
        """
        result = await session.execute(
            select(Thumbnail)
            .where(Thumbnail.video_id == video_id)
            .order_by(Thumbnail.timestamp_seconds)
        )
        return list(result.scalars().all())

    async def _get_thumbnail(
        self,
        session: AsyncSession,
        thumbnail_id: UUID,
        video_id: UUID,
    ) -> Thumbnail:
        """Get thumbnail by ID.

        Args:
            session: Database session
            thumbnail_id: Thumbnail ID
            video_id: Video ID for validation

        Returns:
            Thumbnail model

        Raises:
            ThumbnailNotFoundError: If thumbnail doesn't exist
        """
        result = await session.execute(
            select(Thumbnail).where(
                Thumbnail.id == thumbnail_id, Thumbnail.video_id == video_id
            )
        )
        thumbnail = result.scalar_one_or_none()

        if thumbnail is None:
            raise ThumbnailNotFoundError(f"Thumbnail not found: {thumbnail_id}")

        return thumbnail

    async def _get_existing_subject(
        self,
        session: AsyncSession,
        video_id: UUID,
    ) -> Optional[Subject]:
        """Get existing subject for a video.

        Args:
            session: Database session
            video_id: Video ID

        Returns:
            Subject model or None
        """
        result = await session.execute(
            select(Subject).where(Subject.video_id == video_id)
        )
        return result.scalar_one_or_none()

    async def _get_image_url(self, storage_key: str) -> str:
        """Generate public URL for a storage key.

        Args:
            storage_key: S3/storage key

        Returns:
            Public URL for the image
        """
        # In production, this would generate a signed URL or CDN URL
        return f"{self.storage_base_url}/{storage_key}"


# Singleton instance
subject_service = SubjectService()
