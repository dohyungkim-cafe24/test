# Code Review: F002 - Video Upload (Iteration 2)

## Verdict
APPROVE

## Summary

The IDOR vulnerability identified in the previous review has been **successfully remediated**. All upload service methods now require and verify `user_id` ownership. The fix is correctly implemented with proper error handling that prevents enumeration attacks. The implementation is ready for merge with a few minor observations noted below.

## Findings

### Blockers

None. The critical IDOR vulnerability has been fixed.

### Majors

1. **Rate Limiting Still Missing** (carried forward)
   - **Location**: `backend/api/routers/upload.py`
   - **Issue**: API spec specifies rate limits (5 initiate/hour, 1000 chunks/hour) which are not implemented.
   - **Status**: This is pre-existing and acceptable for initial merge; should be addressed in a follow-up.

2. **No Cleanup of Expired Sessions** (carried forward)
   - **Location**: `backend/api/services/upload_service.py`
   - **Issue**: No background task for cleaning up expired sessions/chunks.
   - **Status**: Acceptable for initial merge; create follow-up task.

### Minors

1. **MD5 Validation Not Enforced** (carried forward)
   - **Location**: `backend/api/services/upload_service.py` line 162-163
   - **Issue**: If client provides `content_md5`, it should be validated against calculated hash.

2. **Test Coverage Relies on Mocking**
   - **Location**: `backend/tests/test_upload.py`
   - **Issue**: Tests mock `_get_session` which means the ownership check itself is not directly tested in unit tests. An integration test would provide stronger assurance.
   - **Recommendation**: Add at least one integration test that attempts cross-user access and verifies 404.

## Required Fixes

None required for approval. The BLOCKER from the previous review is resolved.

## IDOR Fix Verification

The fix is complete and correctly implemented:

| Component | Change | Verified |
|-----------|--------|----------|
| `_get_session()` | Added `user_id` parameter and ownership check (lines 339-371) | Yes |
| `upload_chunk()` | Added `user_id` parameter, passes to `_get_session()` (lines 127, 148) | Yes |
| `complete_upload()` | Added `user_id` parameter, passes to `_get_session()` (lines 199, 215) | Yes |
| `cancel_upload()` | Added `user_id` parameter, passes to `_get_session()` (lines 256, 272) | Yes |
| `get_upload_status()` | Added `user_id` parameter, passes to `_get_session()` (lines 291, 303) | Yes |
| `get_received_chunks()` | Added `user_id` parameter, passes to `_get_session()` (lines 325, 336) | Yes |
| Router endpoints | All extract `user_id` from `current_user` and pass to service (lines 107, 161, 205, 240, 280) | Yes |

**Security design choices (correct)**:
- Ownership failure returns `SessionNotFoundError` (same as not-found), preventing enumeration
- Error message is identical: `"Upload session not found: {upload_id}"`

## Evidence

| File | Lines | Observation |
|------|-------|-------------|
| `backend/api/services/upload_service.py` | 339-383 | `_get_session()` now requires `user_id` and verifies ownership at line 370-371 |
| `backend/api/services/upload_service.py` | 121-128 | `upload_chunk()` signature includes `user_id: UUID` |
| `backend/api/services/upload_service.py` | 195-200 | `complete_upload()` signature includes `user_id: UUID` |
| `backend/api/services/upload_service.py` | 253-258 | `cancel_upload()` signature includes `user_id: UUID` |
| `backend/api/services/upload_service.py` | 287-292 | `get_upload_status()` signature includes `user_id: UUID` |
| `backend/api/services/upload_service.py` | 320-325 | `get_received_chunks()` signature includes `user_id: UUID` |
| `backend/api/routers/upload.py` | 107, 116-117 | `upload_chunk` endpoint extracts and passes `user_id` |
| `backend/api/routers/upload.py` | 161, 165-169 | `complete_upload` endpoint extracts and passes `user_id` |
| `backend/api/routers/upload.py` | 205, 209-212 | `cancel_upload` endpoint extracts and passes `user_id` |
| `backend/api/routers/upload.py` | 240, 244-248 | `get_upload_status` endpoint extracts and passes `user_id` |
| `backend/api/routers/upload.py` | 280, 284-288 | `get_received_chunks` endpoint extracts and passes `user_id` |
| `backend/tests/test_upload.py` | 197, 212-214, 277-281, 296-309 | Tests updated with `user_id` in mock sessions |

## Inputs

- `backend/api/routers/upload.py`
- `backend/api/services/upload_service.py`
- `backend/tests/test_upload.py`
- `specs/bdd/upload.feature`
- Previous CODE_REVIEW.md (attempt 20260121T142752Z-0bf3-review)
