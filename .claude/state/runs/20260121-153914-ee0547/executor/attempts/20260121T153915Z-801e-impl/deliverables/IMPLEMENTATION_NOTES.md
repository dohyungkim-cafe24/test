# Implementation Notes - F004 Body Specification Input

## Summary

Implemented F004 Body Specification Input feature following TDD methodology. The implementation includes backend API endpoints for creating body specs and prefilling form data for returning users, with full validation and IDOR prevention.

## Inputs

Files consulted:
- `specs/bdd/body-specs.feature` - BDD scenarios for validation requirements
- `docs/engineering/API.md` - API endpoint specifications (from task context)
- `docs/engineering/DATA_MODEL.md` - Database schema (from task context)
- `backend/api/schemas/subject.py` - Existing schema patterns
- `backend/api/services/subject_service.py` - Service pattern with IDOR prevention
- `backend/api/routers/subject.py` - Router pattern
- `backend/api/models/user.py` - User model with body_specs columns
- `backend/api/models/upload.py` - Video model reference
- `backend/tests/test_subject.py` - Test patterns

## Approach

1. **TDD RED Phase**: Wrote 24 failing tests covering:
   - Schema validation (enums, field constraints)
   - Service business logic (IDOR prevention, profile persistence)
   - Router endpoints (auth, validation, error handling)

2. **TDD GREEN Phase**: Implemented minimal code to pass tests:
   - `api/schemas/body_specs.py` - Pydantic schemas with validation
   - `api/models/body_specs.py` - SQLAlchemy model with constraints
   - `api/services/body_specs_service.py` - Business logic service
   - `api/routers/body_specs.py` - FastAPI router

3. **TDD REFACTOR Phase**: Verified no regressions in existing tests

## Changes

### New Files
- `backend/api/schemas/body_specs.py` - Request/response schemas
  - `ExperienceLevel` enum (beginner|intermediate|advanced|competitive)
  - `Stance` enum (orthodox|southpaw)
  - `BodySpecsCreate` schema with height (100-250cm), weight (30-200kg) validation
  - `BodySpecsResponse` schema
  - `PrefillResponse` schema

- `backend/api/models/body_specs.py` - Database model
  - `BodySpecs` SQLAlchemy model with CHECK constraints

- `backend/api/services/body_specs_service.py` - Service layer
  - `create_body_specs()` - Creates specs with IDOR check, persists to user profile
  - `get_prefill()` - Returns user's saved specs for form pre-fill

- `backend/api/routers/body_specs.py` - API endpoints
  - `POST /api/v1/analysis/body-specs/{video_id}` - Create body specs
  - `GET /api/v1/analysis/body-specs/prefill` - Get prefill data

- `backend/tests/test_body_specs.py` - 24 test cases

### Modified Files
- `backend/api/main.py` - Registered body_specs router
- `backend/api/services/database.py` - Added body_specs model import for table creation

## Decisions

1. **Enum validation over string validation**: Used Pydantic enums for experience_level and stance to get automatic validation and clear API documentation.

2. **Video-scoped body specs**: Each body_specs record is tied to a video_id, allowing different specs per analysis while persisting to user profile for prefill.

3. **Prefill endpoint as separate route**: Implemented as `GET /prefill` rather than in user profile to keep concerns separate and maintain clear API boundaries.

4. **IDOR prevention pattern**: Followed existing subject_service pattern - same "Video not found" error for both missing and unauthorized access to prevent enumeration.

5. **Profile persistence by default**: Body specs always persist to user profile (persist_to_profile: true) as specified in API contract, enabling AC-024 returning user prefill.

## Risks / Follow-ups

1. **Frontend integration**: Frontend components not yet implemented (body-specs/[videoId]/page.tsx). Marked as "if time permits" in task.

2. **Database migration**: Model uses CHECK constraints that need proper migration in production PostgreSQL. Current implementation relies on SQLAlchemy create_all.

3. **Existing test environment**: Some test_auth.py tests error due to greenlet dependency issue (pre-existing, not related to this change).

4. **Decimal handling**: BDD scenario mentions rounding "175.5" to "176" - current implementation uses integers only. Frontend should handle rounding before submission.
