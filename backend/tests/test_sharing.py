"""Test suite for report sharing endpoints.

@feature F009 - Report Sharing

Acceptance Criteria:
- AC-049: Share button shows on report page (default private)
- AC-050: Enable sharing generates unique URL
- AC-051: Shared URL accessible without authentication
- AC-052: Copy Link copies to clipboard with confirmation
- AC-053: Shared report shows social preview cards
- AC-054: Disabling sharing invalidates the URL
- AC-055: Re-enabling generates new unique URL
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import status


# Test fixtures
@pytest.fixture
def mock_report_owner_id():
    """UUID for report owner."""
    return str(uuid4())


@pytest.fixture
def mock_report_id():
    """UUID for report."""
    return str(uuid4())


@pytest.fixture
def mock_share_token():
    """8-character share token."""
    return "abc12345"


class TestEnableSharingEndpoint:
    """Tests for POST /api/v1/reports/{report_id}/share endpoint.

    AC-050: Enable sharing generates unique URL
    """

    @pytest.mark.asyncio
    async def test_enable_sharing_success(
        self, client, mock_report_id, mock_report_owner_id, mock_share_token
    ):
        """Test successful enabling of sharing generates 8-char token.

        BDD: User enables sharing and gets unique URL
        """
        with patch(
            "api.services.sharing_service.sharing_service.enable_sharing"
        ) as mock_enable:
            mock_enable.return_value = {
                "share_enabled": True,
                "share_token": mock_share_token,
                "share_url": f"http://localhost:3000/shared/{mock_share_token}",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            with patch(
                "api.routers.auth.get_current_user",
                return_value={"id": mock_report_owner_id, "email": "test@example.com"},
            ):
                response = client.post(
                    f"/api/v1/reports/{mock_report_id}/share",
                    headers={"Authorization": "Bearer test-token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # AC-050: Generates unique URL with 8-char hash
        assert data["share_enabled"] is True
        assert "share_token" in data
        assert len(data["share_token"]) == 8
        assert "share_url" in data
        assert mock_share_token in data["share_url"]

    @pytest.mark.asyncio
    async def test_enable_sharing_not_owner(self, client, mock_report_id):
        """Test 403 when non-owner tries to enable sharing."""
        from api.services.sharing_service import ShareOwnershipError

        with patch(
            "api.services.sharing_service.sharing_service.enable_sharing"
        ) as mock_enable:
            mock_enable.side_effect = ShareOwnershipError("Not authorized")

            with patch(
                "api.routers.auth.get_current_user",
                return_value={"id": str(uuid4()), "email": "other@example.com"},
            ):
                response = client.post(
                    f"/api/v1/reports/{mock_report_id}/share",
                    headers={"Authorization": "Bearer test-token"},
                )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_enable_sharing_report_not_found(self, client):
        """Test 404 when report doesn't exist."""
        from api.services.sharing_service import ShareReportNotFoundError

        fake_report_id = str(uuid4())

        with patch(
            "api.services.sharing_service.sharing_service.enable_sharing"
        ) as mock_enable:
            mock_enable.side_effect = ShareReportNotFoundError("Report not found")

            with patch(
                "api.routers.auth.get_current_user",
                return_value={"id": str(uuid4()), "email": "test@example.com"},
            ):
                response = client.post(
                    f"/api/v1/reports/{fake_report_id}/share",
                    headers={"Authorization": "Bearer test-token"},
                )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDisableSharingEndpoint:
    """Tests for DELETE /api/v1/reports/{report_id}/share endpoint.

    AC-054: Disabling sharing invalidates the URL
    """

    @pytest.mark.asyncio
    async def test_disable_sharing_success(
        self, client, mock_report_id, mock_report_owner_id
    ):
        """Test successful disabling of sharing.

        BDD: User disables sharing
        """
        with patch(
            "api.services.sharing_service.sharing_service.disable_sharing"
        ) as mock_disable:
            mock_disable.return_value = {
                "share_enabled": False,
                "message": "Sharing disabled",
            }

            with patch(
                "api.routers.auth.get_current_user",
                return_value={"id": mock_report_owner_id, "email": "test@example.com"},
            ):
                response = client.delete(
                    f"/api/v1/reports/{mock_report_id}/share",
                    headers={"Authorization": "Bearer test-token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["share_enabled"] is False


class TestGetSharedReportEndpoint:
    """Tests for GET /api/v1/shared/{share_token} endpoint.

    AC-051: Shared URL accessible without authentication
    """

    @pytest.mark.asyncio
    async def test_get_shared_report_success(
        self, client, mock_share_token
    ):
        """Test accessing shared report without authentication.

        BDD: Shared report accessible without login
        """
        mock_report = {
            "id": str(uuid4()),
            "performance_score": 75,
            "overall_assessment": "Good technique",
            "strengths": [{"title": "Jab", "description": "Fast jab"}],
            "weaknesses": [{"title": "Guard", "description": "Slow recovery"}],
            "recommendations": [{"title": "Practice", "description": "Drill more", "priority": "high"}],
            "metrics": {},
            "stamps": [],
            "disclaimer": "AI analysis for training purposes only.",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        with patch(
            "api.services.sharing_service.sharing_service.get_shared_report"
        ) as mock_get:
            mock_get.return_value = mock_report

            # NO authentication header - public access
            response = client.get(f"/api/v1/shared/{mock_share_token}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # AC-051: Report content accessible
        assert "performance_score" in data
        assert "overall_assessment" in data
        assert "disclaimer" in data  # AI disclaimer visible

    @pytest.mark.asyncio
    async def test_get_shared_report_disabled(self, client, mock_share_token):
        """Test 403 when accessing disabled share link.

        BDD: Disabled share link returns error
        """
        from api.services.sharing_service import ShareDisabledError

        with patch(
            "api.services.sharing_service.sharing_service.get_shared_report"
        ) as mock_get:
            mock_get.side_effect = ShareDisabledError("Sharing disabled")

            response = client.get(f"/api/v1/shared/{mock_share_token}")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "disabled" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_shared_report_not_found(self, client):
        """Test 404 when share token doesn't exist."""
        from api.services.sharing_service import ShareNotFoundError

        with patch(
            "api.services.sharing_service.sharing_service.get_shared_report"
        ) as mock_get:
            mock_get.side_effect = ShareNotFoundError("Share link not found")

            response = client.get("/api/v1/shared/invalid1")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetShareStatusEndpoint:
    """Tests for GET /api/v1/reports/{report_id}/share endpoint.

    AC-049: Share button shows on report page (default private)
    """

    @pytest.mark.asyncio
    async def test_get_share_status_not_shared(
        self, client, mock_report_id, mock_report_owner_id
    ):
        """Test getting share status when report is not shared (default private).

        BDD: Report shows share button in private state
        """
        with patch(
            "api.services.sharing_service.sharing_service.get_share_status"
        ) as mock_status:
            mock_status.return_value = {
                "share_enabled": False,
                "share_token": None,
                "share_url": None,
            }

            with patch(
                "api.routers.auth.get_current_user",
                return_value={"id": mock_report_owner_id, "email": "test@example.com"},
            ):
                response = client.get(
                    f"/api/v1/reports/{mock_report_id}/share",
                    headers={"Authorization": "Bearer test-token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # AC-049: Default private state
        assert data["share_enabled"] is False
        assert data["share_token"] is None

    @pytest.mark.asyncio
    async def test_get_share_status_shared(
        self, client, mock_report_id, mock_report_owner_id, mock_share_token
    ):
        """Test getting share status when sharing is enabled."""
        with patch(
            "api.services.sharing_service.sharing_service.get_share_status"
        ) as mock_status:
            mock_status.return_value = {
                "share_enabled": True,
                "share_token": mock_share_token,
                "share_url": f"http://localhost:3000/shared/{mock_share_token}",
            }

            with patch(
                "api.routers.auth.get_current_user",
                return_value={"id": mock_report_owner_id, "email": "test@example.com"},
            ):
                response = client.get(
                    f"/api/v1/reports/{mock_report_id}/share",
                    headers={"Authorization": "Bearer test-token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["share_enabled"] is True
        assert data["share_token"] == mock_share_token


class TestReEnableSharingGeneratesNewToken:
    """Tests for re-enabling sharing behavior.

    AC-055: Re-enabling generates new unique URL
    """

    @pytest.mark.asyncio
    async def test_re_enable_sharing_new_token(
        self, client, mock_report_id, mock_report_owner_id
    ):
        """Test that re-enabling sharing generates a new unique token.

        BDD: User re-enables sharing gets new URL
        """
        new_token = "newtoken1"

        with patch(
            "api.services.sharing_service.sharing_service.enable_sharing"
        ) as mock_enable:
            mock_enable.return_value = {
                "share_enabled": True,
                "share_token": new_token,
                "share_url": f"http://localhost:3000/shared/{new_token}",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            with patch(
                "api.routers.auth.get_current_user",
                return_value={"id": mock_report_owner_id, "email": "test@example.com"},
            ):
                response = client.post(
                    f"/api/v1/reports/{mock_report_id}/share",
                    headers={"Authorization": "Bearer test-token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # AC-055: New unique URL
        assert data["share_token"] == new_token
        assert len(data["share_token"]) == 8


class TestSharingService:
    """Tests for sharing service business logic."""

    @pytest.mark.asyncio
    async def test_generate_share_token_is_8_chars(self):
        """Test that generated share tokens are 8 characters."""
        from api.services.sharing_service import SharingService

        service = SharingService()
        token = service._generate_share_token()

        assert len(token) == 8
        # Should be alphanumeric
        assert token.isalnum()

    @pytest.mark.asyncio
    async def test_generate_share_token_unique(self):
        """Test that generated tokens are unique."""
        from api.services.sharing_service import SharingService

        service = SharingService()
        tokens = {service._generate_share_token() for _ in range(100)}

        # All tokens should be unique
        assert len(tokens) == 100
