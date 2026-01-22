"""Subject selection router for thumbnail and subject endpoints.

@feature F003 - Subject Selection

Implements:
- AC-013: Thumbnail grid displays after upload completes
- AC-014: Tap on person highlights with selection indicator
- AC-015: Confirm selection stores bounding box for tracking
- AC-016: Selection can be changed before confirmation
- AC-017: Single person auto-selected with confirm option
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status

from api.routers.auth import get_current_user
from api.schemas.subject import (
    SubjectError,
    SubjectSelectRequest,
    SubjectSelectResponse,
    ThumbnailsResponse,
)
from api.services.database import get_db_session
from api.services.subject_service import (
    PersonNotFoundError,
    ThumbnailNotFoundError,
    VideoNotFoundError,
    subject_service,
)

router = APIRouter(prefix="/analysis", tags=["analysis", "subject"])


@router.get(
    "/thumbnails/{video_id}",
    response_model=ThumbnailsResponse,
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Video not found"},
    },
)
async def get_thumbnails(
    video_id: Annotated[UUID, Path(description="Video ID")],
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Get extracted thumbnails for subject selection.

    AC-013: Thumbnail grid displays after upload completes
    AC-017: Single person auto-selected with confirm option

    Returns a grid of 6-9 thumbnail frames with detected persons.
    If only one person is detected, includes auto_select info.
    """
    user_id = UUID(current_user["id"])

    try:
        async with get_db_session() as session:
            result = await subject_service.get_thumbnails(
                session=session,
                video_id=video_id,
                user_id=user_id,
            )
        return ThumbnailsResponse(**result)

    except VideoNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )


@router.post(
    "/subject/{video_id}",
    response_model=SubjectSelectResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Video, thumbnail, or person not found"},
        409: {"description": "Subject already selected (use PUT to update)"},
    },
)
async def select_subject(
    video_id: Annotated[UUID, Path(description="Video ID")],
    request: SubjectSelectRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Select analysis subject from thumbnail.

    AC-014: Tap on person highlights with selection indicator
    AC-015: Confirm selection stores bounding box for tracking
    AC-016: Selection can be changed before confirmation

    Stores the selected person's bounding box for tracking.
    If a subject was already selected, updates it.
    """
    user_id = UUID(current_user["id"])

    try:
        thumbnail_id = UUID(request.thumbnail_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid thumbnail_id format",
        )

    try:
        async with get_db_session() as session:
            result = await subject_service.select_subject(
                session=session,
                video_id=video_id,
                user_id=user_id,
                thumbnail_id=thumbnail_id,
                person_id=request.person_id,
            )
        return SubjectSelectResponse(**result)

    except VideoNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    except ThumbnailNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thumbnail not found",
        )
    except PersonNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
