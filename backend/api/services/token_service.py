"""Token service for refresh token database operations.

Addresses B2/M2 from code review: Refresh token storage and validation.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.user import RefreshToken, User


async def create_refresh_token(
    session: AsyncSession,
    user_id: UUID,
    token_hash: str,
    expires_at: datetime,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> RefreshToken:
    """Create and store a refresh token.

    Args:
        session: Database session.
        user_id: User UUID.
        token_hash: SHA-256 hash of the raw token.
        expires_at: Token expiration datetime.
        user_agent: Client user agent string.
        ip_address: Client IP address.

    Returns:
        Created RefreshToken.
    """
    token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    session.add(token)
    await session.flush()
    return token


async def validate_refresh_token(
    session: AsyncSession,
    token_hash: str,
) -> Optional[tuple[RefreshToken, User]]:
    """Validate a refresh token and get associated user.

    Args:
        session: Database session.
        token_hash: SHA-256 hash of the raw token.

    Returns:
        Tuple of (RefreshToken, User) if valid, None otherwise.
    """
    # Find token that is not expired and not revoked
    now = datetime.now(timezone.utc)
    result = await session.execute(
        select(RefreshToken, User)
        .join(User, RefreshToken.user_id == User.id)
        .where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.expires_at > now,
            RefreshToken.revoked_at.is_(None),
            User.deleted_at.is_(None),
        )
    )
    row = result.first()
    if row:
        return row[0], row[1]
    return None


async def revoke_refresh_token(
    session: AsyncSession,
    token_hash: str,
) -> bool:
    """Revoke a refresh token.

    Args:
        session: Database session.
        token_hash: SHA-256 hash of the raw token.

    Returns:
        True if token was revoked, False if not found.
    """
    result = await session.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
        )
    )
    token = result.scalar_one_or_none()

    if token:
        token.revoked_at = datetime.now(timezone.utc)
        await session.flush()
        return True
    return False


async def revoke_user_tokens(
    session: AsyncSession,
    user_id: UUID,
) -> int:
    """Revoke all refresh tokens for a user.

    Args:
        session: Database session.
        user_id: User UUID.

    Returns:
        Number of tokens revoked.
    """
    now = datetime.now(timezone.utc)
    result = await session.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
    )
    tokens = result.scalars().all()

    for token in tokens:
        token.revoked_at = now

    await session.flush()
    return len(tokens)


async def cleanup_expired_tokens(
    session: AsyncSession,
    older_than_days: int = 30,
) -> int:
    """Delete expired tokens older than specified days.

    Args:
        session: Database session.
        older_than_days: Delete tokens expired more than this many days ago.

    Returns:
        Number of tokens deleted.
    """
    from datetime import timedelta
    from sqlalchemy import delete

    cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
    result = await session.execute(
        delete(RefreshToken).where(RefreshToken.expires_at < cutoff)
    )
    return result.rowcount
