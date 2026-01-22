"""Stamp generation service for orchestrating action detection and storage.

@feature F006 - Stamp Generation

Implements:
- AC-030: Strikes detected by arm velocity and trajectory patterns
- AC-031: Defensive actions detected by torso and arm positioning
- AC-032: Each action timestamped with frame number and confidence
- AC-033: Stamps stored with type, timestamp, side, and confidence
- AC-034: No actions detected proceeds with generic feedback

This service coordinates detection algorithms and database storage.
"""
import logging
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.stamp import ActionType, Side, Stamp
from api.schemas.stamp import StampCreate, StampSummary
from api.services.stamp_detection_service import stamp_detection_service

logger = logging.getLogger(__name__)


class StampGenerationError(Exception):
    """Base exception for stamp generation errors."""

    pass


class StampGenerationService:
    """Service for generating stamps from pose data.

    AC-032: Each action timestamped with frame number and confidence
    AC-033: Stamps stored with type, timestamp, side, and confidence
    AC-034: No actions detected proceeds with generic feedback

    Orchestrates the detection of strikes and defensive actions,
    then stores the results in the database.
    """

    def __init__(self):
        """Initialize stamp generation service."""
        self.detection_service = stamp_detection_service

    def detect_all_actions(self, pose_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Detect all actions (strikes and defense) from pose data.

        AC-030: Strikes detected by arm velocity and trajectory patterns
        AC-031: Defensive actions detected by torso and arm positioning
        AC-034: No actions detected proceeds with generic feedback

        Args:
            pose_data: Pose data with frames and fps

        Returns:
            List of detected action stamps (may be empty for AC-034)
        """
        all_stamps = []

        # Detect strikes
        strikes = self.detection_service.detect_strikes(pose_data)
        all_stamps.extend(strikes)

        # Detect defensive actions
        defense = self.detection_service.detect_defense(pose_data)
        all_stamps.extend(defense)

        # Sort by timestamp
        all_stamps.sort(key=lambda s: s["timestamp_seconds"])

        logger.info(
            "stamp_detection.complete",
            extra={
                "total_stamps": len(all_stamps),
                "strikes_count": len(strikes),
                "defense_count": len(defense),
            },
        )

        return all_stamps

    async def generate_stamps(
        self,
        session: AsyncSession,
        analysis_id: UUID,
        pose_data: dict[str, Any],
    ) -> list[Stamp]:
        """Generate and store stamps for an analysis.

        AC-032: Each action timestamped with frame number and confidence
        AC-033: Stamps stored with type, timestamp, side, and confidence
        AC-034: No actions detected proceeds with generic feedback

        Args:
            session: Database session
            analysis_id: Analysis ID
            pose_data: Pose data with frames and fps

        Returns:
            List of created Stamp models
        """
        # Detect all actions
        detected_stamps = self.detect_all_actions(pose_data)

        # AC-034: No actions is valid - proceed with empty list
        if not detected_stamps:
            logger.info(
                "stamp_generation.no_actions",
                extra={
                    "analysis_id": str(analysis_id),
                    "message": "No significant actions detected",
                },
            )
            return []

        # Create stamp records
        stamps = []
        for stamp_data in detected_stamps:
            stamp = Stamp(
                analysis_id=analysis_id,
                timestamp_seconds=stamp_data["timestamp_seconds"],
                frame_number=stamp_data["frame_number"],
                action_type=stamp_data["action_type"],
                side=stamp_data["side"],
                confidence=stamp_data["confidence"],
                velocity_vector=stamp_data.get("velocity_vector"),
                trajectory_data=stamp_data.get("trajectory_data"),
            )
            session.add(stamp)
            stamps.append(stamp)

        await session.flush()

        logger.info(
            "stamp_generation.complete",
            extra={
                "analysis_id": str(analysis_id),
                "stamps_created": len(stamps),
            },
        )

        return stamps

    async def get_stamps_for_analysis(
        self,
        session: AsyncSession,
        analysis_id: UUID,
    ) -> list[Stamp]:
        """Get all stamps for an analysis.

        Args:
            session: Database session
            analysis_id: Analysis ID

        Returns:
            List of Stamp models ordered by timestamp
        """
        result = await session.execute(
            select(Stamp)
            .where(Stamp.analysis_id == analysis_id)
            .order_by(Stamp.timestamp_seconds)
        )
        return list(result.scalars().all())

    async def get_stamp_summary(
        self,
        session: AsyncSession,
        analysis_id: UUID,
    ) -> StampSummary:
        """Get summary statistics for stamps.

        Args:
            session: Database session
            analysis_id: Analysis ID

        Returns:
            StampSummary with counts and statistics
        """
        stamps = await self.get_stamps_for_analysis(session, analysis_id)

        # Calculate counts by type
        strike_counts = {
            "jab": 0,
            "straight": 0,
            "hook": 0,
            "uppercut": 0,
        }
        defense_counts = {
            "guard_up": 0,
            "guard_down": 0,
            "slip": 0,
            "duck": 0,
            "bob_weave": 0,
        }

        total_confidence = 0.0
        for stamp in stamps:
            action_type = stamp._action_type
            if action_type in strike_counts:
                strike_counts[action_type] += 1
            elif action_type in defense_counts:
                defense_counts[action_type] += 1
            total_confidence += stamp.confidence

        avg_confidence = total_confidence / len(stamps) if stamps else 0.0

        return StampSummary(
            total_stamps=len(stamps),
            strikes=strike_counts,
            defense=defense_counts,
            avg_confidence=round(avg_confidence, 2),
            no_actions_detected=len(stamps) == 0,
        )

    async def delete_stamps_for_analysis(
        self,
        session: AsyncSession,
        analysis_id: UUID,
    ) -> int:
        """Delete all stamps for an analysis.

        Used when reprocessing an analysis.

        Args:
            session: Database session
            analysis_id: Analysis ID

        Returns:
            Number of stamps deleted
        """
        result = await session.execute(
            select(Stamp).where(Stamp.analysis_id == analysis_id)
        )
        stamps = list(result.scalars().all())
        count = len(stamps)

        for stamp in stamps:
            await session.delete(stamp)

        await session.flush()

        logger.info(
            "stamp_generation.deleted",
            extra={
                "analysis_id": str(analysis_id),
                "stamps_deleted": count,
            },
        )

        return count


# Singleton instance
stamp_generation_service = StampGenerationService()
