"""Stamp database model for detected actions.

@feature F006 - Stamp Generation

Maps to stamps table as defined in DATA_MODEL.md.

Acceptance Criteria:
- AC-030: Strikes detected by arm velocity and trajectory patterns
- AC-031: Defensive actions detected by torso and arm positioning
- AC-032: Each action timestamped with frame number and confidence
- AC-033: Stamps stored with type, timestamp, side, and confidence
"""
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import JSON

from api.models.user import Base


class ActionType(str, Enum):
    """Action type enumeration for stamps.

    Strikes (AC-030):
    - jab: Quick, straight punch with lead hand
    - straight: Power punch with rear hand
    - hook: Curved punch targeting sides
    - uppercut: Upward punch targeting chin

    Defense (AC-031):
    - guard_up: Hands raised to protect head
    - guard_down: Hands lowered (vulnerable position)
    - slip: Lateral head/torso movement
    - duck: Lowering head to avoid strikes
    - bob_weave: Combined lateral and vertical movement
    """

    # Strikes
    JAB = "jab"
    STRAIGHT = "straight"
    HOOK = "hook"
    UPPERCUT = "uppercut"

    # Defense
    GUARD_UP = "guard_up"
    GUARD_DOWN = "guard_down"
    SLIP = "slip"
    DUCK = "duck"
    BOB_WEAVE = "bob_weave"

    def is_strike(self) -> bool:
        """Check if this action type is a strike."""
        return self in {
            ActionType.JAB,
            ActionType.STRAIGHT,
            ActionType.HOOK,
            ActionType.UPPERCUT,
        }

    def is_defense(self) -> bool:
        """Check if this action type is a defensive action."""
        return self in {
            ActionType.GUARD_UP,
            ActionType.GUARD_DOWN,
            ActionType.SLIP,
            ActionType.DUCK,
            ActionType.BOB_WEAVE,
        }


class Side(str, Enum):
    """Side enumeration for body side of action.

    AC-033: Stamps stored with type, timestamp, side, and confidence
    """

    LEFT = "left"
    RIGHT = "right"
    BOTH = "both"


class Stamp(Base):
    """Stamp model for detected key moments.

    AC-032: Each action timestamped with frame number and confidence
    AC-033: Stamps stored with type, timestamp, side, and confidence

    Stores detected strikes and defensive actions with timing and confidence.
    """

    __tablename__ = "stamps"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    analysis_id: Mapped[UUID] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False
    )

    # Timing (AC-032)
    timestamp_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    frame_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Action classification (AC-030, AC-031, AC-033)
    _action_type: Mapped[str] = mapped_column(
        "action_type", String(30), nullable=False
    )
    _side: Mapped[str] = mapped_column("side", String(10), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    # Detection details (for debugging/improvement)
    velocity_vector: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    trajectory_data: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Visual reference
    thumbnail_key: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    @property
    def action_type(self) -> ActionType:
        """Get action_type as enum."""
        return ActionType(self._action_type) if self._action_type else None

    @action_type.setter
    def action_type(self, value: ActionType | str) -> None:
        """Set action_type from enum or string."""
        if isinstance(value, ActionType):
            self._action_type = value.value
        else:
            self._action_type = value

    @property
    def side(self) -> Side:
        """Get side as enum."""
        return Side(self._side) if self._side else None

    @side.setter
    def side(self, value: Side | str) -> None:
        """Set side from enum or string."""
        if isinstance(value, Side):
            self._side = value.value
        else:
            self._side = value

    __table_args__ = (
        Index("idx_stamps_analysis", "analysis_id", "timestamp_seconds"),
        Index("idx_stamps_type", "action_type"),
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary for API response.

        AC-033: Stamps stored with type, timestamp, side, and confidence
        """
        return {
            "id": str(self.id),
            "analysis_id": str(self.analysis_id),
            "timestamp_seconds": self.timestamp_seconds,
            "frame_number": self.frame_number,
            "action_type": self._action_type,
            "side": self._side,
            "confidence": self.confidence,
            "velocity_vector": self.velocity_vector,
            "trajectory_data": self.trajectory_data,
            "thumbnail_key": self.thumbnail_key,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
