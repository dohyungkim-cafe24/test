"""Tests for body specification functionality.

@feature F004 - Body Specification Input

TDD: RED phase - write failing tests first

BDD Scenarios:
- User enters valid body specifications -> saves and navigates to processing
- Height validation: 100-250cm
- Weight validation: 30-200kg
- All fields required for submission
- Body specs pre-filled for returning user (AC-024)
- Invalid number format shows error
"""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from pydantic import ValidationError


class TestBodySpecsSchemas:
    """Test body specs request/response schemas."""

    def test_experience_level_enum_valid(self):
        """ExperienceLevel enum includes all valid values."""
        from api.schemas.body_specs import ExperienceLevel

        assert ExperienceLevel.BEGINNER == "beginner"
        assert ExperienceLevel.INTERMEDIATE == "intermediate"
        assert ExperienceLevel.ADVANCED == "advanced"
        assert ExperienceLevel.COMPETITIVE == "competitive"

    def test_stance_enum_valid(self):
        """Stance enum includes orthodox and southpaw."""
        from api.schemas.body_specs import Stance

        assert Stance.ORTHODOX == "orthodox"
        assert Stance.SOUTHPAW == "southpaw"

    def test_body_specs_create_valid(self):
        """BodySpecsCreate schema with valid data."""
        from api.schemas.body_specs import BodySpecsCreate

        data = BodySpecsCreate(
            height_cm=175,
            weight_kg=70,
            experience_level="intermediate",
            stance="orthodox",
        )
        assert data.height_cm == 175
        assert data.weight_kg == 70
        assert data.experience_level == "intermediate"
        assert data.stance == "orthodox"

    def test_height_below_minimum_rejected(self):
        """Height below 100cm is rejected."""
        from api.schemas.body_specs import BodySpecsCreate

        with pytest.raises(ValidationError) as exc_info:
            BodySpecsCreate(
                height_cm=95,
                weight_kg=70,
                experience_level="intermediate",
                stance="orthodox",
            )
        assert "greater than or equal to 100" in str(exc_info.value).lower()

    def test_height_above_maximum_rejected(self):
        """Height above 250cm is rejected."""
        from api.schemas.body_specs import BodySpecsCreate

        with pytest.raises(ValidationError) as exc_info:
            BodySpecsCreate(
                height_cm=260,
                weight_kg=70,
                experience_level="intermediate",
                stance="orthodox",
            )
        assert "less than or equal to 250" in str(exc_info.value).lower()

    def test_weight_below_minimum_rejected(self):
        """Weight below 30kg is rejected."""
        from api.schemas.body_specs import BodySpecsCreate

        with pytest.raises(ValidationError) as exc_info:
            BodySpecsCreate(
                height_cm=175,
                weight_kg=25,
                experience_level="intermediate",
                stance="orthodox",
            )
        assert "greater than or equal to 30" in str(exc_info.value).lower()

    def test_weight_above_maximum_rejected(self):
        """Weight above 200kg is rejected."""
        from api.schemas.body_specs import BodySpecsCreate

        with pytest.raises(ValidationError) as exc_info:
            BodySpecsCreate(
                height_cm=175,
                weight_kg=210,
                experience_level="intermediate",
                stance="orthodox",
            )
        assert "less than or equal to 200" in str(exc_info.value).lower()

    def test_invalid_experience_level_rejected(self):
        """Invalid experience level is rejected."""
        from api.schemas.body_specs import BodySpecsCreate

        with pytest.raises(ValidationError) as exc_info:
            BodySpecsCreate(
                height_cm=175,
                weight_kg=70,
                experience_level="expert",  # Invalid
                stance="orthodox",
            )
        # Check for enum validation error
        error_str = str(exc_info.value).lower()
        assert "experience_level" in error_str or "input should be" in error_str

    def test_invalid_stance_rejected(self):
        """Invalid stance is rejected."""
        from api.schemas.body_specs import BodySpecsCreate

        with pytest.raises(ValidationError) as exc_info:
            BodySpecsCreate(
                height_cm=175,
                weight_kg=70,
                experience_level="intermediate",
                stance="switch",  # Invalid
            )
        # Check for enum validation error
        error_str = str(exc_info.value).lower()
        assert "stance" in error_str or "input should be" in error_str

    def test_body_specs_response_valid(self):
        """BodySpecsResponse includes all expected fields."""
        from api.schemas.body_specs import BodySpecsResponse

        response = BodySpecsResponse(
            video_id="vid_abc123",
            body_specs_id="bs_ghi789",
            saved=True,
            persist_to_profile=True,
        )
        assert response.video_id == "vid_abc123"
        assert response.body_specs_id == "bs_ghi789"
        assert response.saved is True
        assert response.persist_to_profile is True

    def test_prefill_response_valid(self):
        """PrefillResponse contains user's saved body specs."""
        from api.schemas.body_specs import PrefillResponse

        response = PrefillResponse(
            has_saved_specs=True,
            height_cm=180,
            weight_kg=75,
            experience_level="advanced",
            stance="southpaw",
        )
        assert response.has_saved_specs is True
        assert response.height_cm == 180
        assert response.weight_kg == 75

    def test_prefill_response_no_saved_specs(self):
        """PrefillResponse when user has no saved specs."""
        from api.schemas.body_specs import PrefillResponse

        response = PrefillResponse(has_saved_specs=False)
        assert response.has_saved_specs is False
        assert response.height_cm is None
        assert response.weight_kg is None


