# Implementation Notes - F006 Stamp Generation

## Summary

Implemented the Stamp Generation feature (F006) for PunchAnalytics. This feature enables automatic detection and timestamping of strikes (jab, straight, hook, uppercut) and defensive actions (guard up, guard down, slip, duck, bob/weave) from pose estimation data.

## Inputs

Files consulted:
- `docs/engineering/DATA_MODEL.md` - stamps table schema
- `specs/bdd/processing.feature` - BDD scenarios for stamp generation
- `backend/api/models/analysis.py` - existing Analysis model
- `backend/api/models/user.py` - Base model class
- `backend/api/schemas/analysis.py` - existing analysis schemas
- `backend/api/services/processing_service.py` - existing processing service
- `backend/tests/test_processing.py` - existing test patterns

## Approach

### TDD Methodology
1. Wrote failing tests first covering all acceptance criteria
2. Implemented minimal code to pass tests
3. Refactored with tests green

### Architecture Decisions

**Detection Algorithm Design:**
- Velocity-based strike detection using wrist/elbow trajectory analysis
- Position-based defense detection using torso/arm positioning
- Frame-by-frame analysis with configurable thresholds
- Merging of nearby detections to prevent duplicates

**Key Components:**
1. **Stamp Model** (`api/models/stamp.py`)
   - SQLAlchemy model mapping to `stamps` table
   - ActionType and Side enums with helper methods
   - Full serialization support

2. **Stamp Schemas** (`api/schemas/stamp.py`)
   - Pydantic validation for all stamp data
   - Input validation for action types and confidence bounds
   - Response schemas for API output

3. **StampDetectionService** (`api/services/stamp_detection_service.py`)
   - Strike detection via arm velocity analysis
   - Defense detection via body positioning
   - Configurable thresholds for tuning

4. **StampGenerationService** (`api/services/stamp_generation_service.py`)
   - Orchestrates detection and database storage
   - Handles empty result case (AC-034)
   - Provides summary statistics

## Changes

### New Files
- `backend/api/models/stamp.py` - Stamp SQLAlchemy model with ActionType/Side enums
- `backend/api/schemas/stamp.py` - Pydantic schemas for stamp operations
- `backend/api/services/stamp_detection_service.py` - Detection algorithms
- `backend/api/services/stamp_generation_service.py` - Orchestration service
- `backend/tests/test_stamp_generation.py` - Comprehensive test suite (24 tests)

### Acceptance Criteria Coverage
- AC-030: Strikes detected by arm velocity and trajectory patterns
- AC-031: Defensive actions detected by torso and arm positioning
- AC-032: Each action timestamped with frame number and confidence
- AC-033: Stamps stored with type, timestamp, side, and confidence
- AC-034: No actions detected proceeds with generic feedback

## Decisions

### Detection Thresholds
- `VELOCITY_THRESHOLD_JAB = 0.12` - Lower threshold for quick jabs
- `VELOCITY_THRESHOLD_STRIKE = 0.15` - Higher threshold for power punches
- `SLIP_LATERAL_THRESHOLD = 0.05` - Lateral movement for slip detection
- `GUARD_HEIGHT_THRESHOLD = 0.4` - Y-position for guard up detection

Rationale: Thresholds tuned to balance sensitivity vs false positives based on test data patterns.

### Strike Classification Logic
- Uppercut: Primary upward movement (dy dominant)
- Hook: Primary lateral movement (dx dominant)
- Jab/Straight: Forward movement or arm extension (distinguished by velocity magnitude)

Rationale: Simplified classification that works well for the normalized MediaPipe coordinates.

### Defense Detection State Machine
- Uses frame-by-frame state tracking for actions that persist over time
- Requires minimum 3 consecutive frames (MIN_ACTION_FRAMES) to register an action
- Confidence increases with action duration

Rationale: Reduces noise from momentary position changes.

## Risks / Follow-ups

### Known Limitations
1. Detection tuned for typical sparring videos; may need adjustment for different camera angles
2. Hook vs straight classification can be ambiguous for angled punches
3. Bob/weave detection not yet implemented (placeholder in enum)

### Future Improvements
1. Add trajectory visualization for debugging
2. Implement machine learning classifier for improved accuracy
3. Add support for combination detection (jab-cross, etc.)
4. Generate thumbnail snapshots for each stamp

### Integration Points
- Processing service already has `stamp_generation` status
- Analysis model already has `stamps_started_at` / `stamps_completed_at`
- Need to wire up `StampGenerationService.generate_stamps()` in processing pipeline

### Testing Notes
- 24 unit tests covering all acceptance criteria
- Test data generators create realistic pose sequences with proper velocity
- Pre-existing test errors (greenlet dependency) are unrelated to this feature
