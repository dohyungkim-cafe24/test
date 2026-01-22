"""State storage for CSRF tokens using Redis or in-memory fallback.

This module provides server-side state validation for OAuth flows,
addressing the CSRF protection requirement (B1 from code review).
"""
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import redis.asyncio as redis

from api.config import get_settings

# In-memory fallback for development/testing
_memory_store: dict[str, tuple[datetime, Optional[str]]] = {}

# Global Redis client
_redis_client: Optional[redis.Redis] = None


async def get_redis() -> Optional[redis.Redis]:
    """Get or create Redis client.

    Returns None if Redis is unavailable (falls back to memory store).
    """
    global _redis_client
    settings = get_settings()

    if _redis_client is None:
        try:
            _redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
            )
            # Test connection
            await _redis_client.ping()
        except Exception:
            _redis_client = None

    return _redis_client


async def close_redis():
    """Close Redis connection."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


async def store_state(redirect_path: Optional[str] = None, ttl_seconds: int = 600) -> str:
    """Generate and store a CSRF state token.

    Args:
        redirect_path: Optional post-auth redirect path.
        ttl_seconds: Time-to-live for the state token (default 10 minutes).

    Returns:
        State token string (optionally with redirect path appended).
    """
    csrf_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)

    redis_client = await get_redis()

    if redis_client:
        # Store in Redis
        key = f"oauth_state:{csrf_token}"
        value = redirect_path or ""
        await redis_client.setex(key, ttl_seconds, value)
    else:
        # Fallback to memory store (development only)
        _memory_store[csrf_token] = (expires_at, redirect_path)
        # Clean up expired tokens
        _cleanup_expired()

    # Return state with optional redirect path
    if redirect_path:
        return f"{csrf_token}|{redirect_path}"
    return csrf_token


async def validate_state(state: str) -> tuple[bool, Optional[str]]:
    """Validate and consume a CSRF state token.

    Args:
        state: The state string from OAuth callback.

    Returns:
        Tuple of (is_valid, redirect_path or None).
    """
    if not state:
        return False, None

    # Parse state to extract token and redirect
    parts = state.split("|", 1)
    csrf_token = parts[0]
    redirect_from_state = parts[1] if len(parts) > 1 else None

    redis_client = await get_redis()

    if redis_client:
        # Validate from Redis (atomic get and delete)
        key = f"oauth_state:{csrf_token}"
        stored_redirect = await redis_client.getdel(key)

        if stored_redirect is None:
            return False, None

        # Use redirect from state or stored value
        redirect_path = redirect_from_state or (stored_redirect if stored_redirect else None)
        return True, redirect_path
    else:
        # Fallback to memory store
        _cleanup_expired()

        if csrf_token not in _memory_store:
            return False, None

        expires_at, stored_redirect = _memory_store.pop(csrf_token)

        if datetime.now(timezone.utc) > expires_at:
            return False, None

        redirect_path = redirect_from_state or stored_redirect
        return True, redirect_path


def _cleanup_expired():
    """Remove expired tokens from memory store."""
    now = datetime.now(timezone.utc)
    expired = [k for k, (exp, _) in _memory_store.items() if exp < now]
    for k in expired:
        _memory_store.pop(k, None)
