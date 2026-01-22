"""GPT-based boxing analysis service.

Uses OpenAI's GPT API to generate strategic boxing feedback from pose data.
"""
import json
from typing import Any, Optional

from openai import AsyncOpenAI

from api.config import get_settings


BOXING_ANALYSIS_SYSTEM_PROMPT = """You are an expert boxing coach with decades of experience training fighters at all levels.
You analyze sparring videos using pose estimation data to provide actionable feedback.

Your analysis should be:
- Technical but accessible to beginners
- Encouraging while highlighting areas for improvement
- Specific with concrete recommendations
- Safety-conscious (always emphasize proper form to prevent injury)

Respond in JSON format with the following structure:
{
    "performance_score": <number 1-100>,
    "overall_assessment": "<2-3 sentence summary in both English and Korean>",
    "strengths": [
        {
            "title": "<short title>",
            "title_ko": "<Korean title>",
            "description": "<detailed explanation>",
            "description_ko": "<Korean explanation>"
        }
    ],
    "weaknesses": [
        {
            "title": "<short title>",
            "title_ko": "<Korean title>",
            "description": "<detailed explanation>",
            "description_ko": "<Korean explanation>"
        }
    ],
    "recommendations": [
        {
            "title": "<drill or exercise name>",
            "title_ko": "<Korean title>",
            "description": "<how to practice>",
            "description_ko": "<Korean explanation>",
            "priority": "<high/medium/low>"
        }
    ]
}

Provide 3-5 items for each of strengths, weaknesses, and recommendations.
Always include both English and Korean (_ko suffix) for each text field."""


