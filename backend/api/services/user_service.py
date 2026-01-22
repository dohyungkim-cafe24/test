"""User service for database operations.

Handles user creation, retrieval, and updates.
Addresses M3 from code review: User persistence on OAuth callback.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.user import User


async def get_user_by_provider(
    session: AsyncSession,
    provider: str,
    provider_id: str,
) -> Optional[User]:
    """Get user by OAuth provider and provider_id.

    Args:
        session: Database session.
        provider: OAuth provider name (kakao, google).
        provider_id: Provider-specific user ID.

    Returns:
        User if found, None otherwise.
    """
    result = await session.execute(
        select(User).where(
            User.provider == provider,
            User.provider_id == provider_id,
            User.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def get_user_by_id(
    session: AsyncSession,
    user_id: UUID,
) -> Optional[User]:
    """Get user by ID.

    Args:
        session: Database session.
        user_id: User UUID.

    Returns:
        User if found, None otherwise.
    """
    result = await session.execute(
        select(User).where(
            User.id == user_id,
            User.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def upsert_user(
    session: AsyncSession,
    provider: str,
    provider_id: str,
    email: str,
    name: Optional[str] = None,
    avatar_url: Optional[str] = None,
) -> User:
    """Create or update user from OAuth data.

    Upserts based on provider + provider_id unique constraint.

    Args:
        session: Database session.
        provider: OAuth provider name.
        provider_id: Provider-specific user ID.
        email: User email.
        name: User display name.
        avatar_url: User avatar URL.

    Returns:
        Created or updated User.
    """
    # Check for existing user
    existing = await get_user_by_provider(session, provider, provider_id)

    if existing:
        # Update existing user
        existing.email = email
        if name:
            existing.name = name
        if avatar_url:
            existing.avatar_url = avatar_url
        existing.last_login_at = datetime.now(timezone.utc)
        await session.flush()
        return existing
    else:
        # Create new user
        user = User(
            email=email,
            name=name,
            avatar_url=avatar_url,
            provider=provider,
            provider_id=provider_id,
            last_login_at=datetime.now(timezone.utc),
        )
        session.add(user)
        await session.flush()
        return user
