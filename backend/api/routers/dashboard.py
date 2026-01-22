"""Dashboard router for report history endpoints.

@feature F010 - Report History Dashboard

Implements:
- GET /api/v1/dashboard/reports - List user's reports (paginated)
- DELETE /api/v1/reports/{report_id} - Soft delete report
- POST /api/v1/reports/{report_id}/restore - Restore deleted report (undo)

Acceptance Criteria:
- AC-056: Dashboard lists reports sorted by date descending
- AC-057: List items show thumbnail, date, summary indicator
- AC-058: Clicking report navigates to full view
- AC-059: Delete report shows confirmation dialog
- AC-060: Empty state shows upload CTA
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from api.routers.auth import get_current_user
from api.schemas.dashboard import (
    DeleteReportResponse,
    ReportListResponse,
    RestoreReportResponse,
)
from api.services.dashboard_service import (
    ReportNotFoundError,
    ReportOwnershipError,
    RestoreWindowExpiredError,
    dashboard_service,
)
from api.services.database import get_db_session


router = APIRouter(prefix="/dashboard", tags=["dashboard"])
reports_router = APIRouter(prefix="/reports", tags=["reports"])


@router.get(
    "/reports",
    response_model=ReportListResponse,
    responses={
        401: {"description": "Not authenticated"},
    },
)
async def list_reports(
    current_user: Annotated[dict, Depends(get_current_user)],
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    limit: Annotated[int, Query(ge=1, le=50, description="Items per page")] = 10,
):
    """List user's analysis reports for dashboard.

    AC-056: Returns reports sorted by date descending (newest first)
    AC-057: Each item includes thumbnail, date, and summary indicator (key moments count)
    AC-060: Returns empty list for new users (frontend handles empty state display)

    The response supports pagination for users with many reports.
    """
    user_id = UUID(current_user["id"])

    async with get_db_session() as session:
        result = await dashboard_service.list_user_reports(
            session=session,
            user_id=user_id,
            page=page,
            limit=limit,
        )

    return ReportListResponse(**result)


@reports_router.delete(
    "/{report_id}",
    response_model=DeleteReportResponse,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to delete this report"},
        404: {"description": "Report not found"},
    },
)
async def delete_report(
    report_id: Annotated[UUID, Path(description="Report ID to delete")],
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Delete a report (soft delete with undo support).

    AC-059: Supports delete confirmation workflow
    BDD: Undo toast shows for 10 seconds

    The report is soft-deleted and can be restored within a 10-second window.
    After the window expires, the report is permanently deleted by a background job.
    """
    user_id = UUID(current_user["id"])

    try:
        async with get_db_session() as session:
            result = await dashboard_service.delete_report(
                session=session,
                report_id=report_id,
                user_id=user_id,
            )
        return DeleteReportResponse(**result)

    except ReportNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    except ReportOwnershipError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this report",
        )


@reports_router.post(
    "/{report_id}/restore",
    response_model=RestoreReportResponse,
    responses={
        400: {"description": "Restore window has expired"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to restore this report"},
        404: {"description": "Report not found"},
    },
)
async def restore_report(
    report_id: Annotated[UUID, Path(description="Report ID to restore")],
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Restore a deleted report (undo delete).

    BDD: User deletes report with undo toast (10 seconds)

    Can only restore reports within the 10-second undo window.
    Returns 400 if the restore window has expired.
    """
    user_id = UUID(current_user["id"])

    try:
        async with get_db_session() as session:
            result = await dashboard_service.restore_report(
                session=session,
                report_id=report_id,
                user_id=user_id,
            )
        return RestoreReportResponse(**result)

    except ReportNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    except ReportOwnershipError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to restore this report",
        )
    except RestoreWindowExpiredError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restore window has expired",
        )
