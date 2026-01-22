"""Report service for retrieving analysis reports.

@feature F008 - Report Display

Implements:
- AC-041: Summary section displays overall assessment
- AC-042: Strengths section shows 3-5 observations
- AC-043: Weaknesses section shows 3-5 improvement areas
- AC-044: Recommendations section shows 3-5 actionable items
- AC-045: Key moments section with timestamp links
- AC-046: Metrics displayed with visual indicators
"""
import logging
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.report import Report
from api.models.stamp import Stamp
from api.models.analysis import Analysis

logger = logging.getLogger(__name__)


class ReportServiceError(Exception):
    """Base exception for report service errors."""

    pass


class ReportNotFoundError(ReportServiceError):
    """Report not found in database."""

    pass


class ReportOwnershipError(ReportServiceError):
    """User not authorized to access report."""

    pass


class ReportService:
    """Service for managing analysis reports.

    Provides report retrieval with ownership validation
    and full data aggregation (report + stamps + metrics).
    """

    async def get_report(
        self,
        session: AsyncSession,
        report_id: UUID,
        user_id: UUID,
    ) -> dict[str, Any]:
        """Get a complete report with all sections.

        AC-041: Summary section displays overall assessment
        AC-042: Strengths section shows 3-5 observations
        AC-043: Weaknesses section shows 3-5 improvement areas
        AC-044: Recommendations section shows 3-5 actionable items
        AC-045: Key moments section with timestamp links
        AC-046: Metrics displayed with visual indicators

        Args:
            session: Database session
            report_id: Report UUID to retrieve
            user_id: ID of user making the request

        Returns:
            Complete report data with all sections

        Raises:
            ReportNotFoundError: If report doesn't exist
            ReportOwnershipError: If user doesn't own the report
        """
        # Get report
        report = await self._get_report_by_id(session, report_id)
        if report is None:
            logger.warning(
                "report.not_found",
                extra={"report_id": str(report_id)},
            )
            raise ReportNotFoundError(f"Report {report_id} not found")

        # Validate ownership
        if report.user_id != user_id:
            logger.warning(
                "report.ownership_denied",
                extra={
                    "report_id": str(report_id),
                    "owner_id": str(report.user_id),
                    "requester_id": str(user_id),
                },
            )
            raise ReportOwnershipError("Not authorized to access this report")

        # Get stamps (key moments) for the analysis - AC-045
        stamps = await self._get_stamps_for_analysis(session, report.analysis_id)

        # Build response
        result = {
            "id": str(report.id),
            "analysis_id": str(report.analysis_id),
            "video_id": str(report.video_id),
            "user_id": str(report.user_id),
            "performance_score": report.performance_score,  # AC-041
            "overall_assessment": report.overall_assessment,  # AC-041
            "strengths": report.strengths,  # AC-042
            "weaknesses": report.weaknesses,  # AC-043
            "recommendations": report.recommendations,  # AC-044
            "metrics": report.metrics,  # AC-046
            "llm_model": report.llm_model,
            "disclaimer": report.disclaimer,  # Required by product
            "created_at": report.created_at.isoformat() if report.created_at else None,
            "updated_at": report.updated_at.isoformat() if report.updated_at else None,
            "stamps": stamps,  # AC-045
        }

        logger.info(
            "report.retrieved",
            extra={
                "report_id": str(report_id),
                "user_id": str(user_id),
                "stamps_count": len(stamps),
            },
        )

        return result

    async def _get_report_by_id(
        self,
        session: AsyncSession,
        report_id: UUID,
    ) -> Optional[Report]:
        """Get report by ID from database.

        Args:
            session: Database session
            report_id: Report UUID

        Returns:
            Report model or None if not found
        """
        query = select(Report).where(
            Report.id == report_id,
            Report.deleted_at.is_(None),
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def _get_stamps_for_analysis(
        self,
        session: AsyncSession,
        analysis_id: UUID,
    ) -> list[dict[str, Any]]:
        """Get all stamps (key moments) for an analysis.

        AC-045: Key moments section with timestamp links

        Args:
            session: Database session
            analysis_id: Analysis UUID

        Returns:
            List of stamp data with timestamps and action types
        """
        query = (
            select(Stamp)
            .where(Stamp.analysis_id == analysis_id)
            .order_by(Stamp.timestamp_seconds)
        )
        result = await session.execute(query)
        stamps = result.scalars().all()

        return [
            {
                "stamp_id": str(stamp.id),
                "timestamp_seconds": stamp.timestamp_seconds,
                "frame_number": stamp.frame_number,
                "action_type": stamp.action_type,
                "side": stamp.side,
                "confidence": stamp.confidence,
                "thumbnail_key": stamp.thumbnail_key,
            }
            for stamp in stamps
        ]

    async def get_report_by_analysis_id(
        self,
        session: AsyncSession,
        analysis_id: UUID,
        user_id: UUID,
    ) -> dict[str, Any]:
        """Get report by analysis ID.

        Args:
            session: Database session
            analysis_id: Analysis UUID
            user_id: ID of user making the request

        Returns:
            Complete report data

        Raises:
            ReportNotFoundError: If no report exists for this analysis
            ReportOwnershipError: If user doesn't own the report
        """
        query = select(Report).where(
            Report.analysis_id == analysis_id,
            Report.deleted_at.is_(None),
        )
        result = await session.execute(query)
        report = result.scalar_one_or_none()

        if report is None:
            raise ReportNotFoundError(f"No report found for analysis {analysis_id}")

        return await self.get_report(session, report.id, user_id)


# Singleton instance
report_service = ReportService()
