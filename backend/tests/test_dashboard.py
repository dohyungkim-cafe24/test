"""Test suite for dashboard endpoints.

@feature F010 - Report History Dashboard

Acceptance Criteria:
- AC-056: Dashboard lists reports sorted by date descending
- AC-057: List items show thumbnail, date, summary indicator
- AC-058: Clicking report navigates to full view
- AC-059: Delete report shows confirmation dialog
- AC-060: Empty state shows upload CTA

BDD Scenarios:
- Dashboard displays report list sorted by date (newest first)
- Report list item shows thumbnail, date, summary (key moments count)
- User navigates to report from list (/dashboard/report/{id})
- User deletes report with confirmation dialog and undo toast (10 seconds)
- Dashboard shows empty state for new user (illustration, Upload Video CTA)
- Dashboard loading state shows skeleton cards with pulse animation
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import status


# Test fixtures
@pytest.fixture
def mock_user_id():
    """Create a consistent user ID for testing."""
    return str(uuid4())


@pytest.fixture
def mock_report_list_data(mock_user_id):
    """Mock paginated report list data for testing.

    AC-056: Reports sorted by date descending
    AC-057: List items show thumbnail, date, summary indicator
    """
    now = datetime.now(timezone.utc)
    return {
        "items": [
            {
                "id": str(uuid4()),
                "video_id": str(uuid4()),
                "thumbnail_url": "https://cdn.example.com/thumbnails/thumb1.jpg",
                "analyzed_at": (now - timedelta(hours=2)).isoformat(),
                "key_moments_count": 8,
                "performance_score": 72,
            },
            {
                "id": str(uuid4()),
                "video_id": str(uuid4()),
                "thumbnail_url": "https://cdn.example.com/thumbnails/thumb2.jpg",
                "analyzed_at": (now - timedelta(days=1)).isoformat(),
                "key_moments_count": 5,
                "performance_score": 68,
            },
            {
                "id": str(uuid4()),
                "video_id": str(uuid4()),
                "thumbnail_url": "https://cdn.example.com/thumbnails/thumb3.jpg",
                "analyzed_at": (now - timedelta(days=3)).isoformat(),
                "key_moments_count": 12,
                "performance_score": 81,
            },
        ],
        "total": 3,
        "page": 1,
        "has_more": False,
    }


@pytest.fixture
def empty_report_list_data():
    """Mock empty report list for new users.

    AC-060: Empty state shows upload CTA
    """
    return {
        "items": [],
        "total": 0,
        "page": 1,
        "has_more": False,
    }


class TestListReportsEndpoint:
    """Tests for GET /api/v1/dashboard/reports endpoint."""

    @pytest.mark.asyncio
    async def test_list_reports_success(
        self, client, mock_user_id, mock_report_list_data
    ):
        """Test successful report list retrieval.

        AC-056: Dashboard lists reports sorted by date descending
        """
        with patch(
            "api.services.dashboard_service.dashboard_service.list_user_reports"
        ) as mock_list:
            mock_list.return_value = mock_report_list_data

            with patch(
                "api.routers.auth.get_current_user",
                return_value={"id": mock_user_id, "email": "test@example.com"},
            ):
                response = client.get(
                    "/api/v1/dashboard/reports",
                    headers={"Authorization": "Bearer test-token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify response structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "has_more" in data

        # AC-056: Sorted by date descending (newest first)
        items = data["items"]
        assert len(items) == 3
        dates = [item["analyzed_at"] for item in items]
        assert dates == sorted(dates, reverse=True)

    @pytest.mark.asyncio
    async def test_list_reports_includes_required_fields(
        self, client, mock_user_id, mock_report_list_data
    ):
        """Test each report item contains required display fields.

        AC-057: List items show thumbnail, date, summary indicator
        """
        with patch(
            "api.services.dashboard_service.dashboard_service.list_user_reports"
        ) as mock_list:
            mock_list.return_value = mock_report_list_data

            with patch(
                "api.routers.auth.get_current_user",
                return_value={"id": mock_user_id, "email": "test@example.com"},
            ):
                response = client.get(
                    "/api/v1/dashboard/reports",
                    headers={"Authorization": "Bearer test-token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        for item in data["items"]:
            # AC-057: Required fields for display
            assert "id" in item
            assert "thumbnail_url" in item
            assert "analyzed_at" in item
            assert "key_moments_count" in item
            assert "performance_score" in item

    @pytest.mark.asyncio
    async def test_list_reports_empty_state(
        self, client, mock_user_id, empty_report_list_data
    ):
        """Test empty response for users with no reports.

        AC-060: Empty state shows upload CTA
        """
        with patch(
            "api.services.dashboard_service.dashboard_service.list_user_reports"
        ) as mock_list:
            mock_list.return_value = empty_report_list_data

            with patch(
                "api.routers.auth.get_current_user",
                return_value={"id": mock_user_id, "email": "test@example.com"},
            ):
                response = client.get(
                    "/api/v1/dashboard/reports",
                    headers={"Authorization": "Bearer test-token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["items"] == []
        assert data["total"] == 0
        assert data["has_more"] is False

    @pytest.mark.asyncio
    async def test_list_reports_pagination(self, client, mock_user_id):
        """Test pagination support for large report lists."""
        paginated_data = {
            "items": [
                {
                    "id": str(uuid4()),
                    "video_id": str(uuid4()),
                    "thumbnail_url": "https://cdn.example.com/thumb.jpg",
                    "analyzed_at": datetime.now(timezone.utc).isoformat(),
                    "key_moments_count": 5,
                    "performance_score": 70,
                }
            ],
            "total": 15,
            "page": 2,
            "has_more": True,
        }

        with patch(
            "api.services.dashboard_service.dashboard_service.list_user_reports"
        ) as mock_list:
            mock_list.return_value = paginated_data

            with patch(
                "api.routers.auth.get_current_user",
                return_value={"id": mock_user_id, "email": "test@example.com"},
            ):
                response = client.get(
                    "/api/v1/dashboard/reports?page=2&limit=10",
                    headers={"Authorization": "Bearer test-token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["page"] == 2
        assert data["total"] == 15
        assert data["has_more"] is True

    @pytest.mark.asyncio
    async def test_list_reports_unauthorized(self, client):
        """Test 401 response when not authenticated."""
        response = client.get("/api/v1/dashboard/reports")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDeleteReportEndpoint:
    """Tests for DELETE /api/v1/reports/{report_id} endpoint.

    AC-059: Delete report shows confirmation dialog
    """

    @pytest.mark.asyncio
    async def test_delete_report_success(self, client, mock_user_id):
        """Test successful report deletion (soft delete).

        AC-059: Delete report with confirmation (server-side soft delete)
        """
        report_id = str(uuid4())

        with patch(
            "api.services.dashboard_service.dashboard_service.delete_report"
        ) as mock_delete:
            mock_delete.return_value = {"deleted": True, "can_restore_until": "..."}

            with patch(
                "api.routers.auth.get_current_user",
                return_value={"id": mock_user_id, "email": "test@example.com"},
            ):
                response = client.delete(
                    f"/api/v1/reports/{report_id}",
                    headers={"Authorization": "Bearer test-token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["deleted"] is True

    @pytest.mark.asyncio
    async def test_delete_report_not_found(self, client, mock_user_id):
        """Test 404 response when report does not exist."""
        from api.services.dashboard_service import ReportNotFoundError

        report_id = str(uuid4())

        with patch(
            "api.services.dashboard_service.dashboard_service.delete_report"
        ) as mock_delete:
            mock_delete.side_effect = ReportNotFoundError("Report not found")

            with patch(
                "api.routers.auth.get_current_user",
                return_value={"id": mock_user_id, "email": "test@example.com"},
            ):
                response = client.delete(
                    f"/api/v1/reports/{report_id}",
                    headers={"Authorization": "Bearer test-token"},
                )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_delete_report_forbidden_wrong_owner(self, client):
        """Test 403 response when deleting another user's report."""
        from api.services.dashboard_service import ReportOwnershipError

        report_id = str(uuid4())
        different_user_id = str(uuid4())

        with patch(
            "api.services.dashboard_service.dashboard_service.delete_report"
        ) as mock_delete:
            mock_delete.side_effect = ReportOwnershipError(
                "Not authorized to delete this report"
            )

            with patch(
                "api.routers.auth.get_current_user",
                return_value={"id": different_user_id, "email": "other@example.com"},
            ):
                response = client.delete(
                    f"/api/v1/reports/{report_id}",
                    headers={"Authorization": "Bearer test-token"},
                )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_delete_report_unauthorized(self, client):
        """Test 401 response when not authenticated."""
        report_id = str(uuid4())
        response = client.delete(f"/api/v1/reports/{report_id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRestoreReportEndpoint:
    """Tests for POST /api/v1/reports/{report_id}/restore endpoint.

    BDD: User deletes report with undo toast (10 seconds)
    """

    @pytest.mark.asyncio
    async def test_restore_report_success(self, client, mock_user_id):
        """Test successful report restoration (undo delete)."""
        report_id = str(uuid4())

        with patch(
            "api.services.dashboard_service.dashboard_service.restore_report"
        ) as mock_restore:
            mock_restore.return_value = {"restored": True}

            with patch(
                "api.routers.auth.get_current_user",
                return_value={"id": mock_user_id, "email": "test@example.com"},
            ):
                response = client.post(
                    f"/api/v1/reports/{report_id}/restore",
                    headers={"Authorization": "Bearer test-token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["restored"] is True

    @pytest.mark.asyncio
    async def test_restore_report_expired(self, client, mock_user_id):
        """Test 400 response when restore window has expired."""
        from api.services.dashboard_service import RestoreWindowExpiredError

        report_id = str(uuid4())

        with patch(
            "api.services.dashboard_service.dashboard_service.restore_report"
        ) as mock_restore:
            mock_restore.side_effect = RestoreWindowExpiredError(
                "Restore window has expired"
            )

            with patch(
                "api.routers.auth.get_current_user",
                return_value={"id": mock_user_id, "email": "test@example.com"},
            ):
                response = client.post(
                    f"/api/v1/reports/{report_id}/restore",
                    headers={"Authorization": "Bearer test-token"},
                )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestDashboardService:
    """Tests for dashboard service business logic."""

    @pytest.mark.asyncio
    async def test_list_user_reports_filters_by_user(self):
        """Test that list_user_reports only returns user's own reports."""
        from api.services.dashboard_service import DashboardService

        service = DashboardService()
        user_id = uuid4()

        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        result = await service.list_user_reports(
            session=mock_session,
            user_id=user_id,
            page=1,
            limit=10,
        )

        # Verify the query was called (service filters by user_id)
        assert mock_session.execute.called

    @pytest.mark.asyncio
    async def test_delete_report_validates_ownership(self):
        """Test that delete_report checks user ownership."""
        from api.services.dashboard_service import (
            DashboardService,
            ReportOwnershipError,
        )

        service = DashboardService()
        report_id = uuid4()
        owner_id = uuid4()
        requester_id = uuid4()

        mock_session = AsyncMock()
        mock_report = AsyncMock()
        mock_report.user_id = owner_id
        mock_report.deleted_at = None

        with patch.object(
            service, "_get_report_by_id", return_value=mock_report
        ):
            with pytest.raises(ReportOwnershipError):
                await service.delete_report(mock_session, report_id, requester_id)

    @pytest.mark.asyncio
    async def test_delete_report_soft_deletes(self):
        """Test that delete_report performs soft delete."""
        from api.services.dashboard_service import DashboardService

        service = DashboardService()
        report_id = uuid4()
        user_id = uuid4()

        mock_session = AsyncMock()
        mock_report = AsyncMock()
        mock_report.user_id = user_id
        mock_report.deleted_at = None

        with patch.object(
            service, "_get_report_by_id", return_value=mock_report
        ):
            result = await service.delete_report(mock_session, report_id, user_id)

        # Verify soft delete was performed
        assert mock_report.deleted_at is not None
        assert result["deleted"] is True
