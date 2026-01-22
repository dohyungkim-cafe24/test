"""Body specifications router for body specs endpoints.

@feature F004 - Body Specification Input

Implements:
- POST /analysis/body-specs/{video_id} - Create body specs for video
- GET /analysis/body-specs/prefill - Get user's saved specs for pre-fill
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status

from api.routers.auth import get_current_user_or_guest
from api.schemas.body_specs import (
    BodySpecsCreate,
    BodySpecsResponse,
    PrefillResponse,
)
from api.services.database import get_db_session
from api.services.body_specs_service import (
    VideoNotFoundError,
    body_specs_service,
)

router = APIRouter(prefix="/analysis", tags=["analysis", "body-specs"])


@router.get(
    "/body-specs/prefill",
    response_model=PrefillResponse,
    responses={
        401: {"description": "Not authenticated"},
    },
)
async def get_prefill(
    current_user: Annotated[dict, Depends(get_current_user_or_guest)],
):
    """Get user's saved body specs for pre-filling form.

    AC-024: Body specs pre-filled for returning users

    Returns previously saved body specifications if available.
    """
    user_id = UUID(current_user["id"])

    async with get_db_session() as session:
        result = await body_specs_service.get_prefill(
            session=session,
            user_id=user_id,
        )
    return PrefillResponse(**result)


@router.post(
    "/body-specs/{video_id}",
    response_model=BodySpecsResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Video not found"},
        422: {"description": "Validation error"},
    },
)
async def create_body_specs(
    video_id: Annotated[UUID, Path(description="Video ID")],
    request: BodySpecsCreate,
    current_user: Annotated[dict, Depends(get_current_user_or_guest)],
):
    """Create body specifications for a video.

    AC-018: Form with height, weight, experience level, stance
    AC-019: Validation: height (100-250cm), weight (30-200kg)

    Saves body specs for the video and persists to user profile
    for future pre-fill.
    """
    user_id = UUID(current_user["id"])

    try:
        async with get_db_session() as session:
            result = await body_specs_service.create_body_specs(
                session=session,
                user_id=user_id,
                video_id=video_id,
                height_cm=request.height_cm,
                weight_kg=request.weight_kg,
                experience_level=request.experience_level.value,
                stance=request.stance.value,
            )
        return BodySpecsResponse(**result)

    except VideoNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
