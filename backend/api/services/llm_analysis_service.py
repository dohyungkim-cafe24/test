"""LLM Analysis Service for generating strategic coaching feedback.

@feature F007 - LLM Strategic Analysis

Implements:
- AC-035: Pose data and stamps formatted as JSON for LLM
- AC-036: Derived metrics calculated (reach ratio, tilt, guard speed, frequency)
- AC-037: LLM generates 3-5 strengths, weaknesses, recommendations each
- AC-038: Analysis adapts to user experience level
- AC-039: LLM failure retries 3 times with exponential backoff
- AC-040: Analysis includes AI disclaimer
"""
import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from api.models.report import DEFAULT_DISCLAIMER

logger = logging.getLogger(__name__)


class LLMAnalysisError(Exception):
    """Base exception for LLM analysis errors."""

    pass


class LLMRetryExhaustedError(LLMAnalysisError):
    """LLM API failed after all retry attempts.

    AC-039: LLM failure retries 3 times with exponential backoff
    BDD: LLM API exhausts retries (show "Analysis incomplete" message)
    """

    pass


class LLMResponseParseError(LLMAnalysisError):
    """Failed to parse LLM response."""

    pass


# Experience level prompts - AC-038
EXPERIENCE_LEVEL_CONTEXTS = {
    "beginner": """
The user is a BEGINNER boxer. Please:
- Use simple, beginner-friendly terminology
- Focus on fundamental techniques (basic stance, guard position, simple punches)
- Provide instructional, encouraging tone
- Emphasize safety and proper form over advanced techniques
- Recommend basic drills suitable for newcomers
""",
    "intermediate": """
The user is an INTERMEDIATE boxer. Please:
- Use standard boxing terminology
- Focus on refining technique and building consistency
- Balance technical feedback with practical advice
- Recommend drills that challenge and improve existing skills
""",
    "advanced": """
The user is an ADVANCED boxer. Please:
- Use technical boxing terminology
- Focus on subtle technique refinements and strategic elements
- Provide detailed analysis of timing, angles, and combinations
- Recommend advanced drills and sparring concepts
""",
    "competitive": """
The user is a COMPETITIVE boxer (competition-level). Please:
- Use advanced technical and strategic terminology
- Focus on high-level refinements and optimization
- Analyze tactical elements, ring generalship, and fight IQ
- Provide competition-specific recommendations
- Compare metrics to competitive benchmarks
""",
}


# Metric benchmarks by experience level
METRIC_BENCHMARKS = {
    "punch_frequency": {
        "unit": "punches_per_10s",
        "beginner": {"min": 1.0, "max": 2.0},
        "intermediate": {"min": 1.5, "max": 2.5},
        "advanced": {"min": 2.0, "max": 3.0},
        "competitive": {"min": 2.5, "max": 3.5},
    },
    "guard_recovery_speed": {
        "unit": "seconds",
        "beginner": {"min": 0.8, "max": 1.2},
        "intermediate": {"min": 0.5, "max": 0.8},
        "advanced": {"min": 0.3, "max": 0.5},
        "competitive": {"min": 0.2, "max": 0.4},
    },
}


