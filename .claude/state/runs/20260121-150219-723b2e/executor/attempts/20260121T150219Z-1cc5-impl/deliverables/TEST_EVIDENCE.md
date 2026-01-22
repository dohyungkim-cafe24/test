# F003 Subject Selection - Test Evidence

## Inputs

Test specifications derived from:
- `specs/bdd/subject-selection.feature` - BDD scenarios
- Acceptance Criteria: AC-013, AC-014, AC-015, AC-016, AC-017

## Commands

### Test Execution

```bash
export PYTHONPATH=/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend
cd /Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend
/tmp/test-venv/bin/pytest tests/test_subject.py -v --tb=short
```

### Output

```
============================= test session starts ==============================
platform darwin -- Python 3.13.5, pytest-9.0.2, pluggy-1.6.0 -- /private/tmp/test-venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend
configfile: pyproject.toml
plugins: anyio-4.12.1, asyncio-1.3.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 21 items

tests/test_subject.py::TestSubjectSchemas::test_bounding_box_valid PASSED [  4%]
tests/test_subject.py::TestSubjectSchemas::test_bounding_box_negative_coordinates_rejected PASSED [  9%]
tests/test_subject.py::TestSubjectSchemas::test_bounding_box_zero_dimensions_rejected PASSED [ 14%]
tests/test_subject.py::TestSubjectSchemas::test_detected_person_valid PASSED [ 19%]
tests/test_subject.py::TestSubjectSchemas::test_detected_person_confidence_range PASSED [ 23%]
tests/test_subject.py::TestSubjectSchemas::test_thumbnail_response_valid PASSED [ 28%]
tests/test_subject.py::TestSubjectSchemas::test_thumbnails_response_valid PASSED [ 33%]
tests/test_subject.py::TestSubjectSchemas::test_subject_select_request_valid PASSED [ 38%]
tests/test_subject.py::TestSubjectSchemas::test_subject_select_response_valid PASSED [ 42%]
tests/test_subject.py::TestSubjectService::test_get_thumbnails_returns_frames PASSED [ 47%]
tests/test_subject.py::TestSubjectService::test_get_thumbnails_processing_state PASSED [ 52%]
tests/test_subject.py::TestSubjectService::test_get_thumbnails_no_persons_detected PASSED [ 57%]
tests/test_subject.py::TestSubjectService::test_select_subject_stores_bounding_box PASSED [ 61%]
tests/test_subject.py::TestSubjectService::test_select_subject_updates_existing_selection PASSED [ 66%]
tests/test_subject.py::TestSubjectService::test_single_person_auto_selected PASSED [ 71%]
tests/test_subject.py::TestSubjectService::test_select_subject_invalid_person_id PASSED [ 76%]
tests/test_subject.py::TestSubjectRouter::test_get_thumbnails_requires_auth PASSED [ 80%]
tests/test_subject.py::TestSubjectRouter::test_get_thumbnails_video_not_found PASSED [ 85%]
tests/test_subject.py::TestSubjectRouter::test_get_thumbnails_success PASSED [ 90%]
tests/test_subject.py::TestSubjectRouter::test_select_subject_success PASSED [ 95%]
tests/test_subject.py::TestSubjectRouter::test_select_subject_person_not_found PASSED [100%]

============================== 21 passed in 0.31s ==============================
```

### Regression Check (F002 Upload Tests)

```bash
/tmp/test-venv/bin/pytest tests/test_upload.py -v --tb=short
```

```
======================== 22 passed, 3 warnings in 0.30s ========================
```

## Test Coverage by Acceptance Criteria

### AC-013: Thumbnail grid displays after upload completes
- `test_get_thumbnails_returns_frames` - Verifies thumbnails endpoint returns frames with detected persons
- `test_get_thumbnails_success` - Verifies API endpoint returns correct response

### AC-014: Tap on person highlights with selection indicator
- `test_detected_person_valid` - Validates DetectedPerson schema
- `test_bounding_box_valid` - Validates BoundingBox coordinates
- Frontend component (ThumbnailGrid) not yet implemented

### AC-015: Confirm selection stores bounding box for tracking
- `test_select_subject_stores_bounding_box` - Verifies bounding box is stored in Subject record
- `test_select_subject_success` - Verifies API returns bounding box in response

### AC-016: Selection can be changed before confirmation
- `test_select_subject_updates_existing_selection` - Verifies existing subject is updated, not duplicated

### AC-017: Single person auto-selected with confirm option
- `test_single_person_auto_selected` - Verifies auto_select info is returned for single-person videos
- `test_thumbnails_response_valid` - Validates ThumbnailsResponse schema with auto_select field

## Edge Cases Tested

1. **Processing state** - `test_get_thumbnails_processing_state`
   - Returns status="processing" with "Extracting frames..." message

2. **No subjects detected** - `test_get_thumbnails_no_persons_detected`
   - Returns status="no_subjects" with guidance message

3. **Invalid person_id** - `test_select_subject_invalid_person_id`
   - Raises PersonNotFoundError (404)

4. **Video not found** - `test_get_thumbnails_video_not_found`
   - Returns 404 Not Found

5. **Authentication required** - `test_get_thumbnails_requires_auth`
   - Returns 401 Unauthorized without token

## Validation Status

| Criterion | Tests | Status |
|-----------|-------|--------|
| AC-013 | 2 | PASS |
| AC-014 | 2 | PASS (API only; frontend pending) |
| AC-015 | 2 | PASS |
| AC-016 | 1 | PASS |
| AC-017 | 2 | PASS |
| Edge cases | 5 | PASS |
| Schema validation | 9 | PASS |

**Total: 21 tests, 21 passed**
