"""Reports router for report retrieval endpoints.

@feature F008 - Report Display

Implements:
- GET /api/v1/reports/{report_id} - Get full report

Acceptance Criteria:
- AC-041: Summary section displays overall assessment
- AC-042: Strengths section shows 3-5 observations
- AC-043: Weaknesses section shows 3-5 improvement areas
- AC-044: Recommendations section shows 3-5 actionable items
- AC-045: Key moments section with timestamp links
- AC-046: Metrics displayed with visual indicators
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status

from api.routers.auth import get_current_user
from api.schemas.report import ReportDetailResponse
from api.services.database import get_db_session
from api.services.report_service import (
    ReportNotFoundError,
    ReportOwnershipError,
    report_service,
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get(
    "/{report_id}",
    response_model=ReportDetailResponse,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to access this report"},
        404: {"description": "Report not found"},
    },
)
async def get_report(
    report_id: Annotated[UUID, Path(description="Report ID to retrieve")],
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Get full report data by ID.

    Returns complete report including:
    - Summary with overall assessment and performance score (AC-041)
    - 3-5 strengths observations (AC-042)
    - 3-5 weaknesses/improvement areas (AC-043)
    - 3-5 actionable recommendations (AC-044)
    - Key moments with timestamps (AC-045)
    - Metrics with benchmarks for visualization (AC-046)
    - AI disclaimer (required)

    Requires authentication and ownership of the report.
    """
    user_id = UUID(current_user["id"])

    try:
        async with get_db_session() as session:
            result = await report_service.get_report(
                session=session,
                report_id=report_id,
                user_id=user_id,
            )
        return ReportDetailResponse(**result)

    except ReportNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    except ReportOwnershipError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this report",
        )


@router.get(
    "/by-analysis/{analysis_id}",
    response_model=ReportDetailResponse,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to access this report"},
        404: {"description": "Report not found"},
    },
)
async def get_report_by_analysis(
    analysis_id: Annotated[UUID, Path(description="Analysis ID")],
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Get report by analysis ID.

    Useful for fetching report after processing completes.
    """
    user_id = UUID(current_user["id"])

    try:
        async with get_db_session() as session:
            result = await report_service.get_report_by_analysis_id(
                session=session,
                analysis_id=analysis_id,
                user_id=user_id,
            )
        return ReportDetailResponse(**result)

    except ReportNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found for this analysis",
        )
    except ReportOwnershipError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this report",
        )
