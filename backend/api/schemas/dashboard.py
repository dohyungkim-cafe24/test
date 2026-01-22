"""Dashboard schemas for request/response validation.

@feature F010 - Report History Dashboard

Acceptance Criteria:
- AC-056: Dashboard lists reports sorted by date descending
- AC-057: List items show thumbnail, date, summary indicator
- AC-059: Delete report with undo support
- AC-060: Empty state shows upload CTA
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReportListItem(BaseModel):
    """Schema for a single report in the dashboard list.

    AC-057: List items show thumbnail, date, summary indicator
    """

    id: str = Field(..., description="Report unique identifier")
    video_id: str = Field(..., description="Associated video ID")
    thumbnail_url: Optional[str] = Field(
        default=None, description="URL to video thumbnail"
    )
    analyzed_at: str = Field(
        ..., description="Analysis timestamp (ISO format)"
    )
    key_moments_count: int = Field(
        ..., ge=0, description="Number of key moments detected"
    )
    performance_score: Optional[int] = Field(
        default=None, ge=0, le=100, description="Overall performance score (0-100)"
    )


class ReportListResponse(BaseModel):
    """Schema for paginated report list response.

    AC-056: Dashboard lists reports sorted by date descending
    """

    items: list[ReportListItem] = Field(
        default_factory=list, description="List of reports"
    )
    total: int = Field(..., ge=0, description="Total number of reports")
    page: int = Field(..., ge=1, description="Current page number")
    has_more: bool = Field(
        ..., description="Whether there are more reports to load"
    )


class DeleteReportResponse(BaseModel):
    """Schema for delete report response.

    AC-059: Delete report shows confirmation dialog
    BDD: Undo toast for 10 seconds
    """

    deleted: bool = Field(..., description="Whether deletion was successful")
    can_restore_until: str = Field(
        ..., description="ISO timestamp until which the report can be restored"
    )


class RestoreReportResponse(BaseModel):
    """Schema for restore report response.

    BDD: User deletes report with undo toast (10 seconds)
    """

    restored: bool = Field(..., description="Whether restoration was successful")
