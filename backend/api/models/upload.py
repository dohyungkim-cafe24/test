"""Upload session database models.

@feature F002 - Video Upload

Maps to upload_sessions and upload_chunks tables as defined in DATA_MODEL.md.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from api.models.user import Base


class UploadSession(Base):
    """Upload session model for tracking chunked uploads.

    Enables resumable uploads (AC-011).
    Sessions expire after 1 hour of inactivity.
    """

    __tablename__ = "upload_sessions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Upload configuration
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    duration_seconds: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    chunk_size: Mapped[int] = mapped_column(Integer, nullable=False, default=5_242_880)  # 5MB

    # Progress tracking
    total_chunks: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    chunks_received: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    bytes_received: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    # Status
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active"
    )  # active, completed, cancelled, expired

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    chunks: Mapped[list["UploadChunk"]] = relationship(
        "UploadChunk", back_populates="session", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_upload_sessions_user", "user_id", "created_at"),
        Index(
            "idx_upload_sessions_expires",
            "expires_at",
            postgresql_where=(status == "active"),
        ),
    )

    def to_dict(self) -> dict:
        """Convert model to dictionary for API response."""
        return {
            "upload_id": str(self.id),
            "status": self.status,
            "chunks_received": self.chunks_received,
            "total_chunks": self.total_chunks,
            "progress_percent": (
                int((self.chunks_received / self.total_chunks) * 100)
                if self.total_chunks > 0
                else 0
            ),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


class UploadChunk(Base):
    """Upload chunk model for tracking individual chunk uploads.

    Enables resumable uploads (AC-011) by tracking which chunks have been received.
    """

    __tablename__ = "upload_chunks"

    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("upload_sessions.id", ondelete="CASCADE"), primary_key=True
    )
    chunk_number: Mapped[int] = mapped_column(SmallInteger, primary_key=True)

    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    md5_hash: Mapped[Optional[str]] = mapped_column(String(32))
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    session: Mapped["UploadSession"] = relationship("UploadSession", back_populates="chunks")


class Video(Base):
    """Video model for storing uploaded video metadata.

    Created after upload completion.
    """

    __tablename__ = "videos"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Metadata
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    # Storage paths (S3 keys)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    thumbnail_key: Mapped[Optional[str]] = mapped_column(String(512))

    # Upload tracking
    upload_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="uploading"
    )  # uploading, processing, ready, failed
    upload_started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    upload_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Video properties (extracted after upload)
    width: Mapped[Optional[int]] = mapped_column(SmallInteger)
    height: Mapped[Optional[int]] = mapped_column(SmallInteger)
    fps: Mapped[Optional[float]] = mapped_column()
    total_frames: Mapped[Optional[int]] = mapped_column(Integer)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("idx_videos_user", "user_id", "created_at"),
        Index(
            "idx_videos_status",
            "upload_status",
            postgresql_where=(deleted_at.is_(None)),
        ),
    )

    def to_dict(self) -> dict:
        """Convert model to dictionary for API response."""
        return {
            "video_id": str(self.id),
            "filename": self.filename,
            "content_type": self.content_type,
            "file_size": self.file_size,
            "duration_seconds": self.duration_seconds,
            "status": self.upload_status,
            "thumbnail_key": self.thumbnail_key,
            "created_at": self.created_at.isoformat(),
        }
