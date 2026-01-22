"""Analysis and processing schemas for request/response validation.

@feature F005 - Pose Estimation Processing
@feature F006 - Stamp Generation
@feature F007 - LLM Analysis

Acceptance Criteria:
- AC-025: Video processed with 33-joint XYZ coordinate extraction
- AC-026: Selected subject tracked across frames via bounding box
- AC-027: Successful pose data stored in structured JSON
- AC-028: Over 20% frame failure marks analysis as failed with guidance
- AC-029: Processing progress logged and retrievable via status endpoint
"""
from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# --- Request Schemas ---


class StartAnalysisRequest(BaseModel):
    """Request to start analysis pipeline.

    POST /api/v1/analysis/start/{video_id}
    """

    subject_id: str = Field(..., description="Subject ID for the analysis target")
    body_specs_id: str = Field(..., description="Body specs ID for the user")


# --- Response Schemas ---


class StartAnalysisResponse(BaseModel):
    """Response after starting analysis.

    Returns analysis ID and WebSocket URL for status updates.
    """

    analysis_id: str = Field(..., description="Created analysis identifier")
    video_id: str = Field(..., description="Video being analyzed")
    status: Literal["queued"] = Field(default="queued", description="Initial status")
    estimated_minutes: int = Field(
        default=3, ge=1, le=10, description="Estimated processing time in minutes"
    )
    websocket_url: str = Field(..., description="WebSocket URL for real-time status")


class StageStatus(BaseModel):
    """Status of a single processing stage.

    AC-029: Processing progress logged and retrievable via status endpoint
    """

    name: str = Field(
        ..., description="Stage name (pose_estimation, stamp_generation, etc.)"
    )
    status: Literal["pending", "processing", "completed", "failed"] = Field(
        default="pending", description="Stage status"
    )
    started_at: Optional[datetime] = Field(default=None, description="Stage start time")
    completed_at: Optional[datetime] = Field(
        default=None, description="Stage completion time"
    )
    progress_percent: Optional[int] = Field(
        default=None, ge=0, le=100, description="Progress percentage (if processing)"
    )
    frames_processed: Optional[int] = Field(
        default=None, ge=0, description="Frames processed (for pose_estimation)"
    )
    total_frames: Optional[int] = Field(
        default=None, ge=0, description="Total frames (for pose_estimation)"
    )


class AnalysisError(BaseModel):
    """Error details for failed analysis.

    AC-028: Over 20% frame failure marks analysis as failed with guidance
    """

    code: str = Field(
        ..., description="Error code (POSE_QUALITY_LOW, LLM_RETRY_EXHAUSTED, etc.)"
    )
    message: str = Field(..., description="Error message for logging")
    user_action: str = Field(
        ..., description="User-friendly action suggestion"
    )


class ProcessingStatusResponse(BaseModel):
    """Response for processing status endpoint.

    GET /api/v1/processing/status/{analysis_id}

    AC-029: Processing progress logged and retrievable via status endpoint
    """

    analysis_id: str = Field(..., description="Analysis identifier")
    status: Literal[
        "queued",
        "processing",
        "pose_estimation",
        "stamp_generation",
        "llm_analysis",
        "report_generation",
        "completed",
        "failed",
    ] = Field(..., description="Overall analysis status")

    # For in-progress
    current_stage: Optional[str] = Field(default=None, description="Current processing stage")
    stages: Optional[list[StageStatus]] = Field(
        default=None, description="Detailed stage statuses"
    )
    estimated_completion: Optional[datetime] = Field(
        default=None, description="Estimated completion time"
    )

    # For completed
    report_id: Optional[str] = Field(
        default=None, description="Report ID (when completed)"
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="Completion timestamp"
    )
    total_duration_seconds: Optional[int] = Field(
        default=None, ge=0, description="Total processing duration"
    )

    # For failed
    failed_stage: Optional[str] = Field(
        default=None, description="Stage where failure occurred"
    )
    error: Optional[AnalysisError] = Field(
        default=None, description="Error details"
    )
    failed_at: Optional[datetime] = Field(default=None, description="Failure timestamp")


# --- Pose Data Schemas ---
# AC-025: Video processed with 33-joint XYZ coordinate extraction
# AC-026: Selected subject tracked across frames via bounding box
# AC-027: Successful pose data stored in structured JSON


