"""Tests for subject selection functionality.

@feature F003 - Subject Selection

TDD: RED phase - write failing tests first

Acceptance Criteria:
- AC-013: Thumbnail grid displays after upload completes
- AC-014: Tap on person highlights with selection indicator
- AC-015: Confirm selection stores bounding box for tracking
- AC-016: Selection can be changed before confirmation
- AC-017: Single person auto-selected with confirm option
"""
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from pydantic import ValidationError

from api.schemas.subject import (
    BoundingBox,
    DetectedPerson,
    SubjectSelectRequest,
    SubjectSelectResponse,
    ThumbnailResponse,
    ThumbnailsResponse,
)


class TestSubjectSchemas:
    """Test subject selection request/response schemas."""

    def test_bounding_box_valid(self):
        """BoundingBox schema validates coordinates."""
        bbox = BoundingBox(x=120, y=80, width=200, height=400)
        assert bbox.x == 120
        assert bbox.y == 80
        assert bbox.width == 200
        assert bbox.height == 400

    def test_bounding_box_negative_coordinates_rejected(self):
        """BoundingBox rejects negative x/y coordinates."""
        with pytest.raises(ValidationError) as exc_info:
            BoundingBox(x=-10, y=80, width=200, height=400)
        assert "greater than or equal to 0" in str(exc_info.value)

    def test_bounding_box_zero_dimensions_rejected(self):
        """BoundingBox rejects zero width/height."""
        with pytest.raises(ValidationError) as exc_info:
            BoundingBox(x=0, y=0, width=0, height=100)
        assert "greater than 0" in str(exc_info.value)

    def test_detected_person_valid(self):
        """DetectedPerson schema with valid data."""
        person = DetectedPerson(
            person_id="p1",
            bounding_box=BoundingBox(x=120, y=80, width=200, height=400),
            confidence=0.95,
        )
        assert person.person_id == "p1"
        assert person.confidence == 0.95

    def test_detected_person_confidence_range(self):
        """DetectedPerson confidence must be 0-1."""
        with pytest.raises(ValidationError) as exc_info:
            DetectedPerson(
                person_id="p1",
                bounding_box=BoundingBox(x=0, y=0, width=100, height=200),
                confidence=1.5,
            )
        assert "less than or equal to 1" in str(exc_info.value)

    def test_thumbnail_response_valid(self):
        """ThumbnailResponse schema with detected persons."""
        thumbnail = ThumbnailResponse(
            thumbnail_id=str(uuid4()),
            frame_number=0,
            timestamp_seconds=0.0,
            image_url="https://storage.example.com/thumbnails/video1/frame_000.jpg",
            detected_persons=[
                DetectedPerson(
                    person_id="p1",
                    bounding_box=BoundingBox(x=120, y=80, width=200, height=400),
                    confidence=0.95,
                ),
                DetectedPerson(
                    person_id="p2",
                    bounding_box=BoundingBox(x=400, y=100, width=180, height=380),
                    confidence=0.88,
                ),
            ],
        )
        assert len(thumbnail.detected_persons) == 2

    def test_thumbnails_response_valid(self):
        """ThumbnailsResponse with thumbnails and status."""
        response = ThumbnailsResponse(
            video_id=str(uuid4()),
            status="ready",
            total_persons_detected=2,
            thumbnails=[
                ThumbnailResponse(
                    thumbnail_id=str(uuid4()),
                    frame_number=0,
                    timestamp_seconds=0.0,
                    image_url="https://storage.example.com/thumb.jpg",
                    detected_persons=[],
                ),
            ],
            message=None,
        )
        assert response.status == "ready"
        assert response.total_persons_detected == 2

    def test_subject_select_request_valid(self):
        """SubjectSelectRequest with valid selection."""
        request = SubjectSelectRequest(
            thumbnail_id=str(uuid4()),
            person_id="p1",
        )
        assert request.person_id == "p1"

    def test_subject_select_response_valid(self):
        """SubjectSelectResponse includes stored bounding box."""
        response = SubjectSelectResponse(
            subject_id=str(uuid4()),
            video_id=str(uuid4()),
            person_id="p1",
            bounding_box=BoundingBox(x=120, y=80, width=200, height=400),
            auto_selected=False,
        )
        assert response.person_id == "p1"
        assert response.auto_selected is False


