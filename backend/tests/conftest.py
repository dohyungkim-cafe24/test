"""Test configuration and fixtures for authentication tests."""
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

# Set test environment variables before importing app
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-do-not-use-in-production")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("KAKAO_CLIENT_ID", "test-kakao-client-id")
os.environ.setdefault("KAKAO_CLIENT_SECRET", "test-kakao-secret")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-google-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-google-secret")
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")


# Mock classes for testing
class MockUser:
    """Mock user object for testing."""
    def __init__(self, user_id=None, email="test@example.com", name="Test User"):
        self.id = user_id or uuid4()
        self.email = email
        self.name = name
        self.avatar_url = None
        self.provider = "kakao"
        self.provider_id = "12345678"
        self.created_at = datetime.now(timezone.utc)
        self.last_login_at = datetime.now(timezone.utc)
        self.height_cm = None
        self.weight_kg = None
        self.experience_level = None
        self.stance = None

    def to_dict(self):
        return {
            "id": str(self.id),
            "email": self.email,
            "name": self.name,
            "provider": self.provider,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at.isoformat(),
            "body_specs": None,
        }


class MockRefreshToken:
    """Mock refresh token for testing."""
    def __init__(self, user_id, token_hash):
        self.id = uuid4()
        self.user_id = user_id
        self.token_hash = token_hash
        self.expires_at = datetime.now(timezone.utc)
        self.created_at = datetime.now(timezone.utc)
        self.revoked_at = None


# Store for test state (simulating in-memory store)
_test_state_store: dict = {}
_test_user_store: dict = {}
_test_token_store: dict = {}


@pytest.fixture(autouse=True)
def reset_test_stores():
    """Reset test stores before each test."""
    global _test_state_store, _test_user_store, _test_token_store
    _test_state_store = {}
    _test_user_store = {}
    _test_token_store = {}
    yield


@pytest.fixture
def app() -> FastAPI:
    """Create test application instance with mocked services."""
    # Import here to avoid circular imports
    from api.main import create_app

    # Mock database session
    @asynccontextmanager
    async def mock_db_session():
        mock_session = AsyncMock()
        yield mock_session

    # Mock state store functions
    async def mock_store_state(redirect_path=None, ttl_seconds=600):
        import secrets
        token = secrets.token_urlsafe(32)
        _test_state_store[token] = redirect_path
        if redirect_path:
            return f"{token}|{redirect_path}"
        return token

    async def mock_validate_state(state):
        if not state:
            return False, None
        parts = state.split("|", 1)
        token = parts[0]
        redirect_from_state = parts[1] if len(parts) > 1 else None

        if token in _test_state_store:
            stored = _test_state_store.pop(token)
            return True, redirect_from_state or stored
        # For testing: accept "valid-state" as always valid
        if token == "valid-state":
            return True, redirect_from_state
        return False, None

    # Mock user service
    async def mock_upsert_user(session, provider, provider_id, email, name=None, avatar_url=None):
        user = MockUser(email=email, name=name)
        user.provider = provider
        user.provider_id = provider_id
        user.avatar_url = avatar_url
        _test_user_store[str(user.id)] = user
        return user

    async def mock_get_user_by_id(session, user_id):
        return _test_user_store.get(str(user_id))

    # Mock token service
    async def mock_create_refresh_token(session, user_id, token_hash, expires_at, user_agent=None, ip_address=None):
        token = MockRefreshToken(user_id, token_hash)
        _test_token_store[token_hash] = (token, _test_user_store.get(str(user_id)))
        return token

    async def mock_validate_refresh_token(session, token_hash):
        return _test_token_store.get(token_hash)

    async def mock_revoke_refresh_token(session, token_hash):
        if token_hash in _test_token_store:
            del _test_token_store[token_hash]
            return True
        return False

    # Apply patches
    with patch("api.services.database.get_db_session", mock_db_session), \
         patch("api.services.state_store.store_state", mock_store_state), \
         patch("api.services.state_store.validate_state", mock_validate_state), \
         patch("api.services.user_service.upsert_user", mock_upsert_user), \
         patch("api.services.user_service.get_user_by_id", mock_get_user_by_id), \
         patch("api.services.token_service.create_refresh_token", mock_create_refresh_token), \
         patch("api.services.token_service.validate_refresh_token", mock_validate_refresh_token), \
         patch("api.services.token_service.revoke_refresh_token", mock_revoke_refresh_token), \
         patch("api.services.database.init_db", AsyncMock()), \
         patch("api.services.database.close_db", AsyncMock()), \
         patch("api.services.state_store.close_redis", AsyncMock()):

        app = create_app()
        yield app


@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    """Create synchronous test client."""
    with TestClient(app, follow_redirects=False) as c:
        yield c


@pytest.fixture
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def mock_kakao_oauth_response() -> dict:
    """Mock successful Kakao OAuth token response."""
    return {
        "access_token": "kakao-access-token-123",
        "token_type": "bearer",
        "refresh_token": "kakao-refresh-token-456",
        "expires_in": 21599,
        "scope": "account_email profile_nickname profile_image",
        "refresh_token_expires_in": 5183999,
    }


@pytest.fixture
def mock_kakao_user_response() -> dict:
    """Mock Kakao user profile response."""
    return {
        "id": 12345678,
        "kakao_account": {
            "email": "boxer@kakao.com",
            "profile": {
                "nickname": "Kim Boxer",
                "thumbnail_image_url": "https://k.kakaocdn.net/thumb/123.jpg",
            },
        },
    }


@pytest.fixture
def mock_google_oauth_response() -> dict:
    """Mock successful Google OAuth token response."""
    return {
        "access_token": "google-access-token-789",
        "token_type": "Bearer",
        "expires_in": 3599,
        "refresh_token": "google-refresh-token-abc",
        "scope": "openid email profile",
        "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    }


@pytest.fixture
def mock_google_user_response() -> dict:
    """Mock Google user info response."""
    return {
        "sub": "109876543210",
        "email": "boxer@gmail.com",
        "email_verified": True,
        "name": "Lee Boxer",
        "picture": "https://lh3.googleusercontent.com/a/photo.jpg",
        "given_name": "Lee",
        "family_name": "Boxer",
    }
