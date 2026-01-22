# Code Review: F002 - Video Upload

## Verdict
REQUEST_CHANGES

## Summary

F002 Video Upload implementation is well-structured with good separation of concerns across router, service, schemas, and models. The chunked upload pattern with resumability is correctly implemented. However, there is a **critical security issue** (IDOR vulnerability) that must be addressed before approval, and a few moderate issues affecting robustness.

## Findings

### Blockers

1. **IDOR Vulnerability in Upload Endpoints** (SECURITY)
   - **Location**: `backend/api/routers/upload.py` lines 86-286, `backend/api/services/upload_service.py`
   - **Issue**: Endpoints for chunk upload, complete, cancel, status, and get_received_chunks do not verify that the `current_user` owns the upload session. Any authenticated user can manipulate another user's upload by guessing or enumerating `upload_id`.
   - **Impact**: Attackers can cancel other users' uploads, upload chunks to others' sessions, or complete uploads on behalf of others.
   - **Fix**: Add `user_id` check in `_get_session()` or pass `user_id` to all service methods and verify ownership:
     ```python
     # In upload_service.py _get_session():
     if upload_session.user_id != user_id:
         raise SessionNotFoundError(f"Upload session not found: {upload_id}")
     ```

### Majors

1. **Missing Rate Limiting for Upload Endpoints**
   - **Location**: `backend/api/routers/upload.py`
   - **Issue**: API spec (API.md lines 1096-1097) specifies rate limits: "Upload initiate: 5 requests/1 hour" and "Upload chunk: 1000 requests/1 hour". These are not implemented.
   - **Impact**: Users could abuse the upload system, causing storage exhaustion or DoS.
   - **Fix**: Implement rate limiting middleware or use a library like `slowapi`.

2. **Session Status Check Allows `completed` Status in `_get_session`**
   - **Location**: `backend/api/services/upload_service.py` line 364
   - **Issue**: The status check `if upload_session.status not in ("active",)` will reject completed sessions, but complete_upload and cancel_upload call `_get_session` which would fail on already completed/cancelled sessions. This is correct behavior but the `SessionExpiredError` message is misleading for cancelled sessions.
   - **Impact**: Confusing error messages for edge cases.
   - **Fix**: Use a more specific exception or message for cancelled sessions.

3. **No Cleanup of Expired Sessions**
   - **Location**: `backend/api/services/upload_service.py`, `backend/api/models/upload.py`
   - **Issue**: Sessions expire after 1 hour but there's no background task to clean up expired sessions and their associated chunks on disk.
   - **Impact**: Storage leak over time with orphaned chunks.
   - **Fix**: Implement a periodic cleanup job or handle cleanup on session access.

### Minors

1. **MD5 Validation Not Enforced**
   - **Location**: `backend/api/services/upload_service.py` line 161-162
   - **Issue**: If `content_md5` is provided by client, it should be validated against the calculated hash. Currently, it's just stored.
   - **Fix**: Compare provided MD5 with calculated and reject on mismatch.

2. **Frontend Abort Signal Not Used in Complete Call**
   - **Location**: `frontend/src/app/(protected)/upload/page.tsx` line 143-157
   - **Issue**: `handleCancel` aborts but doesn't call `cancelUpload` API - it only triggers abort signal. The `uploadVideo` function handles this correctly, but the race between abort and API call could leave server-side session active.
   - **Impact**: Potential orphaned server sessions.

3. **Test Coverage Could Be Improved**
   - **Location**: `backend/tests/test_upload.py`
   - **Issue**: Tests use extensive mocking which reduces confidence in integration. No tests for the IDOR scenario, no tests for session expiration, no tests for chunk integrity verification.
   - **Fix**: Add integration tests with actual database and test authorization scenarios.

## Required Fixes

1. **BLOCKER**: Implement user ownership verification in all upload endpoints
2. **MAJOR**: Implement rate limiting per API spec
3. **MAJOR**: Add cleanup mechanism for expired sessions

## Evidence

| File | Lines | Issue |
|------|-------|-------|
| `backend/api/routers/upload.py` | 86-136 | upload_chunk lacks user_id verification |
| `backend/api/routers/upload.py` | 149-180 | complete_upload lacks user_id verification |
| `backend/api/routers/upload.py` | 191-211 | cancel_upload lacks user_id verification |
| `backend/api/routers/upload.py` | 223-248 | get_upload_status lacks user_id verification |
| `backend/api/routers/upload.py` | 260-285 | get_received_chunks lacks user_id verification |
| `backend/api/services/upload_service.py` | 329-367 | _get_session does not verify user ownership |
| `docs/engineering/API.md` | 1096-1097 | Rate limits specified but not implemented |

## Inputs

- `backend/api/routers/upload.py`
- `backend/api/services/upload_service.py`
- `backend/api/schemas/upload.py`
- `backend/api/models/upload.py`
- `backend/tests/test_upload.py`
- `frontend/src/lib/upload/api.ts`
- `frontend/src/components/upload/UploadDropzone.tsx`
- `frontend/src/components/upload/UploadProgress.tsx`
- `frontend/src/app/(protected)/upload/page.tsx`
- `specs/bdd/upload.feature`
- `docs/engineering/API.md`
- `docs/engineering/DATA_MODEL.md`
- `features.json`
