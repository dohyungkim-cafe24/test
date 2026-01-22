# Implementation Notes: F007 - LLM Strategic Analysis

## Summary

Implemented LLM-based strategic coaching analysis for boxing videos. The implementation includes:
- Report model for storing analysis results
- Report schemas for API validation
- LLM Analysis Service with retry logic and experience-level adaptation
- Comprehensive unit tests covering all acceptance criteria

## Inputs

Files consulted:
- `docs/engineering/DATA_MODEL.md` - Report table schema definition
- `specs/bdd/processing.feature` - BDD scenarios for F007
- `plan.md` (lines 470-518) - F007 implementation notes
- `backend/api/models/analysis.py` - Existing model patterns
- `backend/api/models/stamp.py` - Stamp model for reference
- `backend/api/schemas/analysis.py` - Schema patterns
- `backend/api/schemas/stamp.py` - Stamp schema patterns
- `backend/api/services/processing_service.py` - Service patterns
- `backend/tests/test_processing.py` - Test patterns
- `backend/api/config.py` - Configuration patterns

## Approach

1. **TDD Workflow**: Started with failing tests, then implemented code to pass
2. **Model First**: Created Report model following DATA_MODEL.md schema
3. **Schemas Second**: Created Pydantic schemas for validation
4. **Service Last**: Implemented LLM service with all AC requirements
5. **Experience Adaptation**: Context-aware prompts for each experience level

## Changes

### 1. Report Model (`backend/api/models/report.py`)
- SQLAlchemy model matching DATA_MODEL.md schema
- All required fields: performance_score, overall_assessment, strengths, weaknesses, recommendations, metrics
- LLM metadata fields: llm_model, prompt_tokens, completion_tokens
- AI disclaimer with default text (AC-040)
- Property-based disclaimer to ensure default is always available

### 2. Report Schemas (`backend/api/schemas/report.py`)
- `StrengthItem`, `WeaknessItem`, `RecommendationItem` schemas
- `MetricValue` and `MetricsData` for derived metrics (AC-036)
- `ReportCreate` and `ReportResponse` for API
- `LLMAnalysisInput` and `LLMAnalysisOutput` for LLM interface

### 3. LLM Analysis Service (`backend/api/services/llm_analysis_service.py`)
- `format_prompt()` - Formats pose data and stamps as JSON for LLM (AC-035)
- `calculate_metrics()` - Calculates derived metrics (AC-036):
  - punch_frequency (punches per 10 seconds)
  - guard_recovery_speed (seconds)
  - combination_frequency (combinations per minute)
  - defense_ratio
- Experience level adaptation (AC-038):
  - Beginner: friendly terminology, fundamental focus
  - Intermediate: standard terminology, consistency focus
  - Advanced: technical terminology, refinement focus
  - Competitive: advanced strategic terminology
- Retry logic with exponential backoff (AC-039):
  - 3 retries maximum
  - Base delay: 1s, 2s, 4s (exponential)
- Response parsing with 3-5 item validation (AC-037)

### 4. Database Update (`backend/api/services/database.py`)
- Added import for report model in `init_db()`
- Added import for stamp model (was missing)

### 5. Tests (`backend/tests/test_llm_analysis.py`)
- 14 tests covering all acceptance criteria
- TestReportModel: Model creation and disclaimer
- TestReportSchemas: Schema validation
- TestLLMAnalysisService: Service methods and behavior
- TestLLMAnalysisIntegration: Full flow integration

## Decisions

### Retry Strategy
- Chose exponential backoff (1s, 2s, 4s) for balance between responsiveness and API protection
- 3 retries matches BDD scenario requirement

### Metric Benchmarks
- Created benchmark ranges per experience level for accurate percentile calculation
- Used linear interpolation for percentile calculation (simple, effective)

### Prompt Structure
- JSON-focused prompt with explicit format specification
- Used `response_format={"type": "json_object"}` for reliable parsing
- Low temperature (0.3) for consistency in coaching advice

### Disclaimer Implementation
- Used property-based approach to ensure disclaimer is never None
- Database default + Python property provides dual protection

## Risks / Follow-ups

1. **OpenAI Dependency**: Service requires `openai` package and API key
   - Consider adding fallback or mock mode for offline development

2. **Metric Calculation Accuracy**: Current metrics are estimates based on stamp timestamps
   - May need refinement with real video data

3. **Token Usage**: No token limit enforcement beyond OpenAI's max_tokens
   - Consider adding prompt truncation for very long videos

4. **Integration Testing**: Full integration with pose estimation and stamps not yet tested
   - Recommend runtime testing with real data in `/agi-test` phase

5. **Error Codes**: Added `LLM_RETRY_EXHAUSTED` but not yet added to `processing_service.ERROR_CODES`
   - Should be added when integrating with full pipeline