class TestBodySpecsService:
    """Test body specs service business logic."""

    @pytest.fixture
    def mock_db_session(self):
        """Create mock database session."""
        session = AsyncMock()
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        session.flush = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_create_body_specs_success(self, mock_db_session):
        """Create body specs with valid data."""
        from api.services.body_specs_service import BodySpecsService

        service = BodySpecsService()
        video_id = uuid4()
        user_id = uuid4()

        # Mock video exists and belongs to user
        mock_video = MagicMock()
        mock_video.id = video_id
        mock_video.user_id = user_id

        # Mock user for persist_to_profile
        mock_user = MagicMock()
        mock_user.id = user_id

        with patch.object(service, "_get_video", return_value=mock_video):
            with patch.object(service, "_get_user", return_value=mock_user):
                with patch.object(service, "_get_existing_specs", return_value=None):
                    result = await service.create_body_specs(
                        session=mock_db_session,
                        user_id=user_id,
                        video_id=video_id,
                        height_cm=175,
                        weight_kg=70,
                        experience_level="intermediate",
                        stance="orthodox",
                    )

        assert result is not None
        assert result["video_id"] == str(video_id)
        assert result["saved"] is True
        assert result["persist_to_profile"] is True
        mock_db_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_body_specs_idor_prevention(self, mock_db_session):
        """IDOR prevention: cannot create specs for another user's video."""
        from api.services.body_specs_service import BodySpecsService, VideoNotFoundError

        service = BodySpecsService()
        video_id = uuid4()
        user_id = uuid4()
        other_user_id = uuid4()

        # Mock video belongs to different user
        mock_video = MagicMock()
        mock_video.id = video_id
        mock_video.user_id = other_user_id  # Different user!

        with patch.object(service, "_get_video", side_effect=VideoNotFoundError("Video not found")):
            with pytest.raises(VideoNotFoundError):
                await service.create_body_specs(
                    session=mock_db_session,
                    user_id=user_id,
                    video_id=video_id,
                    height_cm=175,
                    weight_kg=70,
                    experience_level="intermediate",
                    stance="orthodox",
                )

    @pytest.mark.asyncio
    async def test_create_body_specs_updates_user_profile(self, mock_db_session):
        """Body specs are persisted to user profile (AC-024)."""
        from api.services.body_specs_service import BodySpecsService

        service = BodySpecsService()
        video_id = uuid4()
        user_id = uuid4()

        mock_video = MagicMock()
        mock_video.id = video_id
        mock_video.user_id = user_id

        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.height_cm = None
        mock_user.weight_kg = None
        mock_user.experience_level = None
        mock_user.stance = None

        with patch.object(service, "_get_video", return_value=mock_video):
            with patch.object(service, "_get_user", return_value=mock_user):
                with patch.object(service, "_get_existing_specs", return_value=None):
                    result = await service.create_body_specs(
                        session=mock_db_session,
                        user_id=user_id,
                        video_id=video_id,
                        height_cm=175,
                        weight_kg=70,
                        experience_level="intermediate",
                        stance="orthodox",
                    )

        # Verify user profile was updated
        assert mock_user.height_cm == 175
        assert mock_user.weight_kg == 70
        assert mock_user.experience_level == "intermediate"
        assert mock_user.stance == "orthodox"
        assert result["persist_to_profile"] is True

    @pytest.mark.asyncio
    async def test_get_prefill_returns_saved_specs(self, mock_db_session):
        """Prefill returns user's previously saved body specs (AC-024)."""
        from api.services.body_specs_service import BodySpecsService

        service = BodySpecsService()
        user_id = uuid4()

        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.height_cm = 180
        mock_user.weight_kg = 75
        mock_user.experience_level = "advanced"
        mock_user.stance = "southpaw"

        with patch.object(service, "_get_user", return_value=mock_user):
            result = await service.get_prefill(
                session=mock_db_session,
                user_id=user_id,
            )

        assert result["has_saved_specs"] is True
        assert result["height_cm"] == 180
        assert result["weight_kg"] == 75
        assert result["experience_level"] == "advanced"
        assert result["stance"] == "southpaw"

    @pytest.mark.asyncio
    async def test_get_prefill_no_saved_specs(self, mock_db_session):
        """Prefill returns empty when user has no saved specs."""
        from api.services.body_specs_service import BodySpecsService

        service = BodySpecsService()
        user_id = uuid4()

        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.height_cm = None
        mock_user.weight_kg = None
        mock_user.experience_level = None
        mock_user.stance = None

        with patch.object(service, "_get_user", return_value=mock_user):
            result = await service.get_prefill(
                session=mock_db_session,
                user_id=user_id,
            )

        assert result["has_saved_specs"] is False
        assert result["height_cm"] is None
        assert result["weight_kg"] is None


