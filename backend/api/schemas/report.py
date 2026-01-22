"""Report schemas for request/response validation.

@feature F007 - LLM Strategic Analysis
@feature F008 - Report Display

Acceptance Criteria:
- AC-035: Pose data and stamps formatted as JSON for LLM
- AC-036: Derived metrics calculated (reach ratio, tilt, guard speed, frequency)
- AC-037: LLM generates 3-5 strengths, weaknesses, recommendations each
- AC-040: Analysis includes AI disclaimer
"""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


# --- Analysis Item Schemas ---


class StrengthItem(BaseModel):
    """Schema for a single strength item in the report.

    AC-037: LLM generates 3-5 strengths
    """

    title: str = Field(..., min_length=1, max_length=100, description="Strength title")
    description: str = Field(
        ..., min_length=1, max_length=500, description="Detailed description"
    )
    metric_reference: Optional[str] = Field(
        default=None, description="Reference to related metric (if any)"
    )


class WeaknessItem(BaseModel):
    """Schema for a single weakness item in the report.

    AC-037: LLM generates 3-5 weaknesses
    """

    title: str = Field(..., min_length=1, max_length=100, description="Weakness title")
    description: str = Field(
        ..., min_length=1, max_length=500, description="Detailed description"
    )
    metric_reference: Optional[str] = Field(
        default=None, description="Reference to related metric (if any)"
    )


class RecommendationItem(BaseModel):
    """Schema for a single recommendation item in the report.

    AC-037: LLM generates 3-5 recommendations
    """

    title: str = Field(
        ..., min_length=1, max_length=100, description="Recommendation title"
    )
    description: str = Field(
        ..., min_length=1, max_length=500, description="Detailed description"
    )
    priority: Literal["high", "medium", "low"] = Field(
        ..., description="Priority level"
    )
    drill_type: Optional[str] = Field(
        default=None, description="Type of drill (speed, power, defense, technique)"
    )


# --- Metrics Schemas ---


class MetricValue(BaseModel):
    """Schema for a single metric value.

    AC-036: Derived metrics calculated (reach ratio, tilt, guard speed, frequency)
    """

    value: float = Field(..., description="Metric value")
    unit: str = Field(..., description="Unit of measurement")
    benchmark_min: Optional[float] = Field(
        default=None, description="Minimum benchmark value"
    )
    benchmark_max: Optional[float] = Field(
        default=None, description="Maximum benchmark value"
    )
    percentile: Optional[int] = Field(
        default=None, ge=0, le=100, description="Percentile ranking (0-100)"
    )


class MetricsData(BaseModel):
    """Schema for all calculated metrics.

    AC-036: Derived metrics calculated
    - Reach-to-distance maintenance ratio
    - Upper body tilt during punches
    - Guard recovery speed
    - Punch frequency
    """

    punch_frequency: Optional[MetricValue] = Field(
        default=None, description="Punches per 10 seconds"
    )
    guard_recovery_speed: Optional[MetricValue] = Field(
        default=None, description="Time to return guard after punch"
    )
    reach_ratio: Optional[MetricValue] = Field(
        default=None, description="Reach-to-distance maintenance ratio"
    )
    upper_body_tilt: Optional[MetricValue] = Field(
        default=None, description="Upper body tilt during punches (degrees)"
    )
    jab_speed: Optional[MetricValue] = Field(
        default=None, description="Average jab velocity"
    )
    combination_frequency: Optional[MetricValue] = Field(
        default=None, description="Combinations per minute"
    )


# --- Request Schemas ---


class ReportCreate(BaseModel):
    """Schema for creating a new report."""

    analysis_id: str = Field(..., description="Analysis ID this report is for")
    video_id: str = Field(..., description="Video ID")
    user_id: str = Field(..., description="User ID")
    performance_score: Optional[int] = Field(
        default=None, ge=0, le=100, description="Overall performance score (0-100)"
    )
    overall_assessment: str = Field(
        ..., min_length=10, max_length=2000, description="Overall assessment text"
    )
    strengths: list[StrengthItem] = Field(
        ..., min_length=3, max_length=5, description="3-5 strength items"
    )
    weaknesses: list[WeaknessItem] = Field(
        ..., min_length=3, max_length=5, description="3-5 weakness items"
    )
    recommendations: list[RecommendationItem] = Field(
        ..., min_length=3, max_length=5, description="3-5 recommendation items"
    )
    metrics: dict = Field(..., description="Calculated metrics")
    llm_model: Optional[str] = Field(default=None, description="LLM model used")
    prompt_tokens: Optional[int] = Field(
        default=None, ge=0, description="Prompt token count"
    )
    completion_tokens: Optional[int] = Field(
        default=None, ge=0, description="Completion token count"
    )


# --- Response Schemas ---


