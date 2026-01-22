"""Processing router for analysis pipeline endpoints.

@feature F005 - Pose Estimation Processing

Implements:
- POST /api/v1/analysis/start/{video_id} - Start analysis
- GET /api/v1/processing/status/{analysis_id} - Get status

Acceptance Criteria:
- AC-029: Processing progress logged and retrievable via status endpoint
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status

from api.routers.auth import get_current_user
from api.schemas.analysis import (
    ProcessingStatusResponse,
    StartAnalysisRequest,
    StartAnalysisResponse,
)
from api.services.database import get_db_session
from api.services.processing_service import (
    AnalysisAlreadyExistsError,
    AnalysisNotFoundError,
    BodySpecsNotFoundError,
    SubjectNotFoundError,
    VideoNotFoundError,
    processing_service,
)

router = APIRouter(tags=["processing"])


@router.post(
    "/analysis/start/{video_id}",
    response_model=StartAnalysisResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Video, subject, or body specs not found"},
        409: {"description": "Analysis already exists for this video"},
    },
)
async def start_analysis(
    video_id: Annotated[UUID, Path(description="Video ID to analyze")],
    request: StartAnalysisRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Start analysis pipeline for a video.

    Requires:
    - Valid video owned by current user
    - Subject selected for the video
    - Body specs submitted for the video

    Returns:
    - analysis_id: Unique identifier for tracking
    - websocket_url: URL for real-time status updates
    - estimated_minutes: Estimated processing time

    AC-029: Processing progress logged and retrievable via status endpoint
    """
    user_id = UUID(current_user["id"])

    try:
        subject_id = UUID(request.subject_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid subject_id format",
        )

    try:
        body_specs_id = UUID(request.body_specs_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid body_specs_id format",
        )

    try:
        async with get_db_session() as session:
            result = await processing_service.start_analysis(
                session=session,
                video_id=video_id,
                user_id=user_id,
                subject_id=subject_id,
                body_specs_id=body_specs_id,
            )
        return StartAnalysisResponse(**result)

    except VideoNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    except SubjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found for this video",
        )
    except BodySpecsNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Body specs not found for this video",
        )
    except AnalysisAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Analysis already exists for this video",
        )


@router.get(
    "/processing/status/{analysis_id}",
    response_model=ProcessingStatusResponse,
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Analysis not found"},
    },
)
async def get_processing_status(
    analysis_id: Annotated[UUID, Path(description="Analysis ID")],
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Get current processing status for an analysis.

    Returns detailed status including:
    - Overall status (queued, processing, completed, failed)
    - Current processing stage
    - Progress percentage for each stage
    - Estimated completion time
    - Error details if failed

    AC-029: Processing progress logged and retrievable via status endpoint
    """
    user_id = UUID(current_user["id"])

    try:
        async with get_db_session() as session:
            result = await processing_service.get_status(
                session=session,
                analysis_id=analysis_id,
                user_id=user_id,
            )
        return ProcessingStatusResponse(**result)

    except AnalysisNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )
