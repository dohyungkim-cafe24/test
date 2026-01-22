"""Body specifications service for handling body spec operations.

@feature F004 - Body Specification Input

Implements:
- AC-018: Form with height, weight, experience level, stance
- AC-019: Validation: height (100-250cm), weight (30-200kg)
- AC-024: Body specs pre-filled for returning users
"""
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.body_specs import BodySpecs
from api.models.upload import Video
from api.models.user import User


class BodySpecsError(Exception):
    """Base exception for body specs errors."""
    pass


class VideoNotFoundError(BodySpecsError):
    """Video not found or user doesn't have access."""
    pass


class UserNotFoundError(BodySpecsError):
    """User not found."""
    pass


class BodySpecsService:
    """Service for managing body specifications."""

    def __init__(self):
        """Initialize body specs service."""
        pass

    async def create_body_specs(
        self,
        session: AsyncSession,
        user_id: UUID,
        video_id: UUID,
        height_cm: int,
        weight_kg: int,
        experience_level: str,
        stance: str,
    ) -> dict:
        """Create body specifications for a video.

        AC-018: Form with height, weight, experience level, stance
        AC-024: Persists to user profile for future pre-fill

        Args:
            session: Database session
            user_id: User ID for ownership verification
            video_id: Video ID to associate specs with
            height_cm: Height in centimeters (100-250)
            weight_kg: Weight in kilograms (30-200)
            experience_level: beginner|intermediate|advanced|competitive
            stance: orthodox|southpaw

        Returns:
            Body specs response with video_id, body_specs_id, saved, persist_to_profile

        Raises:
            VideoNotFoundError: If video doesn't exist or user doesn't own it
        """
        # Verify video ownership (IDOR prevention)
        video = await self._get_video(session, video_id, user_id)

        # Get user for profile update
        user = await self._get_user(session, user_id)

        # Check for existing body specs for this video
        existing_specs = await self._get_existing_specs(session, video_id)

        if existing_specs:
            # Update existing specs
            existing_specs.height_cm = height_cm
            existing_specs.weight_kg = weight_kg
            existing_specs.experience_level = experience_level
            existing_specs.stance = stance
            await session.flush()

            body_specs_id = str(existing_specs.id)
        else:
            # Create new body specs record
            body_specs = BodySpecs(
                user_id=user_id,
                video_id=video_id,
                height_cm=height_cm,
                weight_kg=weight_kg,
                experience_level=experience_level,
                stance=stance,
            )
            session.add(body_specs)
            await session.flush()
            await session.refresh(body_specs)

            body_specs_id = str(body_specs.id)

        # Persist to user profile (AC-024)
        user.height_cm = height_cm
        user.weight_kg = weight_kg
        user.experience_level = experience_level
        user.stance = stance

        return {
            "video_id": str(video_id),
            "body_specs_id": body_specs_id,
            "saved": True,
            "persist_to_profile": True,
        }

    async def get_prefill(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> dict:
        """Get user's saved body specs for pre-filling form.

        AC-024: Body specs pre-filled for returning users

        Args:
            session: Database session
            user_id: User ID

        Returns:
            Prefill response with has_saved_specs and spec values
        """
        user = await self._get_user(session, user_id)

        has_specs = any([
            user.height_cm,
            user.weight_kg,
            user.experience_level,
            user.stance,
        ])

        return {
            "has_saved_specs": has_specs,
            "height_cm": user.height_cm,
            "weight_kg": user.weight_kg,
            "experience_level": user.experience_level,
            "stance": user.stance,
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

    async def _get_user(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> User:
        """Get user by ID.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            User model

        Raises:
            UserNotFoundError: If user doesn't exist
        """
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            raise UserNotFoundError(f"User not found: {user_id}")

        return user

    async def _get_existing_specs(
        self,
        session: AsyncSession,
        video_id: UUID,
    ) -> Optional[BodySpecs]:
        """Get existing body specs for a video.

        Args:
            session: Database session
            video_id: Video ID

        Returns:
            BodySpecs model or None
        """
        result = await session.execute(
            select(BodySpecs).where(BodySpecs.video_id == video_id)
        )
        return result.scalar_one_or_none()


# Singleton instance
body_specs_service = BodySpecsService()
