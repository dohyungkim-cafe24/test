"""Sharing service for report sharing functionality.

@feature F009 - Report Sharing

Implements:
- AC-049: Share button shows on report page (default private)
- AC-050: Enable sharing generates unique URL
- AC-051: Shared URL accessible without authentication
- AC-054: Disabling sharing invalidates the URL
- AC-055: Re-enabling generates new unique URL
"""
import logging
import secrets
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import get_settings
from api.models.report import Report
from api.models.share_link import ShareLink

logger = logging.getLogger(__name__)


class SharingServiceError(Exception):
    """Base exception for sharing service errors."""

    pass


class ShareReportNotFoundError(SharingServiceError):
    """Report not found in database."""

    pass


class ShareOwnershipError(SharingServiceError):
    """User not authorized to manage sharing for this report."""

    pass


class ShareNotFoundError(SharingServiceError):
    """Share link not found."""

    pass


class ShareDisabledError(SharingServiceError):
    """Share link exists but is disabled."""

    pass


class SharingService:
    """Service for managing report sharing.

    Provides functionality to enable/disable sharing and retrieve
    shared reports via public tokens.
    """

    def _generate_share_token(self) -> str:
        """Generate a unique 8-character alphanumeric share token.

        AC-050: URL should use a short 8-character hash

        Returns:
            8-character alphanumeric token
        """
        # Use URL-safe characters, take first 8
        return secrets.token_urlsafe(6)[:8]

    def _get_share_url(self, token: str) -> str:
        """Build the full share URL for a token.

        Args:
            token: Share token

        Returns:
            Full URL to shared report
        """
        settings = get_settings()
        return f"{settings.frontend_url}/shared/{token}"

    async def get_share_status(
        self,
        session: AsyncSession,
        report_id: UUID,
        user_id: UUID,
    ) -> dict[str, Any]:
        """Get the current sharing status for a report.

        AC-049: Share button shows on report page (default private)

        Args:
            session: Database session
            report_id: Report UUID
            user_id: ID of user making the request

        Returns:
            Dictionary with share_enabled, share_token, share_url

        Raises:
            ShareReportNotFoundError: If report doesn't exist
            ShareOwnershipError: If user doesn't own the report
        """
        # Verify report exists and user owns it
        report = await self._get_report(session, report_id)
        if report is None:
            raise ShareReportNotFoundError(f"Report {report_id} not found")

        if report.user_id != user_id:
            raise ShareOwnershipError("Not authorized to view sharing status")

        # Check for active share link
        share_link = await self._get_active_share_link(session, report_id)

        if share_link is None:
            return {
                "share_enabled": False,
                "share_token": None,
                "share_url": None,
            }

        return {
            "share_enabled": True,
            "share_token": share_link.share_hash,
            "share_url": self._get_share_url(share_link.share_hash),
        }

    async def enable_sharing(
        self,
        session: AsyncSession,
        report_id: UUID,
        user_id: UUID,
    ) -> dict[str, Any]:
        """Enable sharing for a report, generating a unique URL.

        AC-050: Enable sharing generates unique URL
        AC-055: Re-enabling generates new unique URL

        If sharing was previously enabled, the old token is invalidated
        and a new one is generated.

        Args:
            session: Database session
            report_id: Report UUID
            user_id: ID of user making the request

        Returns:
            Dictionary with share_enabled, share_token, share_url, created_at

        Raises:
            ShareReportNotFoundError: If report doesn't exist
            ShareOwnershipError: If user doesn't own the report
        """
        # Verify report exists and user owns it
        report = await self._get_report(session, report_id)
        if report is None:
            logger.warning(
                "sharing.report_not_found",
                extra={"report_id": str(report_id)},
            )
            raise ShareReportNotFoundError(f"Report {report_id} not found")

        if report.user_id != user_id:
            logger.warning(
                "sharing.ownership_denied",
                extra={
                    "report_id": str(report_id),
                    "owner_id": str(report.user_id),
                    "requester_id": str(user_id),
                },
            )
            raise ShareOwnershipError("Not authorized to enable sharing")

        # Revoke any existing active share links (AC-055)
        await self._revoke_existing_links(session, report_id)

        # Generate new share token
        share_token = self._generate_share_token()
        now = datetime.now(timezone.utc)

        # Create new share link
        share_link = ShareLink(
            report_id=report_id,
            share_hash=share_token,
            is_active=True,
            created_at=now,
        )
        session.add(share_link)
        await session.commit()

        logger.info(
            "sharing.enabled",
            extra={
                "report_id": str(report_id),
                "user_id": str(user_id),
                "share_token": share_token,
            },
        )

        return {
            "share_enabled": True,
            "share_token": share_token,
            "share_url": self._get_share_url(share_token),
            "created_at": now.isoformat(),
        }

    async def disable_sharing(
        self,
        session: AsyncSession,
        report_id: UUID,
        user_id: UUID,
    ) -> dict[str, Any]:
        """Disable sharing for a report, invalidating the URL.

        AC-054: Disabling sharing invalidates the URL

        Args:
            session: Database session
            report_id: Report UUID
            user_id: ID of user making the request

        Returns:
            Dictionary with share_enabled, message

        Raises:
            ShareReportNotFoundError: If report doesn't exist
            ShareOwnershipError: If user doesn't own the report
        """
        # Verify report exists and user owns it
        report = await self._get_report(session, report_id)
        if report is None:
            raise ShareReportNotFoundError(f"Report {report_id} not found")

        if report.user_id != user_id:
            raise ShareOwnershipError("Not authorized to disable sharing")

        # Revoke active share links
        await self._revoke_existing_links(session, report_id)

        logger.info(
            "sharing.disabled",
            extra={
                "report_id": str(report_id),
                "user_id": str(user_id),
            },
        )

        return {
            "share_enabled": False,
            "message": "Sharing disabled",
        }

    async def get_shared_report(
        self,
        session: AsyncSession,
        share_token: str,
    ) -> dict[str, Any]:
        """Get a report via its public share token.

        AC-051: Shared URL accessible without authentication

        Args:
            session: Database session
            share_token: 8-character share token

        Returns:
            Report data for public display

        Raises:
            ShareNotFoundError: If share token doesn't exist
            ShareDisabledError: If sharing was disabled
        """
        # Look up share link by token
        query = select(ShareLink).where(ShareLink.share_hash == share_token)
        result = await session.execute(query)
        share_link = result.scalar_one_or_none()

        if share_link is None:
            logger.warning(
                "sharing.token_not_found",
                extra={"share_token": share_token},
            )
            raise ShareNotFoundError("Share link not found")

        if not share_link.is_active:
            logger.warning(
                "sharing.token_disabled",
                extra={"share_token": share_token},
            )
            raise ShareDisabledError("Sharing disabled for this report")

        # Get the report
        report = await self._get_report(session, share_link.report_id)
        if report is None:
            raise ShareNotFoundError("Report not found")

        # Update view count
        await session.execute(
            update(ShareLink)
            .where(ShareLink.id == share_link.id)
            .values(
                view_count=ShareLink.view_count + 1,
                last_viewed_at=datetime.now(timezone.utc),
            )
        )
        await session.commit()

        # Get stamps for key moments
        from api.services.report_service import report_service
        stamps = await report_service._get_stamps_for_analysis(session, report.analysis_id)

        logger.info(
            "sharing.public_view",
            extra={
                "share_token": share_token,
                "report_id": str(report.id),
            },
        )

        return {
            "id": str(report.id),
            "performance_score": report.performance_score,
            "overall_assessment": report.overall_assessment,
            "strengths": report.strengths,
            "weaknesses": report.weaknesses,
            "recommendations": report.recommendations,
            "metrics": report.metrics,
            "stamps": stamps,
            "disclaimer": report.disclaimer,
            "created_at": report.created_at.isoformat() if report.created_at else None,
        }

    async def _get_report(
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

    async def _get_active_share_link(
        self,
        session: AsyncSession,
        report_id: UUID,
    ) -> Optional[ShareLink]:
        """Get active share link for a report.

        Args:
            session: Database session
            report_id: Report UUID

        Returns:
            ShareLink or None if no active link
        """
        query = select(ShareLink).where(
            ShareLink.report_id == report_id,
            ShareLink.is_active == True,
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def _revoke_existing_links(
        self,
        session: AsyncSession,
        report_id: UUID,
    ) -> None:
        """Revoke all existing active share links for a report.

        Args:
            session: Database session
            report_id: Report UUID
        """
        await session.execute(
            update(ShareLink)
            .where(
                ShareLink.report_id == report_id,
                ShareLink.is_active == True,
            )
            .values(
                is_active=False,
                revoked_at=datetime.now(timezone.utc),
            )
        )


# Singleton instance
sharing_service = SharingService()
