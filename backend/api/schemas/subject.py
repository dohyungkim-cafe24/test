"""Subject selection schemas for request/response validation.

@feature F003 - Subject Selection

Acceptance Criteria:
- AC-013: Thumbnail grid displays after upload completes
- AC-014: Tap on person highlights with selection indicator
- AC-015: Confirm selection stores bounding box for tracking
- AC-016: Selection can be changed before confirmation
- AC-017: Single person auto-selected with confirm option
"""
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Bounding box coordinates for detected person.

    Represents the rectangular region containing a detected person
    in a thumbnail frame.
    """

    x: int = Field(..., ge=0, description="X coordinate of top-left corner")
    y: int = Field(..., ge=0, description="Y coordinate of top-left corner")
    width: int = Field(..., gt=0, description="Width of bounding box")
    height: int = Field(..., gt=0, description="Height of bounding box")


class DetectedPerson(BaseModel):
    """A person detected in a thumbnail frame."""

    person_id: str = Field(..., description="Unique identifier for this person in the video")
    bounding_box: BoundingBox = Field(..., description="Location of person in frame")
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence (0-1)")


class ThumbnailResponse(BaseModel):
    """Single thumbnail with detected persons."""

    thumbnail_id: str = Field(..., description="Thumbnail identifier")
    frame_number: int = Field(..., ge=0, description="Frame number in video")
    timestamp_seconds: float = Field(..., ge=0, description="Timestamp in video")
    image_url: str = Field(..., description="URL to thumbnail image")
    detected_persons: list[DetectedPerson] = Field(
        default_factory=list, description="Persons detected in this frame"
    )


class AutoSelectInfo(BaseModel):
    """Auto-selection info for single-person videos."""

    thumbnail_id: str = Field(..., description="Thumbnail containing the person")
    person_id: str = Field(..., description="Person ID to auto-select")
    bounding_box: BoundingBox = Field(..., description="Bounding box of the person")


class ThumbnailsResponse(BaseModel):
    """Response for thumbnails endpoint.

    AC-013: Thumbnail grid displays after upload completes
    AC-017: Single person auto-selected with confirm option
    """

    video_id: str = Field(..., description="Video identifier")
    status: Literal["processing", "ready", "no_subjects", "failed"] = Field(
        ..., description="Processing status"
    )
    total_persons_detected: int = Field(
        default=0, ge=0, description="Total unique persons detected"
    )
    thumbnails: list[ThumbnailResponse] = Field(
        default_factory=list, description="Extracted thumbnail frames"
    )
    auto_select: Optional[AutoSelectInfo] = Field(
        default=None, description="Auto-selection info for single person"
    )
    message: Optional[str] = Field(
        default=None, description="Status message for user"
    )


class SubjectSelectRequest(BaseModel):
    """Request to select analysis subject.

    AC-014: Tap on person highlights with selection indicator
    AC-015: Confirm selection stores bounding box for tracking
    AC-016: Selection can be changed before confirmation
    """

    thumbnail_id: str = Field(..., description="Thumbnail where selection was made")
    person_id: str = Field(..., description="ID of selected person")


class SubjectSelectResponse(BaseModel):
    """Response after subject selection.

    AC-015: Confirm selection stores bounding box for tracking
    """

    subject_id: str = Field(..., description="Created subject identifier")
    video_id: str = Field(..., description="Video identifier")
    person_id: str = Field(..., description="Selected person ID")
    bounding_box: BoundingBox = Field(..., description="Initial bounding box for tracking")
    auto_selected: bool = Field(
        default=False, description="Whether this was auto-selected (single person)"
    )


class SubjectError(BaseModel):
    """Generic subject selection error response."""

    error: str
    error_description: str
