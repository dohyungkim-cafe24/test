# CODE_REVIEW.md

## Verdict
APPROVE

## Summary

F003 Subject Selection implementation is well-structured with proper separation of concerns across schemas, models, service, and router layers. The code correctly implements all five acceptance criteria (AC-013 through AC-017), follows established patterns from F001/F002, and includes comprehensive test coverage.

## Findings

### Blockers
None.

### Majors
None.

### Minors

**m1: API contract mismatch with canonical API.md** (Low impact)
- Location: `routers/subject.py:73-76`
- Issue: API spec shows `POST /analysis/subject/{video_id}` with request body `{person_id, frame_number}`, but implementation uses `{thumbnail_id, person_id}` instead.
- Assessment: The implementation is correct since `thumbnail_id` is more precise than `frame_number`. The canonical API.md should be updated to reflect this during promotion.

**m2: Unused JSONB import** (Cosmetic)
- Location: `models/subject.py:12`
- Issue: `JSONB` is imported but not used (code uses `JSON` for SQLite compatibility).
- Suggestion: Remove unused import.

**m3: PersonNotFoundError leaks internal ID in HTTP response** (Minor info exposure)
- Location: `routers/subject.py:128-132`
- Issue: `str(e)` exposes `"Person p999 not found in thumbnail {uuid}"` which reveals internal IDs.
- Suggestion: Use a generic message like `"Selected person not found in thumbnail"`.

## Required fixes
None. All minors are nice-to-fix but not blocking.

## Evidence

### Acceptance Criteria Coverage

| AC | Description | Implementation | Test |
|----|-------------|----------------|------|
| AC-013 | Thumbnail grid displays | `get_thumbnails()` returns `ThumbnailsResponse` with frames | `test_get_thumbnails_returns_frames` |
| AC-014 | Tap on person highlights | Schema supports selection data | Schema tests pass |
| AC-015 | Confirm stores bounding box | `select_subject()` stores `initial_bbox` | `test_select_subject_stores_bounding_box` |
| AC-016 | Selection can change | `select_subject()` updates existing | `test_select_subject_updates_existing_selection` |
| AC-017 | Single person auto-select | `get_thumbnails()` returns `auto_select` | `test_single_person_auto_selected` |

### Code Quality Assessment

**Strengths:**
1. Proper video ownership verification in service layer (lines 271-302)
2. IDOR protection: `_get_video()` returns same error for non-existent and unauthorized access
3. Thumbnail-to-video validation in `_get_thumbnail()` (lines 325-354)
4. Person ID validation against `detected_persons` array (lines 219-230)
5. Proper async/await patterns throughout
6. Comprehensive schema validation with Pydantic Field constraints
7. Tests cover happy paths, error paths, and edge cases

**Patterns followed from F001/F002:**
- Router uses `get_current_user` dependency correctly
- Service layer handles business logic
- Context manager pattern for DB sessions
- Error mapping to appropriate HTTP status codes

### Test Quality

- 23 test cases covering schemas, service, and router layers
- Tests include auth requirement verification
- Tests use mocking appropriately for unit tests
- Both success and failure paths covered

## Inputs

- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/schemas/subject.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/models/subject.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/services/subject_service.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/routers/subject.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/tests/test_subject.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/specs/bdd/subject-selection.feature`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/docs/engineering/API.md`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/plan.md`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/routers/auth.py` (pattern reference)
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/routers/upload.py` (pattern reference)
