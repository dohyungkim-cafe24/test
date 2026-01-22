"""Sharing router for report sharing endpoints.

@feature F009 - Report Sharing

Implements:
- GET /api/v1/reports/{report_id}/share - Get share status
- POST /api/v1/reports/{report_id}/share - Enable sharing
- DELETE /api/v1/reports/{report_id}/share - Disable sharing
- GET /api/v1/shared/{share_token} - Public access to shared report

Acceptance Criteria:
- AC-049: Share button shows on report page (default private)
- AC-050: Enable sharing generates unique URL
- AC-051: Shared URL accessible without authentication
- AC-054: Disabling sharing invalidates the URL
- AC-055: Re-enabling generates new unique URL
"""
from typing import Annotated, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel

from api.routers.auth import get_current_user
from api.services.database import get_db_session
from api.services.sharing_service import (
    ShareDisabledError,
    ShareNotFoundError,
    ShareOwnershipError,
    ShareReportNotFoundError,
    sharing_service,
)


# Request/Response schemas
class ShareStatusResponse(BaseModel):
    """Response for share status endpoint."""

    share_enabled: bool
    share_token: Optional[str] = None
    share_url: Optional[str] = None


class ShareEnabledResponse(BaseModel):
    """Response when sharing is enabled."""

    share_enabled: bool
    share_token: str
    share_url: str
    created_at: str


class ShareDisabledResponse(BaseModel):
    """Response when sharing is disabled."""

    share_enabled: bool
    message: str


class SharedReportResponse(BaseModel):
    """Response for public shared report.

    AC-051: Shared URL accessible without authentication
    Read-only view with AI disclaimer visible.
    """

    id: str
    performance_score: Optional[int] = None
    overall_assessment: str
    strengths: list[dict[str, Any]]
    weaknesses: list[dict[str, Any]]
    recommendations: list[dict[str, Any]]
    metrics: dict[str, Any]
    stamps: list[dict[str, Any]]
    disclaimer: str
    created_at: Optional[str] = None


# Routers
router = APIRouter(prefix="/reports", tags=["sharing"])
public_router = APIRouter(prefix="/shared", tags=["sharing"])


@router.get(
    "/{report_id}/share",
    response_model=ShareStatusResponse,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to view sharing status"},
        404: {"description": "Report not found"},
    },
)
async def get_share_status(
    report_id: Annotated[UUID, Path(description="Report ID")],
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Get current sharing status for a report.

    AC-049: Share button shows on report page (default private)

    Returns whether sharing is enabled and the share URL if active.
    Requires authentication and ownership.
    """
    user_id = UUID(current_user["id"])

    try:
        async with get_db_session() as session:
            result = await sharing_service.get_share_status(
                session=session,
                report_id=report_id,
                user_id=user_id,
            )
        return ShareStatusResponse(**result)

    except ShareReportNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    except ShareOwnershipError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view sharing status",
        )


@router.post(
    "/{report_id}/share",
    response_model=ShareEnabledResponse,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to enable sharing"},
        404: {"description": "Report not found"},
    },
)
async def enable_sharing(
    report_id: Annotated[UUID, Path(description="Report ID")],
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Enable sharing for a report, generating a unique URL.

    AC-050: Enable sharing generates unique URL
    AC-055: Re-enabling generates new unique URL (old one invalidated)

    Returns the share token and URL. If sharing was previously enabled,
    the old URL is invalidated and a new one is generated.
    """
    user_id = UUID(current_user["id"])

    try:
        async with get_db_session() as session:
            result = await sharing_service.enable_sharing(
                session=session,
                report_id=report_id,
                user_id=user_id,
            )
        return ShareEnabledResponse(**result)

    except ShareReportNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    except ShareOwnershipError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to enable sharing",
        )


@router.delete(
    "/{report_id}/share",
    response_model=ShareDisabledResponse,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to disable sharing"},
        404: {"description": "Report not found"},
    },
)
async def disable_sharing(
    report_id: Annotated[UUID, Path(description="Report ID")],
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Disable sharing for a report, invalidating the URL.

    AC-054: Disabling sharing invalidates the URL

    Any existing share links will no longer work after this call.
    """
    user_id = UUID(current_user["id"])

    try:
        async with get_db_session() as session:
            result = await sharing_service.disable_sharing(
                session=session,
                report_id=report_id,
                user_id=user_id,
            )
        return ShareDisabledResponse(**result)

    except ShareReportNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    except ShareOwnershipError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to disable sharing",
        )


@public_router.get(
    "/{share_token}",
    response_model=SharedReportResponse,
    responses={
        403: {"description": "Sharing disabled for this report"},
        404: {"description": "Share link not found"},
    },
)
async def get_shared_report(
    share_token: Annotated[str, Path(description="8-character share token")],
):
    """Get a shared report via public token.

    AC-051: Shared URL accessible without authentication

    Returns the report content in read-only form with AI disclaimer.
    No authentication required.
    """
    try:
        async with get_db_session() as session:
            result = await sharing_service.get_shared_report(
                session=session,
                share_token=share_token,
            )
        return SharedReportResponse(**result)

    except ShareNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share link not found",
        )
    except ShareDisabledError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sharing disabled. The owner has disabled sharing for this report.",
        )
