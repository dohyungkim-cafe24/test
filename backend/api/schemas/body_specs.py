"""Body specification schemas for request/response validation.

@feature F004 - Body Specification Input

Acceptance Criteria:
- AC-018: Form with height, weight, experience level, stance
- AC-019: Validation: height (100-250cm), weight (30-200kg)
- AC-024: Body specs pre-filled for returning users
"""
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ExperienceLevel(str, Enum):
    """Boxing experience level options.

    Used for contextualizing analysis to user's skill level.
    """
    BEGINNER = "beginner"  # Less than 1 year
    INTERMEDIATE = "intermediate"  # 1-3 years
    ADVANCED = "advanced"  # 3-5 years
    COMPETITIVE = "competitive"  # Competition experience


class Stance(str, Enum):
    """Boxing stance options.

    Determines dominant side for analysis.
    """
    ORTHODOX = "orthodox"  # Left foot forward, right-handed
    SOUTHPAW = "southpaw"  # Right foot forward, left-handed


class BodySpecsCreate(BaseModel):
    """Request schema for creating body specifications.

    AC-018: Form with height, weight, experience level, stance
    AC-019: Validation: height (100-250cm), weight (30-200kg)
    """
    height_cm: int = Field(
        ...,
        ge=100,
        le=250,
        description="Height in centimeters (100-250cm)"
    )
    weight_kg: int = Field(
        ...,
        ge=30,
        le=200,
        description="Weight in kilograms (30-200kg)"
    )
    experience_level: ExperienceLevel = Field(
        ...,
        description="Boxing experience level"
    )
    stance: Stance = Field(
        ...,
        description="Boxing stance (orthodox/southpaw)"
    )


class BodySpecsResponse(BaseModel):
    """Response schema after saving body specifications.

    AC-015: Confirm selection stores bounding box for tracking
    """
    video_id: str = Field(..., description="Video identifier")
    body_specs_id: str = Field(..., description="Body specs record identifier")
    saved: bool = Field(..., description="Whether specs were saved successfully")
    persist_to_profile: bool = Field(
        ...,
        description="Whether specs were persisted to user profile for future use"
    )


class PrefillResponse(BaseModel):
    """Response schema for prefill endpoint.

    AC-024: Body specs pre-filled for returning users
    """
    has_saved_specs: bool = Field(
        ...,
        description="Whether user has previously saved body specs"
    )
    height_cm: Optional[int] = Field(
        default=None,
        description="Previously saved height in centimeters"
    )
    weight_kg: Optional[int] = Field(
        default=None,
        description="Previously saved weight in kilograms"
    )
    experience_level: Optional[str] = Field(
        default=None,
        description="Previously saved experience level"
    )
    stance: Optional[str] = Field(
        default=None,
        description="Previously saved stance"
    )
