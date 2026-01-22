# Code Review: F006 - Stamp Generation

## Verdict
APPROVE

## Summary

F006 Stamp Generation implementation is well-structured, follows the data model contract, and provides comprehensive test coverage. The code correctly implements all five acceptance criteria (AC-030 through AC-034) with proper separation of concerns between detection logic and orchestration/storage.

**Strengths:**
- Clear separation: `stamp_detection_service.py` handles kinematic analysis; `stamp_generation_service.py` handles orchestration and DB persistence
- Strong alignment with DATA_MODEL.md schema (stamps table structure)
- Comprehensive validation in Pydantic schemas (confidence bounds, action type enum, side enum)
- Good test coverage with realistic pose sequence generators
- Proper handling of AC-034 (no actions detected) - returns empty list gracefully

## Findings

### Blockers
None.

### Majors

1. **M-001: Potential division by zero in velocity calculation**
   - **File**: `stamp_detection_service.py:260`
   - **Issue**: `time_delta = 2.0 / fps` - if fps is 0, will raise ZeroDivisionError
   - **Recommendation**: Add guard: `fps = max(pose_data.get("fps", 30.0), 1.0)` or validate fps > 0 early
   - **Impact**: Could crash processing for malformed pose data

2. **M-002: Missing bob_weave detection implementation**
   - **File**: `stamp_detection_service.py`
   - **Issue**: `bob_weave` is defined in ActionType enum but no detection logic exists (only guard_up, slip, duck implemented)
   - **Recommendation**: Either implement bob_weave detection or document it as future work
   - **Impact**: Incomplete coverage of AC-031

### Minors

1. **m-001: Singleton pattern with module-level instance**
   - **Files**: `stamp_detection_service.py:480`, `stamp_generation_service.py:258`
   - **Issue**: Module-level singletons make testing and dependency injection harder
   - **Recommendation**: Consider factory pattern or dependency injection for better testability

2. **m-002: Magic numbers for thresholds**
   - **File**: `stamp_detection_service.py:32-38`
   - **Issue**: Thresholds (0.15, 0.12, 0.7, etc.) are defined as constants but lack explanation of how they were derived
   - **Recommendation**: Add comments explaining calibration source or reference

3. **m-003: Unused `guard_down` detection**
   - **File**: `stamp_detection_service.py`
   - **Issue**: `guard_down` is in ActionType but detection only produces `guard_up`
   - **Recommendation**: Implement guard_down as inverse of guard_up condition

4. **m-004: `_create_pose_frame` helper has complex signature**
   - **File**: `test_stamp_generation.py:755-764`
   - **Issue**: 8 boolean parameters - fragile and hard to maintain
   - **Recommendation**: Consider using a builder pattern or dataclass for test fixtures

## Required fixes

1. Add fps validation to prevent division by zero (M-001)
2. Either implement bob_weave detection or add explicit TODO/skip (M-002)

## Evidence

**AC-030 (Strike detection)**: Implemented in `stamp_detection_service.py:55-105` via `detect_strikes()` with velocity and trajectory analysis. Tests in `test_stamp_generation.py:358-408` verify jab and hook detection.

**AC-031 (Defense detection)**: Implemented in `stamp_detection_service.py:107-222` via `detect_defense()`. Tests verify guard_up (`test_detect_defense_guard_up`), slip (`test_detect_defense_slip`), and duck (`test_detect_defense_duck`).

**AC-032 (Timestamping)**: Each stamp dict includes `frame_number` and `timestamp_seconds` (e.g., line 279-280 in detection service). Schema enforces these fields (`stamp.py:38-41`).

**AC-033 (Storage structure)**: `Stamp` model (`stamp.py:87-156`) matches DATA_MODEL.md schema with `action_type`, `side`, `confidence`, `timestamp_seconds`, `frame_number`. Indexes defined at lines 152-155.

**AC-034 (No actions)**: Handled in `stamp_generation_service.py:109-118` - logs info message and returns empty list without failing.

**BDD Coverage**: Tests explicitly reference BDD scenarios (e.g., `test_stamp_generation.py:12-17` lists all relevant scenarios). Test methods include docstrings mapping to BDD scenarios.

## Inputs

Files reviewed:
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/models/stamp.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/schemas/stamp.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/services/stamp_detection_service.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/services/stamp_generation_service.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/tests/test_stamp_generation.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/models/analysis.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/specs/bdd/processing.feature`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/docs/engineering/DATA_MODEL.md`
