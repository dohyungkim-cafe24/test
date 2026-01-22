"""Dashboard service for user report history management.

@feature F010 - Report History Dashboard

Implements:
- AC-056: Dashboard lists reports sorted by date descending
- AC-057: List items show thumbnail, date, summary indicator
- AC-059: Delete report with undo support

BDD Scenarios:
- Dashboard displays report list sorted by date (newest first)
- Report list item shows thumbnail, date, summary (key moments count)
- User deletes report with confirmation dialog and undo toast (10 seconds)
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.report import Report
from api.models.stamp import Stamp
from api.models.upload import Video

logger = logging.getLogger(__name__)

# Undo window for soft-deleted reports (10 seconds per BDD scenario)
RESTORE_WINDOW_SECONDS = 10


class DashboardServiceError(Exception):
    """Base exception for dashboard service errors."""

    pass


class ReportNotFoundError(DashboardServiceError):
    """Report not found in database."""

    pass


class ReportOwnershipError(DashboardServiceError):
    """User not authorized to access report."""

    pass


class RestoreWindowExpiredError(DashboardServiceError):
    """Restore window has expired for deleted report."""

    pass


class DashboardService:
    """Service for managing user's report history dashboard.

    Provides paginated report listing and soft-delete with undo support.
    """

    async def list_user_reports(
        self,
        session: AsyncSession,
        user_id: UUID,
        page: int = 1,
        limit: int = 10,
    ) -> dict[str, Any]:
        """List user's reports sorted by date descending.

        AC-056: Dashboard lists reports sorted by date descending
        AC-057: List items show thumbnail, date, summary indicator

        Args:
            session: Database session
            user_id: User ID to filter reports
            page: Page number (1-indexed)
            limit: Number of items per page

        Returns:
            Paginated report list with metadata
        """
        offset = (page - 1) * limit

        # Count total reports for user (excluding deleted)
        count_query = (
            select(func.count())
            .select_from(Report)
            .where(
                Report.user_id == user_id,
                Report.deleted_at.is_(None),
            )
        )
        count_result = await session.execute(count_query)
        total = count_result.scalar_one()

        # Get reports with video thumbnail, sorted by created_at DESC
        # AC-056: Sorted by date descending (newest first)
        reports_query = (
            select(Report, Video.thumbnail_key)
            .join(Video, Report.video_id == Video.id)
            .where(
                Report.user_id == user_id,
                Report.deleted_at.is_(None),
            )
            .order_by(Report.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        reports_result = await session.execute(reports_query)
        reports = reports_result.all()

        # Get stamp counts for each report (key_moments_count)
        items = []
        for report, thumbnail_key in reports:
            # Count stamps for this report's analysis
            stamps_count_query = (
                select(func.count())
                .select_from(Stamp)
                .where(Stamp.analysis_id == report.analysis_id)
            )
            stamps_result = await session.execute(stamps_count_query)
            key_moments_count = stamps_result.scalar_one()

            # AC-057: Required fields for display
            items.append({
                "id": str(report.id),
                "video_id": str(report.video_id),
                "thumbnail_url": self._build_thumbnail_url(thumbnail_key),
                "analyzed_at": report.created_at.isoformat(),
                "key_moments_count": key_moments_count,
                "performance_score": report.performance_score,
            })

        has_more = offset + len(items) < total

        logger.info(
            "dashboard.reports_listed",
            extra={
                "user_id": str(user_id),
                "page": page,
                "limit": limit,
                "total": total,
                "returned": len(items),
            },
        )

        return {
            "items": items,
            "total": total,
            "page": page,
            "has_more": has_more,
        }

    async def delete_report(
        self,
        session: AsyncSession,
        report_id: UUID,
        user_id: UUID,
    ) -> dict[str, Any]:
        """Soft-delete a report with undo support.

        AC-059: Delete report shows confirmation dialog
        BDD: Undo toast for 10 seconds

        Args:
            session: Database session
            report_id: Report UUID to delete
            user_id: User ID for ownership validation

        Returns:
            Deletion confirmation with restore window info

        Raises:
            ReportNotFoundError: If report doesn't exist
            ReportOwnershipError: If user doesn't own the report
        """
        report = await self._get_report_by_id(session, report_id)

        if report is None:
            logger.warning(
                "dashboard.delete_not_found",
                extra={"report_id": str(report_id)},
            )
            raise ReportNotFoundError(f"Report {report_id} not found")

        if report.user_id != user_id:
            logger.warning(
                "dashboard.delete_ownership_denied",
                extra={
                    "report_id": str(report_id),
                    "owner_id": str(report.user_id),
                    "requester_id": str(user_id),
                },
            )
            raise ReportOwnershipError("Not authorized to delete this report")

        # Soft delete
        now = datetime.now(timezone.utc)
        report.deleted_at = now
        await session.commit()

        restore_until = now + timedelta(seconds=RESTORE_WINDOW_SECONDS)

        logger.info(
            "dashboard.report_deleted",
            extra={
                "report_id": str(report_id),
                "user_id": str(user_id),
                "restore_until": restore_until.isoformat(),
            },
        )

        return {
            "deleted": True,
            "can_restore_until": restore_until.isoformat(),
        }

    async def restore_report(
        self,
        session: AsyncSession,
        report_id: UUID,
        user_id: UUID,
    ) -> dict[str, Any]:
        """Restore a soft-deleted report (undo delete).

        BDD: User deletes report with undo toast (10 seconds)

        Args:
            session: Database session
            report_id: Report UUID to restore
            user_id: User ID for ownership validation

        Returns:
            Restoration confirmation

        Raises:
            ReportNotFoundError: If report doesn't exist
            ReportOwnershipError: If user doesn't own the report
            RestoreWindowExpiredError: If restore window has passed
        """
        # Get report including soft-deleted
        report = await self._get_report_by_id(
            session, report_id, include_deleted=True
        )

        if report is None:
            logger.warning(
                "dashboard.restore_not_found",
                extra={"report_id": str(report_id)},
            )
            raise ReportNotFoundError(f"Report {report_id} not found")

        if report.user_id != user_id:
            logger.warning(
                "dashboard.restore_ownership_denied",
                extra={
                    "report_id": str(report_id),
                    "owner_id": str(report.user_id),
                    "requester_id": str(user_id),
                },
            )
            raise ReportOwnershipError("Not authorized to restore this report")

        # Check if report is deleted
        if report.deleted_at is None:
            # Report is not deleted, nothing to restore
            return {"restored": True}

        # Check restore window
        now = datetime.now(timezone.utc)
        restore_deadline = report.deleted_at + timedelta(seconds=RESTORE_WINDOW_SECONDS)

        if now > restore_deadline:
            logger.warning(
                "dashboard.restore_window_expired",
                extra={
                    "report_id": str(report_id),
                    "deleted_at": report.deleted_at.isoformat(),
                    "deadline": restore_deadline.isoformat(),
                },
            )
            raise RestoreWindowExpiredError("Restore window has expired")

        # Restore
        report.deleted_at = None
        await session.commit()

        logger.info(
            "dashboard.report_restored",
            extra={
                "report_id": str(report_id),
                "user_id": str(user_id),
            },
        )

        return {"restored": True}

    async def _get_report_by_id(
        self,
        session: AsyncSession,
        report_id: UUID,
        include_deleted: bool = False,
    ) -> Optional[Report]:
        """Get report by ID from database.

        Args:
            session: Database session
            report_id: Report UUID
            include_deleted: Whether to include soft-deleted reports

        Returns:
            Report model or None if not found
        """
        if include_deleted:
            query = select(Report).where(Report.id == report_id)
        else:
            query = select(Report).where(
                Report.id == report_id,
                Report.deleted_at.is_(None),
            )

        result = await session.execute(query)
        return result.scalar_one_or_none()

    def _build_thumbnail_url(self, thumbnail_key: Optional[str]) -> Optional[str]:
        """Build CDN URL for thumbnail.

        Args:
            thumbnail_key: S3 key for thumbnail

        Returns:
            Full CDN URL or None
        """
        if not thumbnail_key:
            return None

        # TODO: Use CDN URL from config when available
        # For now, return a placeholder that follows the pattern
        return f"https://cdn.example.com/{thumbnail_key}"


# Singleton instance
dashboard_service = DashboardService()
