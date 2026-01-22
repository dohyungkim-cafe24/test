"""Authentication schemas for request/response validation."""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class TokenResponse(BaseModel):
    """Response schema for token endpoints."""

    access_token: str
    token_type: str = "Bearer"
    expires_in: int = Field(description="Token expiry in seconds")


class TokenError(BaseModel):
    """Error response for token endpoints."""

    error: str
    error_description: Optional[str] = None


class UserProfile(BaseModel):
    """User profile response schema."""

    id: str
    email: EmailStr
    name: Optional[str] = None
    provider: Literal["kakao", "google"]
    avatar_url: Optional[str] = None
    created_at: datetime
    body_specs: Optional["BodySpecs"] = None


class BodySpecs(BaseModel):
    """User body specifications."""

    height_cm: Optional[int] = Field(None, ge=100, le=250)
    weight_kg: Optional[int] = Field(None, ge=30, le=200)
    experience_level: Optional[Literal["beginner", "intermediate", "advanced", "competitive"]] = None
    stance: Optional[Literal["orthodox", "southpaw"]] = None


class LogoutResponse(BaseModel):
    """Response schema for logout endpoint."""

    message: str = "Logged out successfully"


# Rebuild model to resolve forward references
UserProfile.model_rebuild()
