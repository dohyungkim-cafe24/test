"""Upload schemas for request/response validation.

@feature F002 - Video Upload
"""
from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

# Constants from API spec
MAX_FILE_SIZE = 524_288_000  # 500MB in bytes
MIN_DURATION_SECONDS = 60  # 1 minute
MAX_DURATION_SECONDS = 180  # 3 minutes
CHUNK_SIZE = 5_242_880  # 5MB in bytes
ALLOWED_CONTENT_TYPES = {"video/mp4", "video/quicktime", "video/webm"}


class UploadInitiateRequest(BaseModel):
    """Request schema for initiating a chunked upload session.

    AC-006: Valid video file (MP4/MOV/WebM, <500MB, 1-3 min)
    """
    filename: str = Field(..., min_length=1, max_length=255)
    file_size: int = Field(..., gt=0)
    content_type: str
    duration_seconds: int = Field(..., gt=0)

    @field_validator("file_size")
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        """AC-008: File over 500MB shows size error message."""
        if v > MAX_FILE_SIZE:
            raise ValueError(
                f"Video file too large. Please upload a file under 500MB. "
                f"Current file: {v / 1_000_000:.0f}MB"
            )
        return v

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        """AC-010: Unsupported format shows format error message."""
        if v not in ALLOWED_CONTENT_TYPES:
            raise ValueError(
                f"Unsupported format. Please upload MP4, MOV, or WebM. "
                f"Detected format: {v}"
            )
        return v

    @field_validator("duration_seconds")
    @classmethod
    def validate_duration(cls, v: int) -> int:
        """AC-009: Video duration outside 1-3 min shows duration error."""
        if v < MIN_DURATION_SECONDS:
            raise ValueError(
                f"Video must be between 1 and 3 minutes. "
                f"Current duration: {v} seconds"
            )
        if v > MAX_DURATION_SECONDS:
            raise ValueError(
                f"Video must be between 1 and 3 minutes. "
                f"Current duration: {v // 60} minutes"
            )
        return v


class UploadInitiateResponse(BaseModel):
    """Response schema for upload initiation."""
    upload_id: str
    chunk_size: int = CHUNK_SIZE
    total_chunks: int
    expires_at: datetime


class UploadChunkResponse(BaseModel):
    """Response schema for chunk upload."""
    chunk_number: int
    received_bytes: int
    total_received: int
    progress_percent: int = Field(..., ge=0, le=100)


class UploadChunkError(BaseModel):
    """Error response for chunk already uploaded (409)."""
    error: str = "chunk_exists"
    error_description: str
    chunk_number: int


class UploadCompleteResponse(BaseModel):
    """Response schema for upload completion."""
    video_id: str
    status: Literal["processing_thumbnails", "ready", "failed"] = "processing_thumbnails"
    duration_seconds: int
    file_size: int


class UploadCancelResponse(BaseModel):
    """Response schema for upload cancellation."""
    message: str = "Upload cancelled"
    upload_id: str


class UploadStatusResponse(BaseModel):
    """Response schema for upload status check."""
    upload_id: str
    status: Literal["active", "completed", "cancelled", "expired"]
    chunks_received: int
    total_chunks: int
    progress_percent: int
    expires_at: Optional[datetime] = None


class UploadError(BaseModel):
    """Generic upload error response."""
    error: str
    error_description: str
