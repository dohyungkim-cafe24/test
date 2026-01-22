"""User database model."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, SmallInteger, DateTime, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class User(Base):
    """User model representing authenticated users.

    Maps to users table as defined in DATA_MODEL.md.
    """

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512))
    provider: Mapped[str] = mapped_column(String(20), nullable=False)
    provider_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Body specs (persisted for returning users)
    height_cm: Mapped[Optional[int]] = mapped_column(SmallInteger)
    weight_kg: Mapped[Optional[int]] = mapped_column(SmallInteger)
    experience_level: Mapped[Optional[str]] = mapped_column(String(20))
    stance: Mapped[Optional[str]] = mapped_column(String(10))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_provider", "provider", "provider_id", unique=True),
    )

    def to_dict(self) -> dict:
        """Convert model to dictionary for API response."""
        return {
            "id": str(self.id),
            "email": self.email,
            "name": self.name,
            "provider": self.provider,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at.isoformat(),
            "body_specs": {
                "height_cm": self.height_cm,
                "weight_kg": self.weight_kg,
                "experience_level": self.experience_level,
                "stance": self.stance,
            }
            if any([self.height_cm, self.weight_kg, self.experience_level, self.stance])
            else None,
        }


class RefreshToken(Base):
    """Refresh token model for session management.

    Maps to refresh_tokens table as defined in DATA_MODEL.md.
    """

    __tablename__ = "refresh_tokens"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Device/session tracking
    user_agent: Mapped[Optional[str]] = mapped_column(String(512))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))  # INET in PG

    __table_args__ = (
        Index("idx_refresh_tokens_user", "user_id"),
        Index(
            "idx_refresh_tokens_expires",
            "expires_at",
            postgresql_where=(revoked_at.is_(None)),
        ),
    )
