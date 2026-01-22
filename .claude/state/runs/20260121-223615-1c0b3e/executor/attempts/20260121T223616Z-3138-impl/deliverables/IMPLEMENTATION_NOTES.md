# Implementation Notes - F005 Pose Estimation Processing

## Summary

Implemented the Analysis model, schemas, processing service, and router for feature F005 (Pose Estimation Processing). This feature enables tracking of video analysis pipeline status with 33-joint MediaPipe pose estimation tracking.

## Inputs

Files consulted for implementation:

- `docs/engineering/ARCHITECTURE.md` - System architecture, pipeline stages
- `docs/engineering/DATA_MODEL.md` - Analysis table schema, status values
- `docs/engineering/API.md` - API endpoints specification
- `specs/bdd/processing.feature` - BDD scenarios for F005
- `backend/api/models/user.py` - SQLAlchemy model patterns
- `backend/api/models/subject.py` - Model patterns with JSON columns
- `backend/api/schemas/subject.py` - Pydantic schema patterns
- `backend/api/services/subject_service.py` - Service layer patterns
- `backend/api/routers/subject.py` - Router patterns
- `backend/tests/conftest.py` - Test fixture patterns

## Approach

**TDD Methodology (Red -> Green -> Refactor)**

1. **RED**: Wrote 18 failing tests covering:
   - AnalysisStatus enum values
   - Analysis model creation and status transitions
   - Schema validation for requests/responses
   - Service layer functions (placeholders)
   - Pose data structure (33 joints, XYZ coordinates)
   - Router endpoint definitions

2. **GREEN**: Implemented minimal code:
   - `api/models/analysis.py` - Analysis SQLAlchemy model with status tracking
   - `api/schemas/analysis.py` - Pydantic schemas for API validation
   - `api/services/processing_service.py` - Business logic for pipeline
   - `api/routers/processing.py` - FastAPI endpoints

3. **REFACTOR**: Fixed SQLAlchemy default value handling, improved test coverage

## Changes

### New Files

| File | Description |
|------|-------------|
| `backend/api/models/analysis.py` | Analysis model with AnalysisStatus enum |
| `backend/api/schemas/analysis.py` | Request/response schemas for processing |
| `backend/api/services/processing_service.py` | Processing pipeline service |
| `backend/api/routers/processing.py` | API endpoints for start/status |
| `backend/tests/test_processing.py` | 18 unit tests for F005 |

### Modified Files

| File | Change |
|------|--------|
| `backend/api/main.py` | Added processing router import and inclusion |
| `backend/api/services/database.py` | Added analysis model import for table creation |

## Decisions

### 1. Status Property Pattern

Used a property/setter pattern for `status` field to allow both enum and string access while storing string in DB. This provides type safety at runtime while maintaining SQLAlchemy compatibility.

```python
@property
def status(self) -> AnalysisStatus:
    return AnalysisStatus(self._status) if self._status else AnalysisStatus.QUEUED

@status.setter
def status(self, value: AnalysisStatus | str) -> None:
    if isinstance(value, AnalysisStatus):
        self._status = value.value
    else:
        self._status = value
```

**Rationale**: SQLAlchemy's Mapped types work best with Python primitives. Using a property provides the enum type safety we want while storing strings in the database.

### 2. 20% Frame Failure Threshold

Implemented `should_fail_for_quality()` method with default 20% threshold per AC-028. Made threshold configurable for future tuning.

**Rationale**: Hard-coding 20% matches the spec, but making it configurable allows adjustment based on real-world data.

### 3. Separate Pose Data Schema

Created comprehensive `PoseData`, `PoseFrame`, and `JointCoordinate` schemas for structured pose storage per AC-027.

**Rationale**: Strong typing for pose data enables:
- Validation of 33 joints per frame
- XYZ coordinate bounds checking
- Subject tracking metadata

### 4. Router Test Strategy

Used schema/route validation tests instead of full integration tests due to greenlet dependency issue in test environment.

**Rationale**: The existing test suite has a known greenlet issue. New tests focus on what can be reliably tested without that dependency.

## Risks / Follow-ups

1. **Celery Worker Integration**: The `processing_service` is designed for API-level operations. Actual pose estimation will be performed by Celery workers (F005 implementation continuation).

2. **WebSocket Endpoint**: The `websocket_url` is generated but the WebSocket handler is not yet implemented. Requires future implementation for real-time status updates.

3. **Greenlet Dependency**: Pre-existing test infrastructure issue. Some tests in `test_auth.py` fail with greenlet import error. Not related to F005 changes.

4. **MediaPipe Integration**: The pose estimation service placeholder exists but actual MediaPipe processing is part of the worker implementation (separate from API layer).

## Acceptance Criteria Mapping

| AC | Implementation |
|----|----------------|
| AC-025 | `JointCoordinate` schema with joint_id (0-32), x, y, z, visibility |
| AC-026 | `Subject` model with tracking fields, `PoseData.tracking` metadata |
| AC-027 | `PoseData` schema for S3 JSON storage |
| AC-028 | `Analysis.should_fail_for_quality(threshold=0.20)` method |
| AC-029 | `GET /processing/status/{analysis_id}` endpoint with stage details |