class ReportResponse(BaseModel):
    """Schema for report API response.

    AC-040: Analysis includes AI disclaimer
    """

    id: str = Field(..., description="Report unique identifier")
    analysis_id: str = Field(..., description="Associated analysis ID")
    video_id: str = Field(..., description="Associated video ID")
    user_id: str = Field(..., description="Owner user ID")
    performance_score: Optional[int] = Field(
        default=None, description="Overall performance score (0-100)"
    )
    overall_assessment: str = Field(..., description="Overall assessment text")
    strengths: list[StrengthItem] = Field(..., description="List of strengths")
    weaknesses: list[WeaknessItem] = Field(..., description="List of weaknesses")
    recommendations: list[RecommendationItem] = Field(
        ..., description="List of recommendations"
    )
    metrics: dict = Field(..., description="Calculated metrics")
    llm_model: Optional[str] = Field(default=None, description="LLM model used")
    disclaimer: str = Field(
        ..., description="AI disclaimer (required) - AC-040"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")


class ReportSummary(BaseModel):
    """Summary schema for report list responses."""

    id: str = Field(..., description="Report unique identifier")
    analysis_id: str = Field(..., description="Associated analysis ID")
    video_id: str = Field(..., description="Associated video ID")
    performance_score: Optional[int] = Field(
        default=None, description="Overall performance score"
    )
    created_at: datetime = Field(..., description="Creation timestamp")


# --- LLM Input/Output Schemas ---


class LLMAnalysisInput(BaseModel):
    """Schema for data sent to LLM for analysis.

    AC-035: Pose data and stamps formatted as JSON for LLM
    """

    pose_summary: dict = Field(..., description="Summarized pose data")
    stamps_summary: dict = Field(..., description="Summarized stamp data")
    metrics: dict = Field(..., description="Pre-calculated metrics")
    user_context: dict = Field(
        ..., description="User context (experience level, body specs)"
    )


class LLMAnalysisOutput(BaseModel):
    """Schema for LLM analysis response.

    AC-037: LLM generates 3-5 strengths, weaknesses, recommendations each
    """

    overall_assessment: str = Field(..., description="Overall assessment")
    performance_score: int = Field(..., ge=0, le=100, description="Performance score")
    strengths: list[StrengthItem] = Field(
        ..., min_length=3, max_length=5, description="3-5 strengths"
    )
    weaknesses: list[WeaknessItem] = Field(
        ..., min_length=3, max_length=5, description="3-5 weaknesses"
    )
    recommendations: list[RecommendationItem] = Field(
        ..., min_length=3, max_length=5, description="3-5 recommendations"
    )


# --- Stamp Schema for Report Display ---


class StampItem(BaseModel):
    """Schema for a stamp (key moment) in the report.

    AC-045: Key moments section with timestamp links
    """

    stamp_id: str = Field(..., description="Stamp unique identifier")
    timestamp_seconds: float = Field(..., description="Timestamp in seconds")
    frame_number: int = Field(..., description="Frame number in video")
    action_type: str = Field(..., description="Action type (jab, hook, etc.)")
    side: str = Field(..., description="Side (left, right, both)")
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence")
    thumbnail_key: Optional[str] = Field(
        default=None, description="S3 key for thumbnail"
    )


# --- Detail Response Schema for Report Display ---


class ReportDetailResponse(BaseModel):
    """Full report detail response for report display page.

    @feature F008 - Report Display

    AC-041: Summary section displays overall assessment
    AC-042: Strengths section shows 3-5 observations
    AC-043: Weaknesses section shows 3-5 improvement areas
    AC-044: Recommendations section shows 3-5 actionable items
    AC-045: Key moments section with timestamp links
    AC-046: Metrics displayed with visual indicators
    """

    id: str = Field(..., description="Report unique identifier")
    analysis_id: str = Field(..., description="Associated analysis ID")
    video_id: str = Field(..., description="Associated video ID")
    user_id: str = Field(..., description="Owner user ID")

    # AC-041: Summary section
    performance_score: Optional[int] = Field(
        default=None, description="Overall performance score (0-100)"
    )
    overall_assessment: str = Field(..., description="Overall assessment text")

    # AC-042: Strengths section (3-5 observations)
    strengths: list[StrengthItem] = Field(..., description="List of strengths")

    # AC-043: Weaknesses section (3-5 improvement areas)
    weaknesses: list[WeaknessItem] = Field(..., description="List of weaknesses")

    # AC-044: Recommendations section (3-5 actionable items)
    recommendations: list[RecommendationItem] = Field(
        ..., description="List of recommendations"
    )

    # AC-046: Metrics with visual indicators
    metrics: dict = Field(..., description="Calculated metrics with benchmarks")

    # AC-045: Key moments with timestamps
    stamps: list[StampItem] = Field(
        default_factory=list, description="Key moments with timestamps"
    )

    # Metadata
    llm_model: Optional[str] = Field(default=None, description="LLM model used")
    disclaimer: str = Field(
        ..., description="AI disclaimer (required)"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(
        default=None, description="Last update timestamp"
    )