class GPTAnalyzer:
    """Service for generating boxing analysis using GPT."""

    def __init__(self):
        """Initialize GPT analyzer."""
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        self.model = "gpt-4o-mini"  # Cost-effective for analysis

    async def analyze_boxing_session(
        self,
        pose_data: dict[str, Any],
        body_specs: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Generate boxing analysis from pose data.

        Args:
            pose_data: Aggregated pose and metrics data from video processor
            body_specs: Optional user body specifications

        Returns:
            Analysis result with scores, strengths, weaknesses, recommendations
        """
        # Build the analysis prompt
        user_prompt = self._build_analysis_prompt(pose_data, body_specs)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": BOXING_ANALYSIS_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=2000,
            )

            # Parse response
            content = response.choices[0].message.content
            analysis = json.loads(content)

            # Add metadata
            analysis["llm_model"] = self.model
            analysis["prompt_tokens"] = response.usage.prompt_tokens
            analysis["completion_tokens"] = response.usage.completion_tokens

            return analysis

        except json.JSONDecodeError as e:
            # Return a default response if JSON parsing fails
            return self._get_fallback_analysis(str(e))
        except Exception as e:
            return self._get_fallback_analysis(str(e))

    def _build_analysis_prompt(
        self,
        pose_data: dict[str, Any],
        body_specs: Optional[dict[str, Any]] = None,
    ) -> str:
        """Build the analysis prompt from pose data.

        Args:
            pose_data: Pose and metrics data
            body_specs: Optional body specifications

        Returns:
            Formatted prompt string
        """
        prompt_parts = ["Analyze this boxing sparring session based on the following data:\n"]

        # Add aggregated metrics
        metrics = pose_data.get("aggregated_metrics", {})
        if metrics:
            prompt_parts.append("## Overall Metrics:")
            prompt_parts.append(f"- Guard up percentage: {metrics.get('guard_up_percentage', 'N/A')}%")
            prompt_parts.append(f"- Stance balanced percentage: {metrics.get('stance_balanced_percentage', 'N/A')}%")
            prompt_parts.append(f"- Shoulders level percentage: {metrics.get('shoulders_level_percentage', 'N/A')}%")
            prompt_parts.append(f"- Average guard tightness: {metrics.get('avg_guard_tightness', 'N/A')} (0-1 scale, higher is tighter)")
            prompt_parts.append(f"- Average stance width: {metrics.get('avg_stance_width', 'N/A')} (normalized)")
            prompt_parts.append(f"- Average hip rotation: {metrics.get('avg_hip_rotation', 'N/A')}")
            prompt_parts.append(f"- Valid frames analyzed: {metrics.get('valid_frames', 0)}")
            prompt_parts.append("")

        # Add body specs if available
        if body_specs:
            prompt_parts.append("## Fighter Profile:")
            prompt_parts.append(f"- Height: {body_specs.get('height_cm', 'N/A')} cm")
            prompt_parts.append(f"- Weight: {body_specs.get('weight_kg', 'N/A')} kg")
            prompt_parts.append(f"- Experience: {body_specs.get('experience_level', 'N/A')}")
            prompt_parts.append(f"- Stance: {body_specs.get('stance', 'N/A')}")
            prompt_parts.append("")

        # Add session info
        prompt_parts.append("## Session Info:")
        prompt_parts.append(f"- Total frames analyzed: {pose_data.get('total_frames_analyzed', 0)}")
        prompt_parts.append(f"- Pose detection rate: {pose_data.get('detection_rate', 0) * 100:.1f}%")
        prompt_parts.append("")

        # Add frame-by-frame highlights (sample)
        frame_results = pose_data.get("frame_results", [])
        if frame_results:
            prompt_parts.append("## Frame Analysis Samples:")
            # Include first, middle, and last frames with detections
            detected_frames = [f for f in frame_results if f.get("pose_detected")]
            samples = []
            if detected_frames:
                samples.append(detected_frames[0])
                if len(detected_frames) > 2:
                    samples.append(detected_frames[len(detected_frames) // 2])
                if len(detected_frames) > 1:
                    samples.append(detected_frames[-1])

            for i, frame in enumerate(samples):
                prompt_parts.append(f"\nFrame {i + 1} (at {frame['timestamp_seconds']}s):")
                boxing_metrics = frame.get("boxing_metrics", {})
                for key, value in boxing_metrics.items():
                    prompt_parts.append(f"  - {key}: {value}")

        prompt_parts.append("\n\nBased on this data, provide a comprehensive boxing analysis.")

        return "\n".join(prompt_parts)

    def _get_fallback_analysis(self, error: str) -> dict[str, Any]:
        """Return a fallback analysis when GPT fails.

        Args:
            error: Error message

        Returns:
            Default analysis structure
        """
        return {
            "performance_score": 50,
            "overall_assessment": (
                "Analysis could not be fully completed. Based on the available data, "
                "continue practicing fundamental techniques and focus on maintaining proper form. "
                "분석을 완료할 수 없습니다. 기본 기술을 계속 연습하고 올바른 자세를 유지하는 데 집중하세요."
            ),
            "strengths": [
                {
                    "title": "Consistent Practice",
                    "title_ko": "꾸준한 연습",
                    "description": "You're actively training and seeking feedback, which is the foundation of improvement.",
                    "description_ko": "적극적으로 훈련하고 피드백을 구하는 것이 발전의 기본입니다.",
                }
            ],
            "weaknesses": [
                {
                    "title": "Insufficient Data",
                    "title_ko": "데이터 부족",
                    "description": "More clear footage would help provide better analysis.",
                    "description_ko": "더 선명한 영상이 있으면 더 나은 분석을 제공할 수 있습니다.",
                }
            ],
            "recommendations": [
                {
                    "title": "Shadow Boxing Drills",
                    "title_ko": "섀도우 복싱 드릴",
                    "description": "Practice 3 rounds of shadow boxing daily, focusing on form over speed.",
                    "description_ko": "매일 3라운드의 섀도우 복싱을 연습하고, 속도보다 자세에 집중하세요.",
                    "priority": "high",
                }
            ],
            "llm_model": "fallback",
            "error": error,
        }


# Singleton instance
gpt_analyzer = GPTAnalyzer()
