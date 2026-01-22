"""Tests for LLM Strategic Analysis (F007).

@feature F007 - LLM Strategic Analysis

Tests:
- AC-035: Pose data and stamps formatted as JSON for LLM
- AC-036: Derived metrics calculated (reach ratio, tilt, guard speed, frequency)
- AC-037: LLM generates 3-5 strengths, weaknesses, recommendations each
- AC-038: Analysis adapts to user experience level
- AC-039: LLM failure retries 3 times with exponential backoff
- AC-040: Analysis includes AI disclaimer

BDD Scenarios from specs/bdd/processing.feature:
- LLM generates strategic analysis (3-5 items for strengths/weaknesses/recommendations)
- Analysis adapts to beginner experience level (friendly terminology)
- Analysis adapts to competitive experience level (advanced terminology)
- LLM API failure triggers retry (exponential backoff)
- LLM API exhausts retries (show "Analysis incomplete" message)
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


class TestReportModel:
    """Tests for Report model."""

    def test_report_model_creation(self):
        """Test Report model can be created with required fields."""
        from api.models.report import Report

        analysis_id = uuid4()
        video_id = uuid4()
        user_id = uuid4()

        report = Report(
            analysis_id=analysis_id,
            video_id=video_id,
            user_id=user_id,
            performance_score=75,
            overall_assessment="Good technique with room for improvement",
            strengths=[
                {"title": "Quick Jab", "description": "Fast lead hand", "metric_reference": "punch_frequency"}
            ],
            weaknesses=[
                {"title": "Guard Recovery", "description": "Slow return to guard", "metric_reference": "guard_recovery_speed"}
            ],
            recommendations=[
                {"title": "Speed Drills", "description": "Work on hand speed", "priority": "high", "drill_type": "speed"}
            ],
            metrics={
                "punch_frequency": {"value": 2.5, "unit": "punches_per_10s", "benchmark_min": 1.5, "benchmark_max": 3.0, "percentile": 70}
            },
            llm_model="gpt-4",
            prompt_tokens=500,
            completion_tokens=800,
        )

        assert report.analysis_id == analysis_id
        assert report.performance_score == 75
        assert len(report.strengths) == 1
        assert len(report.weaknesses) == 1
        assert len(report.recommendations) == 1
        assert report.disclaimer is not None  # AC-040: AI disclaimer required

    def test_report_disclaimer_default(self):
        """Test Report includes default AI disclaimer.

        AC-040: Analysis includes AI disclaimer
        """
        from api.models.report import Report

        report = Report(
            analysis_id=uuid4(),
            video_id=uuid4(),
            user_id=uuid4(),
            performance_score=75,
            overall_assessment="Test assessment",
            strengths=[],
            weaknesses=[],
            recommendations=[],
            metrics={},
        )

        # Default disclaimer should be set
        assert report.disclaimer is not None
        assert "AI analysis" in report.disclaimer or "training purposes" in report.disclaimer


class TestReportSchemas:
    """Tests for Report schemas."""

    def test_strength_item_schema(self):
        """Test StrengthItem schema validation."""
        from api.schemas.report import StrengthItem

        item = StrengthItem(
            title="Quick Jab",
            description="Your jab is fast and precise",
            metric_reference="punch_frequency",
        )

        assert item.title == "Quick Jab"
        assert item.description is not None
        assert item.metric_reference == "punch_frequency"

    def test_weakness_item_schema(self):
        """Test WeaknessItem schema validation."""
        from api.schemas.report import WeaknessItem

        item = WeaknessItem(
            title="Guard Recovery",
            description="Your guard drops after punching",
            metric_reference="guard_recovery_speed",
        )

        assert item.title == "Guard Recovery"
        assert item.metric_reference == "guard_recovery_speed"

    def test_recommendation_item_schema(self):
        """Test RecommendationItem schema validation."""
        from api.schemas.report import RecommendationItem

        item = RecommendationItem(
            title="Speed Drills",
            description="Practice shadow boxing with speed focus",
            priority="high",
            drill_type="speed",
        )

        assert item.title == "Speed Drills"
        assert item.priority in ["high", "medium", "low"]
        assert item.drill_type is not None

    def test_metrics_data_schema(self):
        """Test MetricsData schema validation.

        AC-036: Derived metrics calculated (reach ratio, tilt, guard speed, frequency)
        """
        from api.schemas.report import MetricValue, MetricsData

        metric = MetricValue(
            value=2.5,
            unit="punches_per_10s",
            benchmark_min=1.5,
            benchmark_max=3.0,
            percentile=70,
        )

        assert metric.value == 2.5
        assert metric.percentile == 70

    def test_report_response_schema(self):
        """Test ReportResponse schema includes all required fields."""
        from api.schemas.report import ReportResponse

        report = ReportResponse(
            id=str(uuid4()),
            analysis_id=str(uuid4()),
            video_id=str(uuid4()),
            user_id=str(uuid4()),
            performance_score=75,
            overall_assessment="Good performance",
            strengths=[],
            weaknesses=[],
            recommendations=[],
            metrics={},
            llm_model="gpt-4",
            disclaimer="AI-generated analysis for training purposes only.",
            created_at=datetime.now(timezone.utc),
        )

        assert report.disclaimer is not None
        assert "AI" in report.disclaimer or "training" in report.disclaimer


class TestLLMAnalysisService:
    """Tests for LLMAnalysisService.

    AC-035: Pose data and stamps formatted as JSON for LLM
    AC-036: Derived metrics calculated (reach ratio, tilt, guard speed, frequency)
    AC-037: LLM generates 3-5 strengths, weaknesses, recommendations each
    AC-038: Analysis adapts to user experience level
    AC-039: LLM failure retries 3 times with exponential backoff
    """

    def test_format_prompt_includes_pose_data(self):
        """Test format_prompt formats pose data for LLM.

        AC-035: Pose data and stamps formatted as JSON for LLM
        """
        from api.services.llm_analysis_service import LLMAnalysisService

        service = LLMAnalysisService()

        # Sample pose data
        pose_data = {
            "analysis_id": str(uuid4()),
            "total_frames": 100,
            "successful_frames": 95,
            "frames": [],
        }

        stamps = [
            {"action_type": "jab", "timestamp_seconds": 1.5, "confidence": 0.9},
            {"action_type": "straight", "timestamp_seconds": 2.0, "confidence": 0.85},
        ]

        body_specs = {
            "height_cm": 175,
            "weight_kg": 70,
            "experience_level": "beginner",
            "stance": "orthodox",
        }

        prompt = service.format_prompt(pose_data, stamps, body_specs)

        # Prompt should include structured data
        assert "jab" in prompt.lower() or "punch" in prompt.lower()
        assert "beginner" in prompt.lower()

    def test_calculate_derived_metrics(self):
        """Test calculate_metrics computes derived metrics.

        AC-036: Derived metrics calculated (reach ratio, tilt, guard speed, frequency)
        """
        from api.services.llm_analysis_service import LLMAnalysisService

        service = LLMAnalysisService()

        # Sample data for metrics calculation
        pose_data = {
            "total_frames": 300,
            "fps": 30,
            "frames": [
                {"joints": [{"x": 0.5, "y": 0.5, "z": 0.0, "name": "left_wrist"}] * 33}
            ] * 300,
        }

        stamps = [
            {"action_type": "jab", "timestamp_seconds": 1.0},
            {"action_type": "straight", "timestamp_seconds": 2.0},
            {"action_type": "jab", "timestamp_seconds": 3.0},
            {"action_type": "guard_up", "timestamp_seconds": 3.5},
        ]

        body_specs = {
            "height_cm": 175,
            "weight_kg": 70,
        }

        metrics = service.calculate_metrics(pose_data, stamps, body_specs)

        # Should have the required derived metrics
        assert "punch_frequency" in metrics
        assert "guard_recovery_speed" in metrics or "guard_recovery" in metrics

    def test_analysis_adapts_to_beginner_level(self):
        """Test analysis uses beginner-friendly terminology.

        AC-038: Analysis adapts to user experience level
        BDD: Analysis adapts to beginner experience level (friendly terminology)
        """
        from api.services.llm_analysis_service import LLMAnalysisService

        service = LLMAnalysisService()

        body_specs = {"experience_level": "beginner"}
        prompt = service.format_prompt({}, [], body_specs)

        # Beginner prompt should include friendly context
        assert "beginner" in prompt.lower() or "fundamental" in prompt.lower() or "basic" in prompt.lower()

    def test_analysis_adapts_to_competitive_level(self):
        """Test analysis uses advanced terminology for competitive level.

        AC-038: Analysis adapts to user experience level
        BDD: Analysis adapts to competitive experience level (advanced terminology)
        """
        from api.services.llm_analysis_service import LLMAnalysisService

        service = LLMAnalysisService()

        body_specs = {"experience_level": "competitive"}
        prompt = service.format_prompt({}, [], body_specs)

        # Competitive prompt should include advanced context
        assert "competitive" in prompt.lower() or "advanced" in prompt.lower() or "refinement" in prompt.lower()

    @pytest.mark.asyncio
    async def test_retry_on_llm_failure(self):
        """Test LLM failure triggers retry with exponential backoff.

        AC-039: LLM failure retries 3 times with exponential backoff
        BDD: LLM API failure triggers retry (exponential backoff)
        """
        from api.services.llm_analysis_service import LLMAnalysisService, LLMRetryExhaustedError

        service = LLMAnalysisService()

        # Mock OpenAI client to fail
        mock_client = AsyncMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        service._client = mock_client

        with pytest.raises(LLMRetryExhaustedError):
            await service._call_llm_with_retry("test prompt")

        # Should have been called 3 times (initial + 2 retries)
        assert mock_client.chat.completions.create.call_count == 3

    @pytest.mark.asyncio
    async def test_llm_generates_3_to_5_items(self):
        """Test LLM generates 3-5 items for each section.

        AC-037: LLM generates 3-5 strengths, weaknesses, recommendations each
        BDD: LLM generates strategic analysis (3-5 items)
        """
        from api.services.llm_analysis_service import LLMAnalysisService

        service = LLMAnalysisService()

        # Mock successful LLM response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        {
            "strengths": [
                {"title": "S1", "description": "D1", "metric_reference": "m1"},
                {"title": "S2", "description": "D2", "metric_reference": "m2"},
                {"title": "S3", "description": "D3", "metric_reference": "m3"}
            ],
            "weaknesses": [
                {"title": "W1", "description": "D1", "metric_reference": "m1"},
                {"title": "W2", "description": "D2", "metric_reference": "m2"},
                {"title": "W3", "description": "D3", "metric_reference": "m3"}
            ],
            "recommendations": [
                {"title": "R1", "description": "D1", "priority": "high", "drill_type": "speed"},
                {"title": "R2", "description": "D2", "priority": "medium", "drill_type": "power"},
                {"title": "R3", "description": "D3", "priority": "low", "drill_type": "technique"}
            ],
            "overall_assessment": "Good performance overall.",
            "performance_score": 75
        }
        '''
        mock_response.usage.prompt_tokens = 500
        mock_response.usage.completion_tokens = 800

        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response
        service._client = mock_client

        result = await service._call_llm_with_retry("test prompt")
        parsed = service.parse_llm_response(result)

        # Verify 3-5 items in each section
        assert 3 <= len(parsed["strengths"]) <= 5
        assert 3 <= len(parsed["weaknesses"]) <= 5
        assert 3 <= len(parsed["recommendations"]) <= 5


class TestLLMAnalysisIntegration:
    """Integration tests for full LLM analysis flow."""

    @pytest.mark.asyncio
    async def test_generate_analysis_full_flow(self):
        """Test full analysis generation flow.

        Integration test covering:
        - AC-035: Pose data and stamps formatted as JSON for LLM
        - AC-036: Derived metrics calculated
        - AC-037: LLM generates 3-5 items each
        - AC-040: Analysis includes AI disclaimer
        """
        from api.services.llm_analysis_service import LLMAnalysisService

        service = LLMAnalysisService()

        # Sample input data
        pose_data = {
            "analysis_id": str(uuid4()),
            "total_frames": 300,
            "successful_frames": 290,
            "fps": 30,
            "frames": [],
        }

        stamps = [
            {"action_type": "jab", "timestamp_seconds": 1.0, "confidence": 0.9, "side": "left"},
            {"action_type": "straight", "timestamp_seconds": 2.0, "confidence": 0.85, "side": "right"},
            {"action_type": "jab", "timestamp_seconds": 3.0, "confidence": 0.88, "side": "left"},
        ]

        body_specs = {
            "height_cm": 175,
            "weight_kg": 70,
            "experience_level": "intermediate",
            "stance": "orthodox",
        }

        # Mock LLM response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        {
            "strengths": [
                {"title": "Quick Jab", "description": "Fast lead hand", "metric_reference": "punch_frequency"},
                {"title": "Good Timing", "description": "Well-timed combinations", "metric_reference": null},
                {"title": "Solid Stance", "description": "Balanced footwork", "metric_reference": null}
            ],
            "weaknesses": [
                {"title": "Guard Recovery", "description": "Slow guard return", "metric_reference": "guard_recovery_speed"},
                {"title": "Head Movement", "description": "Limited head movement", "metric_reference": null},
                {"title": "Power Generation", "description": "Could use more hip rotation", "metric_reference": null}
            ],
            "recommendations": [
                {"title": "Speed Bag Work", "description": "Improve hand speed", "priority": "high", "drill_type": "speed"},
                {"title": "Slip Rope Drill", "description": "Improve head movement", "priority": "medium", "drill_type": "defense"},
                {"title": "Heavy Bag Rotation", "description": "Practice hip rotation", "priority": "medium", "drill_type": "power"}
            ],
            "overall_assessment": "Good intermediate-level performance with solid fundamentals.",
            "performance_score": 72
        }
        '''
        mock_response.usage.prompt_tokens = 500
        mock_response.usage.completion_tokens = 800
        mock_response.model = "gpt-4"

        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response
        service._client = mock_client

        result = await service.generate_analysis(pose_data, stamps, body_specs)

        # Verify result structure
        assert "strengths" in result
        assert "weaknesses" in result
        assert "recommendations" in result
        assert "metrics" in result
        assert "overall_assessment" in result
        assert "performance_score" in result
        assert "disclaimer" in result

        # AC-037: 3-5 items each
        assert 3 <= len(result["strengths"]) <= 5
        assert 3 <= len(result["weaknesses"]) <= 5
        assert 3 <= len(result["recommendations"]) <= 5

        # AC-040: Disclaimer included
        assert "AI" in result["disclaimer"] or "training" in result["disclaimer"]
