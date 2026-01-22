# F003 Subject Selection - Implementation Notes

## Summary

Implemented backend API endpoints for F003 Subject Selection feature, including:
- `GET /api/v1/analysis/thumbnails/{video_id}` - Get extracted thumbnails with detected persons
- `POST /api/v1/analysis/subject/{video_id}` - Select analysis subject from thumbnail

All acceptance criteria (AC-013 through AC-017) are addressed in the implementation.

## Inputs

Files consulted:
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/specs/bdd/subject-selection.feature` - BDD scenarios
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/docs/engineering/DATA_MODEL.md` - Data models (Thumbnail, Subject)
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/schemas/upload.py` - Existing schema patterns
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/models/upload.py` - Existing model patterns
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/routers/upload.py` - Existing router patterns
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/services/upload_service.py` - Existing service patterns
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/tests/test_upload.py` - Existing test patterns

## Approach

TDD approach (Red-Green-Refactor):
1. Wrote failing tests first covering all acceptance criteria and BDD scenarios
2. Implemented schemas, models, service, and router to make tests pass
3. Verified no regressions in existing tests

Architecture follows existing patterns from F001/F002:
- Pydantic schemas for request/response validation
- SQLAlchemy models with proper indexes and constraints
- Service layer for business logic with proper error handling
- Router layer for HTTP endpoint definitions
- Comprehensive unit tests with mocked dependencies

## Changes

### New Files

1. **`backend/api/schemas/subject.py`**
   - `BoundingBox` - Coordinate validation for detected persons
   - `DetectedPerson` - Person detection data with confidence
   - `ThumbnailResponse` - Single thumbnail with detected persons
   - `ThumbnailsResponse` - Full thumbnails endpoint response with auto-select
   - `SubjectSelectRequest` - Subject selection request
   - `SubjectSelectResponse` - Subject selection response with bounding box

2. **`backend/api/models/subject.py`**
   - `Thumbnail` - Extracted video frames with detected persons (JSONB)
   - `Subject` - Selected analysis subject with initial bounding box

3. **`backend/api/services/subject_service.py`**
   - `SubjectService` - Business logic for thumbnails and subject selection
   - Handles: processing state, no-subjects state, auto-selection for single person
   - Custom exceptions: `VideoNotFoundError`, `ThumbnailNotFoundError`, `PersonNotFoundError`

4. **`backend/api/routers/subject.py`**
   - `GET /api/v1/analysis/thumbnails/{video_id}` - Thumbnails endpoint
   - `POST /api/v1/analysis/subject/{video_id}` - Subject selection endpoint

5. **`backend/tests/test_subject.py`**
   - 21 tests covering schemas, service, and router
   - Tests for all acceptance criteria and edge cases

### Modified Files

1. **`backend/api/main.py`**
   - Registered subject router with `/api/v1` prefix

2. **`backend/api/services/database.py`**
   - Added import for subject models to register with Base.metadata

## Decisions

1. **JSON vs JSONB for detected_persons**
   - Used `sqlalchemy.types.JSON` for SQLite compatibility in tests
   - PostgreSQL will automatically use JSONB for better performance

2. **Unique person_id tracking across thumbnails**
   - Tracks unique person IDs across all thumbnails to determine total persons
   - Enables correct auto-select behavior for single-person videos

3. **Subject update vs create**
   - Checking for existing subject before creating new one
   - Allows selection change without creating duplicate records (AC-016)

4. **Float type for timestamp_seconds**
   - Used `Float` instead of `Real` for broader SQLAlchemy compatibility

## Risks / Follow-ups

1. **Person detection not implemented**
   - Current implementation expects `detected_persons` to be populated externally
   - Actual person detection (OpenCV/YOLO) should be implemented in video processing pipeline

2. **Thumbnail extraction not implemented**
   - Thumbnails need to be generated during video upload processing
   - Should extract 6-9 frames at regular intervals after upload completes

3. **Storage URL generation**
   - `_get_image_url` returns placeholder URLs
   - Production should generate signed URLs for S3/CDN

4. **Frontend components not implemented**
   - `ThumbnailGrid.tsx`, `PersonSelector.tsx`, and page component still needed
   - API is ready for frontend integration

## Test Coverage

All 21 tests pass:
- 9 schema validation tests
- 7 service business logic tests
- 5 router endpoint tests

Coverage includes:
- Happy paths for all acceptance criteria
- Edge cases: no subjects detected, single person auto-select
- Error handling: video not found, person not found, invalid inputs
- Authentication requirements verified