class TestBodySpecsRouter:
    """Test body specs API endpoints."""

    @pytest.fixture
    def mock_user(self):
        """Create mock user for auth override."""
        return {"id": str(uuid4()), "email": "test@example.com"}

    def test_create_body_specs_requires_auth(self):
        """Body specs endpoint requires authentication."""
        from fastapi import FastAPI
        from api.routers.body_specs import router

        app = FastAPI()
        app.include_router(router, prefix="/api/v1")
        client = TestClient(app)

        video_id = uuid4()
        response = client.post(
            f"/api/v1/analysis/body-specs/{video_id}",
            json={
                "height_cm": 175,
                "weight_kg": 70,
                "experience_level": "intermediate",
                "stance": "orthodox",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_body_specs_success(self, mock_user):
        """Create body specs with valid data returns 201."""
        from fastapi import FastAPI
        from api.routers.body_specs import router
        from api.routers.auth import get_current_user

        app = FastAPI()
        app.include_router(router, prefix="/api/v1")

        async def mock_get_current_user():
            return mock_user

        @asynccontextmanager
        async def mock_db_session():
            yield AsyncMock()

        app.dependency_overrides[get_current_user] = mock_get_current_user

        video_id = uuid4()
        body_specs_id = str(uuid4())

        with patch("api.routers.body_specs.get_db_session", mock_db_session):
            with patch("api.routers.body_specs.body_specs_service") as mock_service:
                mock_service.create_body_specs = AsyncMock(
                    return_value={
                        "video_id": str(video_id),
                        "body_specs_id": body_specs_id,
                        "saved": True,
                        "persist_to_profile": True,
                    }
                )
                client = TestClient(app)
                response = client.post(
                    f"/api/v1/analysis/body-specs/{video_id}",
                    json={
                        "height_cm": 175,
                        "weight_kg": 70,
                        "experience_level": "intermediate",
                        "stance": "orthodox",
                    },
                )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["video_id"] == str(video_id)
        assert data["saved"] is True
        assert data["persist_to_profile"] is True

    def test_create_body_specs_video_not_found(self, mock_user):
        """Non-existent video returns 404."""
        from fastapi import FastAPI
        from api.routers.body_specs import router
        from api.routers.auth import get_current_user
        from api.services.body_specs_service import VideoNotFoundError

        app = FastAPI()
        app.include_router(router, prefix="/api/v1")

        async def mock_get_current_user():
            return mock_user

        @asynccontextmanager
        async def mock_db_session():
            yield AsyncMock()

        app.dependency_overrides[get_current_user] = mock_get_current_user

        video_id = uuid4()

        with patch("api.routers.body_specs.get_db_session", mock_db_session):
            with patch("api.routers.body_specs.body_specs_service") as mock_service:
                mock_service.create_body_specs = AsyncMock(
                    side_effect=VideoNotFoundError("Video not found")
                )
                client = TestClient(app)
                response = client.post(
                    f"/api/v1/analysis/body-specs/{video_id}",
                    json={
                        "height_cm": 175,
                        "weight_kg": 70,
                        "experience_level": "intermediate",
                        "stance": "orthodox",
                    },
                )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_body_specs_invalid_height(self, mock_user):
        """Invalid height returns 422."""
        from fastapi import FastAPI
        from api.routers.body_specs import router
        from api.routers.auth import get_current_user

        app = FastAPI()
        app.include_router(router, prefix="/api/v1")

        async def mock_get_current_user():
            return mock_user

        app.dependency_overrides[get_current_user] = mock_get_current_user

        client = TestClient(app)
        video_id = uuid4()

        response = client.post(
            f"/api/v1/analysis/body-specs/{video_id}",
            json={
                "height_cm": 95,  # Below minimum
                "weight_kg": 70,
                "experience_level": "intermediate",
                "stance": "orthodox",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_body_specs_invalid_weight(self, mock_user):
        """Invalid weight returns 422."""
        from fastapi import FastAPI
        from api.routers.body_specs import router
        from api.routers.auth import get_current_user

        app = FastAPI()
        app.include_router(router, prefix="/api/v1")

        async def mock_get_current_user():
            return mock_user

        app.dependency_overrides[get_current_user] = mock_get_current_user

        client = TestClient(app)
        video_id = uuid4()

        response = client.post(
            f"/api/v1/analysis/body-specs/{video_id}",
            json={
                "height_cm": 175,
                "weight_kg": 210,  # Above maximum
                "experience_level": "intermediate",
                "stance": "orthodox",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_prefill_success(self, mock_user):
        """Get prefill returns user's saved specs."""
        from fastapi import FastAPI
        from api.routers.body_specs import router
        from api.routers.auth import get_current_user

        app = FastAPI()
        app.include_router(router, prefix="/api/v1")

        async def mock_get_current_user():
            return mock_user

        @asynccontextmanager
        async def mock_db_session():
            yield AsyncMock()

        app.dependency_overrides[get_current_user] = mock_get_current_user

        with patch("api.routers.body_specs.get_db_session", mock_db_session):
            with patch("api.routers.body_specs.body_specs_service") as mock_service:
                mock_service.get_prefill = AsyncMock(
                    return_value={
                        "has_saved_specs": True,
                        "height_cm": 180,
                        "weight_kg": 75,
                        "experience_level": "advanced",
                        "stance": "southpaw",
                    }
                )
                client = TestClient(app)
                response = client.get("/api/v1/analysis/body-specs/prefill")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["has_saved_specs"] is True
        assert data["height_cm"] == 180

    def test_get_prefill_requires_auth(self):
        """Prefill endpoint requires authentication."""
        from fastapi import FastAPI
        from api.routers.body_specs import router

        app = FastAPI()
        app.include_router(router, prefix="/api/v1")
        client = TestClient(app)

        response = client.get("/api/v1/analysis/body-specs/prefill")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
