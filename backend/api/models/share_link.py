"""ShareLink database model for public report sharing.

@feature F009 - Report Sharing

Maps to share_links table as defined in DATA_MODEL.md.

Acceptance Criteria:
- AC-050: Enable sharing generates unique URL (8-char hash)
- AC-054: Disabling sharing invalidates the URL
- AC-055: Re-enabling generates new unique URL
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from api.models.user import Base


class ShareLink(Base):
    """ShareLink model for public sharing of reports.

    AC-050: URL uses short 8-character hash
    AC-054: Links can be deactivated (is_active=False)
    AC-055: Re-enabling creates new link with new hash

    Only one active share link per report (enforced via partial unique index).
    """

    __tablename__ = "share_links"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    report_id: Mapped[UUID] = mapped_column(
        ForeignKey("reports.id", ondelete="CASCADE"), nullable=False
    )

    # Public identifier (8-char hash)
    share_hash: Mapped[str] = mapped_column(String(8), unique=True, nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Analytics
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_viewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Social preview (S3 key for generated OG image)
    og_image_key: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        # Index for looking up share by hash (public access)
        Index("idx_share_links_hash", "share_hash", postgresql_where=is_active == True),
        # Partial unique index: only one active link per report
        Index(
            "idx_share_links_active",
            "report_id",
            unique=True,
            postgresql_where=is_active == True,
        ),
    )
