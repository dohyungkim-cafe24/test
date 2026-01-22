"""Body specifications database model.

@feature F004 - Body Specification Input

Maps to body_specs table as defined in DATA_MODEL.md.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, SmallInteger, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from api.models.user import Base


class BodySpecs(Base):
    """Body specifications model for storing user physical attributes.

    Used to contextualize analysis to user's body type and experience level.
    Records are created per-video but also persisted to user profile (persist_to_profile).
    """

    __tablename__ = "body_specs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    video_id: Mapped[UUID] = mapped_column(
        ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=False
    )

    # Physical attributes
    height_cm: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    weight_kg: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    # Experience/stance
    experience_level: Mapped[str] = mapped_column(String(20), nullable=False)
    stance: Mapped[str] = mapped_column(String(10), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        CheckConstraint("height_cm BETWEEN 100 AND 250", name="chk_height"),
        CheckConstraint("weight_kg BETWEEN 30 AND 200", name="chk_weight"),
        CheckConstraint(
            "experience_level IN ('beginner', 'intermediate', 'advanced', 'competitive')",
            name="chk_experience"
        ),
        CheckConstraint(
            "stance IN ('orthodox', 'southpaw')",
            name="chk_stance"
        ),
        Index("idx_body_specs_video", "video_id", unique=True),
        Index("idx_body_specs_user", "user_id", "created_at"),
    )

    def to_dict(self) -> dict:
        """Convert model to dictionary for API response."""
        return {
            "body_specs_id": str(self.id),
            "video_id": str(self.video_id),
            "height_cm": self.height_cm,
            "weight_kg": self.weight_kg,
            "experience_level": self.experience_level,
            "stance": self.stance,
            "created_at": self.created_at.isoformat(),
        }