class JointCoordinate(BaseModel):
    """Single joint coordinate from MediaPipe pose estimation.

    AC-025: Video processed with 33-joint XYZ coordinate extraction

    MediaPipe Pose outputs 33 landmarks (joints).
    """

    joint_id: int = Field(..., ge=0, le=32, description="Joint index (0-32)")
    name: str = Field(..., description="Joint name (e.g., 'nose', 'left_shoulder')")
    x: float = Field(
        ..., ge=0.0, le=1.0, description="X coordinate (normalized 0-1)"
    )
    y: float = Field(
        ..., ge=0.0, le=1.0, description="Y coordinate (normalized 0-1)"
    )
    z: float = Field(..., description="Z coordinate (depth, relative to hips)")
    visibility: float = Field(
        ..., ge=0.0, le=1.0, description="Visibility confidence (0-1)"
    )


class BoundingBox(BaseModel):
    """Bounding box for subject tracking.

    AC-026: Selected subject tracked across frames via bounding box
    """

    x: int = Field(..., ge=0, description="X coordinate of top-left corner")
    y: int = Field(..., ge=0, description="Y coordinate of top-left corner")
    width: int = Field(..., gt=0, description="Width of bounding box")
    height: int = Field(..., gt=0, description="Height of bounding box")


class PoseFrame(BaseModel):
    """Pose data for a single frame.

    AC-025: Video processed with 33-joint XYZ coordinate extraction
    """

    frame_number: int = Field(..., ge=0, description="Frame number in video")
    timestamp_seconds: float = Field(..., ge=0.0, description="Timestamp in video")
    joints: list[JointCoordinate] = Field(
        ..., min_length=33, max_length=33, description="33 joint coordinates"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Overall pose detection confidence"
    )
    bounding_box: Optional[BoundingBox] = Field(
        default=None, description="Subject bounding box in this frame"
    )


class TrackingStats(BaseModel):
    """Subject tracking statistics.

    AC-026: Selected subject tracked across frames via bounding box
    """

    frames_tracked: int = Field(..., ge=0, description="Frames where subject was tracked")
    frames_lost: int = Field(..., ge=0, description="Frames where tracking was lost")
    average_confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Average tracking confidence"
    )


class PoseData(BaseModel):
    """Complete pose data for an analysis.

    AC-027: Successful pose data stored in structured JSON

    This is the structure stored in S3 as pose_data/{analysis_id}/pose.json.gz
    """

    analysis_id: str = Field(..., description="Analysis identifier")
    subject_id: str = Field(..., description="Subject identifier")
    video_id: Optional[str] = Field(default=None, description="Video identifier")
    total_frames: int = Field(..., ge=0, description="Total video frames")
    successful_frames: int = Field(..., ge=0, description="Frames with successful pose detection")
    failed_frames: int = Field(..., ge=0, description="Frames with failed pose detection")
    fps: Optional[float] = Field(default=None, gt=0, description="Video frame rate")
    tracking: dict = Field(..., description="Tracking statistics")
    frames: list[PoseFrame] = Field(
        default_factory=list, description="Pose data per frame"
    )


# --- WebSocket Message Schemas ---


class WSProgressMessage(BaseModel):
    """WebSocket progress update message.

    Sent during processing to update client on progress.
    """

    type: Literal["progress"] = "progress"
    stage: str = Field(..., description="Current processing stage")
    progress_percent: int = Field(..., ge=0, le=100, description="Progress percentage")
    message: str = Field(..., description="Progress message")


class WSStageCompleteMessage(BaseModel):
    """WebSocket stage completion message."""

    type: Literal["stage_complete"] = "stage_complete"
    stage: str = Field(..., description="Completed stage")
    next_stage: Optional[str] = Field(default=None, description="Next stage (if any)")


class WSCompleteMessage(BaseModel):
    """WebSocket analysis completion message."""

    type: Literal["complete"] = "complete"
    report_id: str = Field(..., description="Generated report ID")


class WSErrorMessage(BaseModel):
    """WebSocket error message.

    AC-028: Over 20% frame failure marks analysis as failed with guidance
    """

    type: Literal["error"] = "error"
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    user_action: str = Field(..., description="User-friendly action suggestion")