class TestSubjectService:
    """Test subject selection service business logic."""

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
    async def test_get_thumbnails_returns_frames(self, mock_db_session):
        """AC-013: Thumbnail grid displays extracted frames after upload."""
        from api.services.subject_service import SubjectService

        service = SubjectService()
        video_id = uuid4()
        user_id = uuid4()

        # Mock video exists with ready status
        mock_video = MagicMock()
        mock_video.id = video_id
        mock_video.user_id = user_id
        mock_video.upload_status = "ready"

        # Mock thumbnails
        mock_thumbnail = MagicMock()
        mock_thumbnail.id = uuid4()
        mock_thumbnail.video_id = video_id
        mock_thumbnail.frame_number = 0
        mock_thumbnail.timestamp_seconds = 0.0
        mock_thumbnail.storage_key = "thumbnails/video1/frame_000.jpg"
        mock_thumbnail.detected_persons = [
            {"person_id": "p1", "bounding_box": {"x": 120, "y": 80, "width": 200, "height": 400}, "confidence": 0.95}
        ]

        with patch.object(service, "_get_video", return_value=mock_video):
            with patch.object(service, "_get_thumbnails", return_value=[mock_thumbnail]):
                with patch.object(service, "_get_image_url", return_value="https://storage.example.com/thumb.jpg"):
                    result = await service.get_thumbnails(
                        session=mock_db_session,
                        video_id=video_id,
                        user_id=user_id,
                    )

        assert result is not None
        assert result["video_id"] == str(video_id)
        assert result["status"] == "ready"
        assert len(result["thumbnails"]) == 1
        assert result["total_persons_detected"] >= 1

    @pytest.mark.asyncio
    async def test_get_thumbnails_processing_state(self, mock_db_session):
        """Thumbnails endpoint returns processing status while extracting."""
        from api.services.subject_service import SubjectService

        service = SubjectService()
        video_id = uuid4()
        user_id = uuid4()

        mock_video = MagicMock()
        mock_video.id = video_id
        mock_video.user_id = user_id
        mock_video.upload_status = "processing_thumbnails"

        with patch.object(service, "_get_video", return_value=mock_video):
            result = await service.get_thumbnails(
                session=mock_db_session,
                video_id=video_id,
                user_id=user_id,
            )

        assert result["status"] == "processing"
        assert result["message"] == "Extracting frames..."

    @pytest.mark.asyncio
    async def test_get_thumbnails_no_persons_detected(self, mock_db_session):
        """No subjects detected returns empty-state message."""
        from api.services.subject_service import SubjectService

        service = SubjectService()
        video_id = uuid4()
        user_id = uuid4()

        mock_video = MagicMock()
        mock_video.id = video_id
        mock_video.user_id = user_id
        mock_video.upload_status = "ready"

        # Mock thumbnails with no detected persons
        mock_thumbnail = MagicMock()
        mock_thumbnail.id = uuid4()
        mock_thumbnail.video_id = video_id
        mock_thumbnail.frame_number = 0
        mock_thumbnail.timestamp_seconds = 0.0
        mock_thumbnail.storage_key = "thumbnails/video1/frame_000.jpg"
        mock_thumbnail.detected_persons = []

        with patch.object(service, "_get_video", return_value=mock_video):
            with patch.object(service, "_get_thumbnails", return_value=[mock_thumbnail]):
                with patch.object(service, "_get_image_url", return_value="https://storage.example.com/thumb.jpg"):
                    result = await service.get_thumbnails(
                        session=mock_db_session,
                        video_id=video_id,
                        user_id=user_id,
                    )

        assert result["status"] == "no_subjects"
        assert result["total_persons_detected"] == 0
        assert "couldn't identify" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_select_subject_stores_bounding_box(self, mock_db_session):
        """AC-015: Confirm selection stores bounding box for tracking."""
        from api.services.subject_service import SubjectService

        service = SubjectService()
        video_id = uuid4()
        user_id = uuid4()
        thumbnail_id = uuid4()

        mock_video = MagicMock()
        mock_video.id = video_id
        mock_video.user_id = user_id

        mock_thumbnail = MagicMock()
        mock_thumbnail.id = thumbnail_id
        mock_thumbnail.video_id = video_id
        mock_thumbnail.detected_persons = [
            {"person_id": "p1", "bounding_box": {"x": 120, "y": 80, "width": 200, "height": 400}, "confidence": 0.95},
            {"person_id": "p2", "bounding_box": {"x": 400, "y": 100, "width": 180, "height": 380}, "confidence": 0.88},
        ]

        with patch.object(service, "_get_video", return_value=mock_video):
            with patch.object(service, "_get_thumbnail", return_value=mock_thumbnail):
                with patch.object(service, "_get_existing_subject", return_value=None):
                    result = await service.select_subject(
                        session=mock_db_session,
                        video_id=video_id,
                        user_id=user_id,
                        thumbnail_id=thumbnail_id,
                        person_id="p1",
                    )

        assert result is not None
        assert result["person_id"] == "p1"
        assert result["bounding_box"]["x"] == 120
        assert result["bounding_box"]["y"] == 80
        assert result["bounding_box"]["width"] == 200
        assert result["bounding_box"]["height"] == 400
        mock_db_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_select_subject_updates_existing_selection(self, mock_db_session):
        """AC-016: Selection can be changed before confirmation."""
        from api.services.subject_service import SubjectService

        service = SubjectService()
        video_id = uuid4()
        user_id = uuid4()
        thumbnail_id = uuid4()
        existing_subject_id = uuid4()

        mock_video = MagicMock()
        mock_video.id = video_id
        mock_video.user_id = user_id

        mock_thumbnail = MagicMock()
        mock_thumbnail.id = thumbnail_id
        mock_thumbnail.video_id = video_id
        mock_thumbnail.detected_persons = [
            {"person_id": "p1", "bounding_box": {"x": 120, "y": 80, "width": 200, "height": 400}, "confidence": 0.95},
            {"person_id": "p2", "bounding_box": {"x": 400, "y": 100, "width": 180, "height": 380}, "confidence": 0.88},
        ]

        # Existing subject selection (changing from p1 to p2)
        mock_existing_subject = MagicMock()
        mock_existing_subject.id = existing_subject_id
        mock_existing_subject.person_id = "p1"

        with patch.object(service, "_get_video", return_value=mock_video):
            with patch.object(service, "_get_thumbnail", return_value=mock_thumbnail):
                with patch.object(service, "_get_existing_subject", return_value=mock_existing_subject):
                    result = await service.select_subject(
                        session=mock_db_session,
                        video_id=video_id,
                        user_id=user_id,
                        thumbnail_id=thumbnail_id,
                        person_id="p2",  # Changed to p2
                    )

        assert result is not None
        assert result["person_id"] == "p2"
        assert result["bounding_box"]["x"] == 400  # p2's bounding box
        # Should update existing, not create new
        mock_db_session.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_single_person_auto_selected(self, mock_db_session):
        """AC-017: Single person auto-selected with confirm option."""
        from api.services.subject_service import SubjectService

        service = SubjectService()
        video_id = uuid4()
        user_id = uuid4()

        mock_video = MagicMock()
        mock_video.id = video_id
        mock_video.user_id = user_id
        mock_video.upload_status = "ready"

        # Only one person detected
        mock_thumbnail = MagicMock()
        mock_thumbnail.id = uuid4()
        mock_thumbnail.video_id = video_id
        mock_thumbnail.frame_number = 0
        mock_thumbnail.timestamp_seconds = 0.0
        mock_thumbnail.storage_key = "thumbnails/video1/frame_000.jpg"
        mock_thumbnail.detected_persons = [
            {"person_id": "p1", "bounding_box": {"x": 120, "y": 80, "width": 200, "height": 400}, "confidence": 0.95}
        ]

        with patch.object(service, "_get_video", return_value=mock_video):
            with patch.object(service, "_get_thumbnails", return_value=[mock_thumbnail]):
                with patch.object(service, "_get_image_url", return_value="https://storage.example.com/thumb.jpg"):
                    result = await service.get_thumbnails(
                        session=mock_db_session,
                        video_id=video_id,
                        user_id=user_id,
                    )

        assert result["total_persons_detected"] == 1
        assert result["auto_select"] is not None
        assert result["auto_select"]["person_id"] == "p1"
        assert result["message"] == "We detected one person. Is this you?"

    @pytest.mark.asyncio
    async def test_select_subject_invalid_person_id(self, mock_db_session):
        """Selecting non-existent person_id returns 404."""
        from api.services.subject_service import SubjectService, PersonNotFoundError

        service = SubjectService()
        video_id = uuid4()
        user_id = uuid4()
        thumbnail_id = uuid4()

        mock_video = MagicMock()
        mock_video.id = video_id
        mock_video.user_id = user_id

        mock_thumbnail = MagicMock()
        mock_thumbnail.id = thumbnail_id
        mock_thumbnail.video_id = video_id
        mock_thumbnail.detected_persons = [
            {"person_id": "p1", "bounding_box": {"x": 120, "y": 80, "width": 200, "height": 400}, "confidence": 0.95}
        ]

        with patch.object(service, "_get_video", return_value=mock_video):
            with patch.object(service, "_get_thumbnail", return_value=mock_thumbnail):
                with pytest.raises(PersonNotFoundError):
                    await service.select_subject(
                        session=mock_db_session,
                        video_id=video_id,
                        user_id=user_id,
                        thumbnail_id=thumbnail_id,
                        person_id="p999",  # Non-existent
                    )


