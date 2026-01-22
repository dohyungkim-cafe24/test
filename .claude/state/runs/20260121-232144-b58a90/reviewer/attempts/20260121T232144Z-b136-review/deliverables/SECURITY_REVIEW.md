# Security Review: F007 - LLM Strategic Analysis

## Verdict
PASS

## Threat model (lightweight)

### Assets
- **User pose/video data**: Sensitive personal training data sent to LLM
- **LLM API credentials**: OpenAI API key used for analysis
- **Generated analysis reports**: Coaching feedback stored in database
- **User body specifications**: Height, weight, experience level

### Entry points
1. `generate_analysis()` - Main entry point receiving pose data, stamps, body specs
2. `format_prompt()` - Constructs prompt from user data
3. `_call_llm_with_retry()` - External API call to OpenAI

### Trust boundaries
- Internal service (trusted) -> OpenAI API (external, semi-trusted)
- User data flows to external LLM provider
- LLM response is parsed and stored

### Attacker goals
- Exfiltrate user training data via prompt injection
- Inject malicious content into analysis reports
- Exhaust API quota via retry abuse
- Access unauthorized user data

## Findings

### No blockers or critical issues identified

### Observations (informational)

1. **API key handling** (line 128-129)
   - API key retrieved from environment variable `OPENAI_API_KEY`
   - This is the correct pattern; key is not logged or exposed
   - Status: PASS

2. **Structured output enforcement** (line 446)
   - Uses `response_format={"type": "json_object"}` to enforce JSON output
   - Reduces risk of unexpected LLM output injection
   - Status: PASS

3. **Input validation via Pydantic schemas**
   - All input/output schemas use Pydantic with field constraints
   - `min_length`, `max_length` constraints on text fields
   - `ge=0, le=100` constraints on score fields
   - Status: PASS

4. **No direct user input in prompts** (prompt injection mitigation)
   - User data (pose, stamps, body specs) is JSON-serialized, not interpolated as raw strings
   - Experience level uses an allowlist lookup (`EXPERIENCE_LEVEL_CONTEXTS`)
   - Prompt structure separates system instructions from user data
   - Status: PASS

5. **Retry limit enforced** (lines 118, 425)
   - Fixed `_max_retries = 3` prevents infinite retry loops
   - Prevents resource exhaustion attacks via repeated failures
   - Status: PASS

6. **Error messages** (lines 479-488)
   - Error logging includes last error but with `str(last_error)` which could leak stack traces
   - Low risk as this is server-side logging, not exposed to users
   - Recommendation: Consider sanitizing error details in logs
   - Status: ACCEPTABLE

7. **No PII in standard logs**
   - Logging statements (lines 427-434, 458-464, 600-608) log counts and metadata, not user data
   - Status: PASS

8. **Data sent to external LLM**
   - Pose data summaries and action stamps are sent to OpenAI
   - This is inherent to the feature design (LLM analysis)
   - Ensure privacy policy covers data sharing with AI providers
   - Status: ACCEPTABLE (business decision, not code issue)

## Required changes
None required.

## Evidence

### Input validation
- `StrengthItem`, `WeaknessItem`, `RecommendationItem` schemas enforce field lengths
- `MetricValue.percentile` constrained to 0-100
- `ReportCreate.performance_score` constrained to 0-100
- `ReportCreate.strengths/weaknesses/recommendations` constrained to 3-5 items

### Secret handling
- Line 128: `api_key=os.getenv("OPENAI_API_KEY")`
- No hardcoded credentials in source code

### Rate limiting / retry bounds
- Line 118: `self._max_retries = 3`
- Line 119: `self._base_delay = 1.0`
- Line 468: Exponential backoff `delay = self._base_delay * (2**attempt)`

### Output sanitization
- Line 446: `response_format={"type": "json_object"}` forces structured output
- Lines 504-550: Response parsing validates structure before use

## Inputs
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/services/llm_analysis_service.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/schemas/report.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/models/report.py`
