# Security Review: F006 - Stamp Generation

## Verdict
PASS

## Threat model (lightweight)

### Assets
- **Pose data**: JSON with joint coordinates - moderate sensitivity (could reveal user biometrics)
- **Stamp records**: Detected actions stored in DB - low sensitivity
- **Analysis session**: Links user to video/stamps - requires auth

### Entry points
1. **Internal**: `StampGenerationService.generate_stamps()` called from processing pipeline (not direct API)
2. **Internal**: `StampDetectionService.detect_*()` receives pose data from upstream service
3. **DB operations**: Via SQLAlchemy ORM with parameterized queries

### Trust boundaries
- Pose data arrives from internal pose estimation service (F005)
- No direct user input reaches stamp generation
- DB access through authenticated session with user_id binding

### Attacker goals
- DoS via malformed pose data causing crashes
- Data injection via pose data manipulation
- Unauthorized access to other users' stamps

## Findings

### Security Issues
None critical.

### Low-Risk Observations

1. **L-001: No explicit rate limiting on stamp generation**
   - **Impact**: DoS via repeated analysis requests is mitigated upstream (video upload limits)
   - **Status**: Acceptable - rate limiting exists at API layer for uploads

2. **L-002: JSON fields store arbitrary dicts**
   - **Files**: `stamp.py:115-116` (`velocity_vector`, `trajectory_data`)
   - **Issue**: JSONB columns accept any dict/list structure
   - **Mitigation**: Data originates from internal detection service, not user input
   - **Recommendation**: Consider schema validation if these fields are ever exposed in queries

3. **L-003: Logging includes analysis_id**
   - **Files**: `stamp_generation_service.py:113-116, 138-144`
   - **Issue**: UUID logged in info level - acceptable for debugging
   - **Mitigation**: No PII in logs, UUIDs are not secret

## Required changes
None.

## Positive security observations

1. **Parameterized queries**: All DB operations use SQLAlchemy ORM (`stamp_generation_service.py:162-167`) - no SQL injection risk

2. **Input validation at schema layer**: `StampCreate` schema (`stamp.py:31-72`) enforces:
   - `confidence` bounded 0.0-1.0 (line 47)
   - `action_type` validated against allowlist (lines 56-64)
   - `side` validated against allowlist (lines 66-72)
   - `timestamp_seconds` >= 0 (line 38)
   - `frame_number` >= 0 (line 41)

3. **Foreign key constraints**: Stamps reference `analysis_id` with CASCADE delete (`stamp.py:99-101`) - no orphan records

4. **No user input in detection logic**: Kinematic analysis operates on structured pose data from internal service, not raw user input

5. **UUID primary keys**: No sequential IDs that could leak record counts

## Evidence

**Input Validation**: `StampCreate` schema enforces bounds and allowlists (stamp.py:31-72)

**SQL Injection**: ORM-only queries - `select(Stamp).where(Stamp.analysis_id == analysis_id)` (stamp_generation_service.py:162-167, 235-238)

**Authorization**: Stamps are tied to `analysis_id` which is tied to `user_id` - access control enforced upstream

**No secrets in code**: Reviewed all files - no hardcoded credentials or API keys

## Inputs

Files reviewed:
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/models/stamp.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/schemas/stamp.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/services/stamp_detection_service.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/services/stamp_generation_service.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/tests/test_stamp_generation.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/docs/engineering/DATA_MODEL.md`