class TestSubjectRouter:
    """Test subject selection API endpoints."""

    @pytest.fixture
    def mock_user(self):
        """Create mock user for auth override."""
        return {"id": str(uuid4()), "email": "test@example.com"}

    @pytest.fixture
    def app(self, mock_user):
        """Create test app with mocked auth dependency."""
        from fastapi import FastAPI
        from api.routers.subject import router
        from api.routers.auth import get_current_user

        app = FastAPI()
        app.include_router(router, prefix="/api/v1")

        async def mock_get_current_user():
            return mock_user

        app.dependency_overrides[get_current_user] = mock_get_current_user
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client with auth."""
        return TestClient(app)

    def test_get_thumbnails_requires_auth(self, mock_user):
        """Thumbnails endpoint requires authentication."""
        from fastapi import FastAPI
        from api.routers.subject import router

        app = FastAPI()
        app.include_router(router, prefix="/api/v1")
        client = TestClient(app)

        video_id = uuid4()
        response = client.get(f"/api/v1/analysis/thumbnails/{video_id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_thumbnails_video_not_found(self, mock_user):
        """Non-existent video returns 404."""
        from fastapi import FastAPI
        from api.routers.subject import router
        from api.routers.auth import get_current_user
        from api.services.subject_service import VideoNotFoundError
        from contextlib import asynccontextmanager

        app = FastAPI()
        app.include_router(router, prefix="/api/v1")

        async def mock_get_current_user():
            return mock_user

        @asynccontextmanager
        async def mock_db_session():
            yield AsyncMock()

        app.dependency_overrides[get_current_user] = mock_get_current_user

        with patch("api.routers.subject.get_db_session", mock_db_session):
            with patch("api.routers.subject.subject_service") as mock_service:
                mock_service.get_thumbnails = AsyncMock(side_effect=VideoNotFoundError("Not found"))
                client = TestClient(app)
                video_id = uuid4()
                response = client.get(f"/api/v1/analysis/thumbnails/{video_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_thumbnails_success(self, mock_user):
        """AC-013: Successful thumbnail retrieval."""
        from fastapi import FastAPI
        from api.routers.subject import router
        from api.routers.auth import get_current_user
        from contextlib import asynccontextmanager

        app = FastAPI()
        app.include_router(router, prefix="/api/v1")

        async def mock_get_current_user():
            return mock_user

        @asynccontextmanager
        async def mock_db_session():
            yield AsyncMock()

        app.dependency_overrides[get_current_user] = mock_get_current_user

        video_id = uuid4()
        thumbnail_id = str(uuid4())

        with patch("api.routers.subject.get_db_session", mock_db_session):
            with patch("api.routers.subject.subject_service") as mock_service:
                mock_service.get_thumbnails = AsyncMock(
                    return_value={
                        "video_id": str(video_id),
                        "status": "ready",
                        "total_persons_detected": 2,
                        "thumbnails": [
                            {
                                "thumbnail_id": thumbnail_id,
                                "frame_number": 0,
                                "timestamp_seconds": 0.0,
                                "image_url": "https://storage.example.com/thumb.jpg",
                                "detected_persons": [
                                    {"person_id": "p1", "bounding_box": {"x": 120, "y": 80, "width": 200, "height": 400}, "confidence": 0.95}
                                ],
                            }
                        ],
                        "auto_select": None,
                        "message": None,
                    }
                )
                client = TestClient(app)
                response = client.get(f"/api/v1/analysis/thumbnails/{video_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["video_id"] == str(video_id)
        assert data["status"] == "ready"
        assert len(data["thumbnails"]) == 1

    def test_select_subject_success(self, mock_user):
        """AC-015: Subject selection stores bounding box."""
        from fastapi import FastAPI
        from api.routers.subject import router
        from api.routers.auth import get_current_user
        from contextlib import asynccontextmanager

        app = FastAPI()
        app.include_router(router, prefix="/api/v1")

        async def mock_get_current_user():
            return mock_user

        @asynccontextmanager
        async def mock_db_session():
            yield AsyncMock()

        app.dependency_overrides[get_current_user] = mock_get_current_user

        video_id = uuid4()
        thumbnail_id = str(uuid4())
        subject_id = str(uuid4())

        with patch("api.routers.subject.get_db_session", mock_db_session):
            with patch("api.routers.subject.subject_service") as mock_service:
                mock_service.select_subject = AsyncMock(
                    return_value={
                        "subject_id": subject_id,
                        "video_id": str(video_id),
                        "person_id": "p1",
                        "bounding_box": {"x": 120, "y": 80, "width": 200, "height": 400},
                        "auto_selected": False,
                    }
                )
                client = TestClient(app)
                response = client.post(
                    f"/api/v1/analysis/subject/{video_id}",
                    json={
                        "thumbnail_id": thumbnail_id,
                        "person_id": "p1",
                    },
                )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["person_id"] == "p1"
        assert data["bounding_box"]["x"] == 120

    def test_select_subject_person_not_found(self, mock_user):
        """Invalid person_id returns 404."""
        from fastapi import FastAPI
        from api.routers.subject import router
        from api.routers.auth import get_current_user
        from api.services.subject_service import PersonNotFoundError
        from contextlib import asynccontextmanager

        app = FastAPI()
        app.include_router(router, prefix="/api/v1")

        async def mock_get_current_user():
            return mock_user

        @asynccontextmanager
        async def mock_db_session():
            yield AsyncMock()

        app.dependency_overrides[get_current_user] = mock_get_current_user

        video_id = uuid4()
        thumbnail_id = str(uuid4())

        with patch("api.routers.subject.get_db_session", mock_db_session):
            with patch("api.routers.subject.subject_service") as mock_service:
                mock_service.select_subject = AsyncMock(
                    side_effect=PersonNotFoundError("Person p999 not found")
                )
                client = TestClient(app)
                response = client.post(
                    f"/api/v1/analysis/subject/{video_id}",
                    json={
                        "thumbnail_id": thumbnail_id,
                        "person_id": "p999",
                    },
                )

        assert response.status_code == status.HTTP_404_NOT_FOUND


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
