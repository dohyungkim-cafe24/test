"""Stamp schemas for request/response validation.

@feature F006 - Stamp Generation

Acceptance Criteria:
- AC-030: Strikes detected by arm velocity and trajectory patterns
- AC-031: Defensive actions detected by torso and arm positioning
- AC-032: Each action timestamped with frame number and confidence
- AC-033: Stamps stored with type, timestamp, side, and confidence
- AC-034: No actions detected proceeds with generic feedback
"""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


# Valid action types from DATA_MODEL.md
VALID_ACTION_TYPES = [
    "jab", "straight", "hook", "uppercut",  # Strikes
    "guard_up", "guard_down", "slip", "duck", "bob_weave",  # Defense
]

STRIKE_TYPES = ["jab", "straight", "hook", "uppercut"]
DEFENSE_TYPES = ["guard_up", "guard_down", "slip", "duck", "bob_weave"]

# Valid sides
VALID_SIDES = ["left", "right", "both"]


class StampCreate(BaseModel):
    """Schema for creating a new stamp.

    AC-032: Each action timestamped with frame number and confidence
    AC-033: Stamps stored with type, timestamp, side, and confidence
    """

    timestamp_seconds: float = Field(
        ..., ge=0.0, description="Timestamp in video (seconds)"
    )
    frame_number: int = Field(..., ge=0, description="Frame number in video")
    action_type: str = Field(
        ..., description="Action type (jab, straight, hook, etc.)"
    )
    side: str = Field(..., description="Body side (left, right, both)")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Detection confidence (0-1)"
    )
    velocity_vector: Optional[dict] = Field(
        default=None, description="Velocity vector at detection"
    )
    trajectory_data: Optional[list] = Field(
        default=None, description="Trajectory points leading to detection"
    )

    @field_validator("action_type")
    @classmethod
    def validate_action_type(cls, v: str) -> str:
        """Validate action type is one of allowed values."""
        if v not in VALID_ACTION_TYPES:
            raise ValueError(
                f"Invalid action_type '{v}'. Must be one of: {VALID_ACTION_TYPES}"
            )
        return v

    @field_validator("side")
    @classmethod
    def validate_side(cls, v: str) -> str:
        """Validate side is one of allowed values."""
        if v not in VALID_SIDES:
            raise ValueError(f"Invalid side '{v}'. Must be one of: {VALID_SIDES}")
        return v


class StampResponse(BaseModel):
    """Response schema for a single stamp.

    BDD: each stamp should include action_type, timestamp, frame_number, body_side, confidence
    """

    id: str = Field(..., description="Stamp unique identifier")
    analysis_id: str = Field(..., description="Associated analysis ID")
    timestamp_seconds: float = Field(..., description="Timestamp in video (seconds)")
    frame_number: int = Field(..., description="Frame number in video")
    action_type: str = Field(..., description="Action type")
    side: str = Field(..., description="Body side")
    confidence: float = Field(..., description="Detection confidence (0-1)")
    velocity_vector: Optional[dict] = Field(
        default=None, description="Velocity vector at detection"
    )
    trajectory_data: Optional[list] = Field(
        default=None, description="Trajectory data"
    )
    thumbnail_key: Optional[str] = Field(
        default=None, description="S3 key for stamp thumbnail"
    )
    created_at: datetime = Field(..., description="Creation timestamp")


class StampListResponse(BaseModel):
    """Response schema for list of stamps.

    AC-034: No actions detected proceeds with generic feedback
    (When stamps is empty, this indicates no significant actions detected)
    """

    stamps: list[StampResponse] = Field(
        default_factory=list, description="List of detected stamps"
    )
    total: int = Field(..., ge=0, description="Total number of stamps")
    strikes_count: int = Field(..., ge=0, description="Number of strike stamps")
    defense_count: int = Field(..., ge=0, description="Number of defense stamps")

    @classmethod
    def from_stamps(cls, stamps: list[StampResponse]) -> "StampListResponse":
        """Create response from list of stamps."""
        strikes = sum(1 for s in stamps if s.action_type in STRIKE_TYPES)
        defense = sum(1 for s in stamps if s.action_type in DEFENSE_TYPES)
        return cls(
            stamps=stamps,
            total=len(stamps),
            strikes_count=strikes,
            defense_count=defense,
        )


class StampSummary(BaseModel):
    """Summary statistics for stamps.

    Used in analysis reports and status responses.
    """

    total_stamps: int = Field(..., ge=0, description="Total detected actions")
    strikes: dict = Field(
        ..., description="Strike counts by type (jab, straight, hook, uppercut)"
    )
    defense: dict = Field(
        ..., description="Defense counts by type (guard_up, slip, duck, etc.)"
    )
    avg_confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Average detection confidence"
    )
    no_actions_detected: bool = Field(
        default=False,
        description="Flag indicating no significant actions were detected (AC-034)",
    )
