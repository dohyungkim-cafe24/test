"""Test suite for reports endpoints.

@feature F008 - Report Display

Acceptance Criteria:
- AC-041: Summary section displays overall assessment
- AC-042: Strengths section shows 3-5 observations
- AC-043: Weaknesses section shows 3-5 improvement areas
- AC-044: Recommendations section shows 3-5 actionable items
- AC-045: Key moments section with timestamp links
- AC-046: Metrics displayed with visual indicators
- AC-047: Report page loads within 1.5 seconds
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import status


# Test fixtures
@pytest.fixture
def mock_report_data():
    """Mock complete report data for testing."""
    return {
        "id": str(uuid4()),
        "analysis_id": str(uuid4()),
        "video_id": str(uuid4()),
        "user_id": str(uuid4()),
        "performance_score": 72,
        "overall_assessment": "Solid intermediate-level technique with room for improvement in defensive positioning",
        "strengths": [
            {
                "title": "Consistent Jab Mechanics",
                "description": "Your jab demonstrates good extension and snap. Shoulder rotation averages 42 degrees, which is within optimal range.",
                "metric_reference": "jab_extension_ratio",
            },
            {
                "title": "Punch Frequency",
                "description": "You maintain an active offensive pace with 2.3 punches per 10 seconds.",
                "metric_reference": "punch_frequency",
            },
            {
                "title": "Good Footwork",
                "description": "You maintain good balance during punches.",
                "metric_reference": None,
            },
        ],
        "weaknesses": [
            {
                "title": "Guard Recovery Delay",
                "description": "After throwing combinations, your guard takes 0.8 seconds to return to defensive position.",
                "metric_reference": "guard_recovery_speed",
            },
            {
                "title": "Telegraphing Punches",
                "description": "Your right hand drops slightly before hooks.",
                "metric_reference": None,
            },
            {
                "title": "Head Movement",
                "description": "Limited lateral head movement during combinations.",
                "metric_reference": None,
            },
        ],
        "recommendations": [
            {
                "title": "Guard Return Drill",
                "description": "Practice 3-punch combos with immediate guard return.",
                "priority": "high",
                "drill_type": "defense",
            },
            {
                "title": "Shadow Boxing Focus",
                "description": "Focus on keeping hands high during combinations.",
                "priority": "medium",
                "drill_type": "technique",
            },
            {
                "title": "Slip Bag Work",
                "description": "Add slip bag drills to your routine.",
                "priority": "medium",
                "drill_type": "defense",
            },
        ],
        "metrics": {
            "punch_frequency": {
                "value": 2.3,
                "unit": "punches_per_10s",
                "benchmark_min": 1.5,
                "benchmark_max": 3.0,
                "percentile": 65,
            },
            "guard_recovery_speed": {
                "value": 0.8,
                "unit": "seconds",
                "benchmark_min": 0.3,
                "benchmark_max": 0.5,
                "percentile": 35,
            },
        },
        "llm_model": "gpt-4",
        "disclaimer": "This AI analysis is for training purposes only and is not a substitute for professional coaching. Always train under proper supervision.",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def mock_stamps_data():
    """Mock stamp data for key moments."""
    return [
        {
            "stamp_id": str(uuid4()),
            "timestamp_seconds": 5.3,
            "frame_number": 159,
            "action_type": "jab",
            "side": "left",
            "confidence": 0.94,
            "thumbnail_url": "https://cdn.example.com/thumb1.jpg",
        },
        {
            "stamp_id": str(uuid4()),
            "timestamp_seconds": 15.2,
            "frame_number": 456,
            "action_type": "straight",
            "side": "right",
            "confidence": 0.91,
            "thumbnail_url": "https://cdn.example.com/thumb2.jpg",
        },
        {
            "stamp_id": str(uuid4()),
            "timestamp_seconds": 23.8,
            "frame_number": 714,
            "action_type": "guard_down",
            "side": "both",
            "confidence": 0.88,
            "thumbnail_url": "https://cdn.example.com/thumb3.jpg",
        },
    ]


class TestGetReportEndpoint:
    """Tests for GET /api/v1/reports/{report_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_report_success(
        self, client, mock_report_data, mock_stamps_data
    ):
        """Test successful report retrieval with all sections.

        AC-041: Summary section displays overall assessment
        AC-042: Strengths section shows 3-5 observations
        AC-043: Weaknesses section shows 3-5 improvement areas
        AC-044: Recommendations section shows 3-5 actionable items
        """
        report_id = mock_report_data["id"]
        user_id = mock_report_data["user_id"]

        with patch(
            "api.services.report_service.report_service.get_report"
        ) as mock_get_report:
            mock_get_report.return_value = {
                **mock_report_data,
                "stamps": mock_stamps_data,
            }

            # Mock auth
            with patch(
                "api.routers.auth.get_current_user",
                return_value={"id": user_id, "email": "test@example.com"},
            ):
                response = client.get(
                    f"/api/v1/reports/{report_id}",
                    headers={"Authorization": "Bearer test-token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # AC-041: Summary section
        assert "overall_assessment" in data
        assert data["overall_assessment"] == mock_report_data["overall_assessment"]
        assert "performance_score" in data
        assert data["performance_score"] == 72

        # AC-042: Strengths section (3-5 items)
        assert "strengths" in data
        assert len(data["strengths"]) >= 3
        assert len(data["strengths"]) <= 5
        assert all("title" in s and "description" in s for s in data["strengths"])

        # AC-043: Weaknesses section (3-5 items)
        assert "weaknesses" in data
        assert len(data["weaknesses"]) >= 3
        assert len(data["weaknesses"]) <= 5
        assert all("title" in w and "description" in w for w in data["weaknesses"])

        # AC-044: Recommendations section (3-5 items)
        assert "recommendations" in data
        assert len(data["recommendations"]) >= 3
        assert len(data["recommendations"]) <= 5
        assert all(
            "title" in r and "description" in r and "priority" in r
            for r in data["recommendations"]
        )

    @pytest.mark.asyncio
    async def test_get_report_includes_key_moments(
        self, client, mock_report_data, mock_stamps_data
    ):
        """Test report includes key moments with timestamp data.

        AC-045: Key moments section with timestamp links
        """
        report_id = mock_report_data["id"]
        user_id = mock_report_data["user_id"]

        with patch(
            "api.services.report_service.report_service.get_report"
        ) as mock_get_report:
            mock_get_report.return_value = {
                **mock_report_data,
                "stamps": mock_stamps_data,
            }

            with patch(
                "api.routers.auth.get_current_user",
                return_value={"id": user_id, "email": "test@example.com"},
            ):
                response = client.get(
                    f"/api/v1/reports/{report_id}",
                    headers={"Authorization": "Bearer test-token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # AC-045: Key moments with timestamps
        assert "stamps" in data
        assert len(data["stamps"]) > 0
        for stamp in data["stamps"]:
            assert "timestamp_seconds" in stamp
            assert "action_type" in stamp
            assert "confidence" in stamp

    @pytest.mark.asyncio
    async def test_get_report_includes_metrics(self, client, mock_report_data):
        """Test report includes metrics with visual indicator data.

        AC-046: Metrics displayed with visual indicators
        """
        report_id = mock_report_data["id"]
        user_id = mock_report_data["user_id"]

        with patch(
            "api.services.report_service.report_service.get_report"
        ) as mock_get_report:
            mock_get_report.return_value = {**mock_report_data, "stamps": []}

            with patch(
                "api.routers.auth.get_current_user",
                return_value={"id": user_id, "email": "test@example.com"},
            ):
                response = client.get(
                    f"/api/v1/reports/{report_id}",
                    headers={"Authorization": "Bearer test-token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # AC-046: Metrics with visual indicators (benchmarks + percentiles)
        assert "metrics" in data
        metrics = data["metrics"]
        for metric_name, metric_data in metrics.items():
            assert "value" in metric_data
            assert "unit" in metric_data
            assert "benchmark_min" in metric_data
            assert "benchmark_max" in metric_data
            assert "percentile" in metric_data

    @pytest.mark.asyncio
    async def test_get_report_includes_disclaimer(self, client, mock_report_data):
        """Test report includes AI disclaimer.

        BDD: Report includes AI disclaimer
        """
        report_id = mock_report_data["id"]
        user_id = mock_report_data["user_id"]

        with patch(
            "api.services.report_service.report_service.get_report"
        ) as mock_get_report:
            mock_get_report.return_value = {**mock_report_data, "stamps": []}

            with patch(
                "api.routers.auth.get_current_user",
                return_value={"id": user_id, "email": "test@example.com"},
            ):
                response = client.get(
                    f"/api/v1/reports/{report_id}",
                    headers={"Authorization": "Bearer test-token"},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "disclaimer" in data
        assert "AI analysis" in data["disclaimer"]
        assert "professional coaching" in data["disclaimer"]

    @pytest.mark.asyncio
    async def test_get_report_not_found(self, client):
        """Test 404 response when report does not exist."""
        from api.services.report_service import ReportNotFoundError

        fake_report_id = str(uuid4())

        with patch(
            "api.services.report_service.report_service.get_report"
        ) as mock_get_report:
            mock_get_report.side_effect = ReportNotFoundError("Report not found")

            with patch(
                "api.routers.auth.get_current_user",
                return_value={"id": str(uuid4()), "email": "test@example.com"},
            ):
                response = client.get(
                    f"/api/v1/reports/{fake_report_id}",
                    headers={"Authorization": "Bearer test-token"},
                )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_report_unauthorized(self, client, mock_report_data):
        """Test 401 response when not authenticated."""
        report_id = mock_report_data["id"]

        response = client.get(f"/api/v1/reports/{report_id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_report_forbidden_wrong_owner(self, client, mock_report_data):
        """Test 403 response when accessing another user's report."""
        from api.services.report_service import ReportOwnershipError

        report_id = mock_report_data["id"]
        different_user_id = str(uuid4())

        with patch(
            "api.services.report_service.report_service.get_report"
        ) as mock_get_report:
            mock_get_report.side_effect = ReportOwnershipError(
                "Not authorized to access this report"
            )

            with patch(
                "api.routers.auth.get_current_user",
                return_value={"id": different_user_id, "email": "other@example.com"},
            ):
                response = client.get(
                    f"/api/v1/reports/{report_id}",
                    headers={"Authorization": "Bearer test-token"},
                )

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestReportService:
    """Tests for report service business logic."""

    @pytest.mark.asyncio
    async def test_get_report_validates_ownership(self):
        """Test that get_report checks user ownership."""
        from api.services.report_service import ReportService, ReportOwnershipError

        service = ReportService()
        report_id = uuid4()
        owner_id = uuid4()
        requester_id = uuid4()

        # Mock the database session and queries
        mock_session = AsyncMock()
        mock_report = AsyncMock()
        mock_report.user_id = owner_id

        with patch.object(
            service, "_get_report_by_id", return_value=mock_report
        ):
            with pytest.raises(ReportOwnershipError):
                await service.get_report(mock_session, report_id, requester_id)