class LLMAnalysisService:
    """Service for generating LLM-based strategic analysis.

    Handles:
    - Prompt formatting with pose data and stamps (AC-035)
    - Derived metrics calculation (AC-036)
    - LLM API calls with retry logic (AC-039)
    - Response parsing and validation (AC-037)
    - Experience level adaptation (AC-038)
    """

    def __init__(self):
        """Initialize LLM analysis service."""
        self._client = None
        self._model = os.getenv("OPENAI_MODEL", "gpt-4")
        self._temperature = 0.3  # Low temperature for consistency
        self._max_retries = 3
        self._base_delay = 1.0  # Base delay for exponential backoff

    @property
    def client(self):
        """Get or create OpenAI client (lazy initialization)."""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(
                    api_key=os.getenv("OPENAI_API_KEY"),
                )
            except ImportError:
                logger.warning("OpenAI package not installed")
                raise LLMAnalysisError("OpenAI package not installed")
        return self._client

    def format_prompt(
        self,
        pose_data: dict[str, Any],
        stamps: list[dict[str, Any]],
        body_specs: dict[str, Any],
    ) -> str:
        """Format pose data and stamps as structured prompt for LLM.

        AC-035: Pose data and stamps formatted as JSON for LLM
        AC-038: Analysis adapts to user experience level

        Args:
            pose_data: Pose estimation data
            stamps: Detected action stamps
            body_specs: User body specifications

        Returns:
            Formatted prompt string for LLM
        """
        experience_level = body_specs.get("experience_level", "intermediate")
        experience_context = EXPERIENCE_LEVEL_CONTEXTS.get(
            experience_level, EXPERIENCE_LEVEL_CONTEXTS["intermediate"]
        )

        # Summarize pose data
        pose_summary = self._summarize_pose_data(pose_data)

        # Summarize stamps
        stamps_summary = self._summarize_stamps(stamps)

        # Pre-calculate metrics
        metrics = self.calculate_metrics(pose_data, stamps, body_specs)

        prompt = f"""You are an expert boxing coach analyzing a sparring video.
Analyze the following data and provide strategic coaching feedback.

## User Profile
- Height: {body_specs.get('height_cm', 'Unknown')} cm
- Weight: {body_specs.get('weight_kg', 'Unknown')} kg
- Experience Level: {experience_level}
- Stance: {body_specs.get('stance', 'orthodox')}

{experience_context}

## Pose Analysis Summary
{json.dumps(pose_summary, indent=2)}

## Detected Actions (Stamps)
{json.dumps(stamps_summary, indent=2)}

## Calculated Metrics
{json.dumps(metrics, indent=2)}

## Your Task
Based on the data above, provide a comprehensive analysis in the following JSON format:

```json
{{
    "overall_assessment": "A 2-3 sentence overall assessment of the boxer's performance",
    "performance_score": <integer 0-100>,
    "strengths": [
        {{"title": "Brief title", "description": "Detailed description (1-2 sentences)", "metric_reference": "metric_name or null"}},
        // 3-5 strengths total
    ],
    "weaknesses": [
        {{"title": "Brief title", "description": "Detailed description (1-2 sentences)", "metric_reference": "metric_name or null"}},
        // 3-5 weaknesses total
    ],
    "recommendations": [
        {{"title": "Brief title", "description": "Specific drill or practice recommendation (1-2 sentences)", "priority": "high|medium|low", "drill_type": "speed|power|defense|technique|footwork"}},
        // 3-5 recommendations total
    ]
}}
```

IMPORTANT:
- Provide exactly 3-5 items for each of strengths, weaknesses, and recommendations
- Be specific and actionable in your feedback
- Reference the metrics data where relevant
- Adjust terminology and recommendations to the user's experience level
- Return ONLY the JSON object, no additional text
"""
        return prompt

    def _summarize_pose_data(self, pose_data: dict[str, Any]) -> dict[str, Any]:
        """Summarize pose data for LLM prompt."""
        return {
            "total_frames": pose_data.get("total_frames", 0),
            "successful_frames": pose_data.get("successful_frames", 0),
            "fps": pose_data.get("fps", 30),
            "tracking_quality": pose_data.get("tracking", {}).get(
                "average_confidence", 0.9
            ),
            "analysis_duration_seconds": (
                pose_data.get("total_frames", 0) / pose_data.get("fps", 30)
                if pose_data.get("fps", 30) > 0
                else 0
            ),
        }

    def _summarize_stamps(self, stamps: list[dict[str, Any]]) -> dict[str, Any]:
        """Summarize stamps for LLM prompt."""
        strike_types = ["jab", "straight", "hook", "uppercut"]
        defense_types = ["guard_up", "guard_down", "slip", "duck", "bob_weave"]

        strikes = {}
        defenses = {}
        total_confidence = 0.0

        for stamp in stamps:
            action_type = stamp.get("action_type", "unknown")
            confidence = stamp.get("confidence", 0.0)
            total_confidence += confidence

            if action_type in strike_types:
                strikes[action_type] = strikes.get(action_type, 0) + 1
            elif action_type in defense_types:
                defenses[action_type] = defenses.get(action_type, 0) + 1

        avg_confidence = total_confidence / len(stamps) if stamps else 0.0

        return {
            "total_actions": len(stamps),
            "strikes": strikes,
            "defenses": defenses,
            "total_strikes": sum(strikes.values()),
            "total_defenses": sum(defenses.values()),
            "average_confidence": round(avg_confidence, 2),
            "timeline": [
                {
                    "time": round(s.get("timestamp_seconds", 0), 1),
                    "action": s.get("action_type"),
                    "side": s.get("side"),
                }
                for s in stamps[:20]  # First 20 actions for context
            ],
        }

    def calculate_metrics(
        self,
        pose_data: dict[str, Any],
        stamps: list[dict[str, Any]],
        body_specs: dict[str, Any],
    ) -> dict[str, Any]:
        """Calculate derived metrics from pose data and stamps.

        AC-036: Derived metrics calculated (reach ratio, tilt, guard speed, frequency)

        Args:
            pose_data: Pose estimation data
            stamps: Detected action stamps
            body_specs: User body specifications

        Returns:
            Dictionary of calculated metrics with benchmarks
        """
        experience_level = body_specs.get("experience_level", "intermediate")
        total_frames = pose_data.get("total_frames", 0)
        fps = pose_data.get("fps", 30)
        duration_seconds = total_frames / fps if fps > 0 else 0

        metrics = {}

        # Punch frequency (punches per 10 seconds)
        strike_types = ["jab", "straight", "hook", "uppercut"]
        strikes = [s for s in stamps if s.get("action_type") in strike_types]
        if duration_seconds > 0:
            punch_freq = (len(strikes) / duration_seconds) * 10
            benchmarks = METRIC_BENCHMARKS["punch_frequency"]
            level_bench = benchmarks.get(experience_level, benchmarks["intermediate"])

            # Calculate percentile (simple linear interpolation)
            percentile = self._calculate_percentile(
                punch_freq, level_bench["min"], level_bench["max"]
            )

            metrics["punch_frequency"] = {
                "value": round(punch_freq, 2),
                "unit": benchmarks["unit"],
                "benchmark_min": level_bench["min"],
                "benchmark_max": level_bench["max"],
                "percentile": percentile,
            }

        # Guard recovery speed (estimate from guard_up stamps after strikes)
        guard_ups = [s for s in stamps if s.get("action_type") == "guard_up"]
        if strikes and guard_ups:
            recovery_times = []
            for strike in strikes:
                strike_time = strike.get("timestamp_seconds", 0)
                # Find next guard_up after this strike
                next_guards = [
                    g for g in guard_ups
                    if g.get("timestamp_seconds", 0) > strike_time
                ]
                if next_guards:
                    recovery = next_guards[0].get("timestamp_seconds", 0) - strike_time
                    if recovery < 2.0:  # Only count reasonable recovery times
                        recovery_times.append(recovery)

            if recovery_times:
                avg_recovery = sum(recovery_times) / len(recovery_times)
                benchmarks = METRIC_BENCHMARKS["guard_recovery_speed"]
                level_bench = benchmarks.get(experience_level, benchmarks["intermediate"])

                # For recovery speed, lower is better
                percentile = self._calculate_percentile_inverse(
                    avg_recovery, level_bench["min"], level_bench["max"]
                )

                metrics["guard_recovery_speed"] = {
                    "value": round(avg_recovery, 2),
                    "unit": benchmarks["unit"],
                    "benchmark_min": level_bench["min"],
                    "benchmark_max": level_bench["max"],
                    "percentile": percentile,
                }

        # Combination frequency (sequences of 2+ punches within 1 second)
        if strikes and duration_seconds > 0:
            combinations = 0
            sorted_strikes = sorted(strikes, key=lambda x: x.get("timestamp_seconds", 0))
            for i in range(len(sorted_strikes) - 1):
                time_diff = (
                    sorted_strikes[i + 1].get("timestamp_seconds", 0)
                    - sorted_strikes[i].get("timestamp_seconds", 0)
                )
                if time_diff < 1.0:
                    combinations += 1

            combo_per_min = (combinations / duration_seconds) * 60 if duration_seconds > 0 else 0
            metrics["combination_frequency"] = {
                "value": round(combo_per_min, 1),
                "unit": "combinations_per_minute",
                "benchmark_min": 2.0,
                "benchmark_max": 8.0,
                "percentile": min(100, int((combo_per_min / 8.0) * 100)),
            }

        # Defensive action ratio
        defense_types = ["guard_up", "slip", "duck", "bob_weave"]
        defenses = [s for s in stamps if s.get("action_type") in defense_types]
        if stamps:
            defense_ratio = len(defenses) / len(stamps)
            metrics["defense_ratio"] = {
                "value": round(defense_ratio, 2),
                "unit": "ratio",
                "benchmark_min": 0.2,
                "benchmark_max": 0.4,
                "percentile": min(100, int((defense_ratio / 0.4) * 100)),
            }

        return metrics

    def _calculate_percentile(
        self, value: float, min_val: float, max_val: float
    ) -> int:
        """Calculate percentile for a metric (higher is better)."""
        if max_val == min_val:
            return 50
        normalized = (value - min_val) / (max_val - min_val)
        return max(0, min(100, int(normalized * 100)))

    def _calculate_percentile_inverse(
        self, value: float, min_val: float, max_val: float
    ) -> int:
        """Calculate percentile for a metric (lower is better)."""
        if max_val == min_val:
            return 50
        # For inverse metrics, being at min_val = 100%, at max_val = 0%
        normalized = 1 - ((value - min_val) / (max_val - min_val))
        return max(0, min(100, int(normalized * 100)))

    async def _call_llm_with_retry(self, prompt: str) -> dict[str, Any]:
        """Call LLM API with exponential backoff retry.

        AC-039: LLM failure retries 3 times with exponential backoff
        BDD: LLM API failure triggers retry (exponential backoff)

        Args:
            prompt: Formatted prompt string

        Returns:
            LLM response with content and usage

        Raises:
            LLMRetryExhaustedError: If all retries fail
        """
        last_error = None

        for attempt in range(self._max_retries):
            try:
                logger.info(
                    "llm.call_attempt",
                    extra={
                        "attempt": attempt + 1,
                        "max_retries": self._max_retries,
                    },
                )

                response = await self.client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert boxing coach providing strategic analysis. Always respond with valid JSON only.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=self._temperature,
                    max_tokens=2000,
                    response_format={"type": "json_object"},
                )

                return {
                    "content": response.choices[0].message.content,
                    "model": response.model,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                }

            except Exception as e:
                last_error = e
                logger.warning(
                    "llm.call_failed",
                    extra={
                        "attempt": attempt + 1,
                        "error": str(e),
                    },
                )

                if attempt < self._max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    delay = self._base_delay * (2**attempt)
                    logger.info(
                        "llm.retry_scheduled",
                        extra={
                            "delay_seconds": delay,
                            "next_attempt": attempt + 2,
                        },
                    )
                    await asyncio.sleep(delay)

        # All retries exhausted
        logger.error(
            "llm.retries_exhausted",
            extra={
                "max_retries": self._max_retries,
                "last_error": str(last_error),
            },
        )
        raise LLMRetryExhaustedError(
            f"LLM API failed after {self._max_retries} attempts: {last_error}"
        )

    def parse_llm_response(self, response: dict[str, Any]) -> dict[str, Any]:
        """Parse and validate LLM response.

        AC-037: LLM generates 3-5 strengths, weaknesses, recommendations each

        Args:
            response: Raw LLM response

        Returns:
            Parsed analysis data

        Raises:
            LLMResponseParseError: If response parsing fails
        """
        try:
            content = response.get("content", "")
            data = json.loads(content)

            # Validate structure
            required_keys = [
                "overall_assessment",
                "performance_score",
                "strengths",
                "weaknesses",
                "recommendations",
            ]
            for key in required_keys:
                if key not in data:
                    raise LLMResponseParseError(f"Missing required key: {key}")

            # Validate item counts (AC-037)
            for section in ["strengths", "weaknesses", "recommendations"]:
                items = data.get(section, [])
                if not isinstance(items, list):
                    raise LLMResponseParseError(f"{section} must be a list")
                if len(items) < 3 or len(items) > 5:
                    logger.warning(
                        f"llm.item_count_warning",
                        extra={
                            "section": section,
                            "count": len(items),
                            "expected": "3-5",
                        },
                    )
                    # Adjust if needed (truncate or pad)
                    if len(items) > 5:
                        data[section] = items[:5]
                    elif len(items) < 3:
                        # Pad with generic items if needed
                        while len(data[section]) < 3:
                            data[section].append({
                                "title": f"Additional {section[:-1]}",
                                "description": "Additional analysis point",
                                "metric_reference": None,
                            })

            return data

        except json.JSONDecodeError as e:
            raise LLMResponseParseError(f"Invalid JSON response: {e}")
        except Exception as e:
            raise LLMResponseParseError(f"Failed to parse response: {e}")

    async def generate_analysis(
        self,
        pose_data: dict[str, Any],
        stamps: list[dict[str, Any]],
        body_specs: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate complete strategic analysis.

        Main entry point for LLM analysis generation.

        Args:
            pose_data: Pose estimation data
            stamps: Detected action stamps
            body_specs: User body specifications

        Returns:
            Complete analysis with all required fields including:
            - strengths, weaknesses, recommendations (AC-037)
            - metrics (AC-036)
            - disclaimer (AC-040)
        """
        # Format prompt (AC-035)
        prompt = self.format_prompt(pose_data, stamps, body_specs)

        # Call LLM with retry (AC-039)
        response = await self._call_llm_with_retry(prompt)

        # Parse response (AC-037)
        analysis = self.parse_llm_response(response)

        # Calculate metrics (AC-036)
        metrics = self.calculate_metrics(pose_data, stamps, body_specs)

        # Build complete result
        result = {
            "overall_assessment": analysis["overall_assessment"],
            "performance_score": analysis["performance_score"],
            "strengths": analysis["strengths"],
            "weaknesses": analysis["weaknesses"],
            "recommendations": analysis["recommendations"],
            "metrics": metrics,
            "llm_model": response.get("model", self._model),
            "prompt_tokens": response.get("prompt_tokens"),
            "completion_tokens": response.get("completion_tokens"),
            "disclaimer": DEFAULT_DISCLAIMER,  # AC-040
        }

        logger.info(
            "llm.analysis_generated",
            extra={
                "strengths_count": len(result["strengths"]),
                "weaknesses_count": len(result["weaknesses"]),
                "recommendations_count": len(result["recommendations"]),
                "performance_score": result["performance_score"],
            },
        )

        return result


# Singleton instance
llm_analysis_service = LLMAnalysisService()
