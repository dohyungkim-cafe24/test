# Security Review: F002 - Video Upload

## Verdict
NEEDS_CHANGES

## Threat Model (Lightweight)

### Assets
- **User video files**: Private sparring footage (sensitive)
- **Upload sessions**: Metadata linking videos to users
- **Storage infrastructure**: Disk/S3 storage for chunks and assembled videos
- **User identity/session**: JWT tokens for authentication

### Entry Points
- `POST /upload/initiate` - Create upload session
- `PUT /upload/chunk/{upload_id}/{chunk_number}` - Upload chunk data
- `POST /upload/complete/{upload_id}` - Finalize upload
- `DELETE /upload/{upload_id}` - Cancel upload
- `GET /upload/status/{upload_id}` - Get upload progress
- `GET /upload/chunks/{upload_id}` - Get received chunks list

### Trust Boundaries
- **Frontend <-> API**: JWT authentication required
- **API <-> Database**: Internal trusted connection
- **API <-> Storage**: Internal trusted file operations

### Attacker Goals
1. Access or delete other users' uploads (privacy breach)
2. Exhaust server storage (DoS)
3. Upload malicious content bypassing validation
4. Enumerate upload IDs to discover active sessions

## Findings

### CRITICAL: Insecure Direct Object Reference (IDOR)

**Severity**: CRITICAL
**Location**: `backend/api/routers/upload.py` (all endpoints except initiate), `backend/api/services/upload_service.py`

**Description**: Upload session operations (chunk upload, complete, cancel, status, get_chunks) authenticate the user but do not verify that the authenticated user owns the upload session. The `upload_id` is a UUID which provides some obscurity but is not a security control.

**Attack Scenario**:
1. Attacker authenticates legitimately
2. Attacker intercepts or guesses a victim's `upload_id`
3. Attacker can: cancel victim's upload, complete victim's upload, view victim's upload status, or upload malicious chunks to victim's session

**Evidence**:
```python
# upload.py line 86-136
async def upload_chunk(...):
    # current_user is obtained but user_id is never passed to service
    async with get_db_session() as session:
        result = await upload_service.upload_chunk(
            session=session,
            upload_id=upload_id,  # No user_id verification
            chunk_number=chunk_number,
            chunk_data=chunk_data,
            content_md5=content_md5,
        )
```

```python
# upload_service.py line 329-367
async def _get_session(...) -> UploadSession:
    # Only checks if session exists and is active
    # Does NOT verify upload_session.user_id matches current user
    if upload_session is None:
        raise SessionNotFoundError(...)
    # Missing: if upload_session.user_id != user_id: raise ...
```

**Required Fix**:
1. Pass `user_id` from `current_user` to all service methods
2. In `_get_session()` or each method, verify `upload_session.user_id == user_id`
3. Return 404 (not 403) to avoid revealing session existence

---

### HIGH: Missing Rate Limiting

**Severity**: HIGH
**Location**: `backend/api/routers/upload.py`

**Description**: API specification defines rate limits (5 initiate/hour, 1000 chunks/hour) but implementation has no rate limiting.

**Attack Scenario**: Attacker can spam upload initiation to exhaust storage allocation, create millions of sessions, or DoS the storage layer.

**Required Fix**: Implement rate limiting using Redis-backed middleware (e.g., `slowapi`, `fastapi-limiter`).

---

### MEDIUM: No File Content Validation

**Severity**: MEDIUM
**Location**: `backend/api/services/upload_service.py` lines 219-227

**Description**: After chunks are assembled, there's no validation that the assembled file is actually a valid video file matching the declared content type. Only client-provided metadata is trusted.

**Attack Scenario**: Attacker declares file as `video/mp4` but uploads arbitrary content (e.g., executable disguised as video).

**Mitigation**:
1. Validate assembled file magic bytes match declared content type
2. Consider running ffprobe/mediainfo to verify video integrity
3. Scan for embedded threats if resources permit

---

### MEDIUM: Predictable Storage Paths

**Severity**: MEDIUM
**Location**: `backend/api/services/upload_service.py` lines 387-393, 410-427

**Description**: Storage paths use predictable patterns: `chunks/{upload_id}/chunk_NNNNN` and `videos/{user_id}/{video_id}.ext`. While these are behind API authentication, if storage is misconfigured (e.g., public S3 bucket), paths could be enumerated.

**Mitigation**:
1. Ensure storage is never publicly accessible
2. Consider adding random prefix to storage keys
3. Document storage security requirements

---

### LOW: MD5 Not Validated

**Severity**: LOW
**Location**: `backend/api/services/upload_service.py` lines 161-162

**Description**: Client can provide `Content-MD5` header but it's calculated if missing and never validated against provided value.

**Impact**: Integrity check is not enforced; corrupted uploads may not be detected.

**Fix**: Compare provided MD5 with calculated hash and reject mismatches.

---

### LOW: Session Expiration Timing Leak

**Severity**: LOW
**Location**: `backend/api/services/upload_service.py` line 359

**Description**: Different error messages for "not found" vs "expired" sessions could allow attackers to determine if an upload_id was ever valid.

**Mitigation**: Return same error message for not found and expired.

## Required Changes

| Priority | Issue | Fix |
|----------|-------|-----|
| CRITICAL | IDOR on upload operations | Add user_id verification in all upload service methods |
| HIGH | No rate limiting | Implement rate limiting per API spec |
| MEDIUM | No content validation | Validate assembled file magic bytes |
| LOW | MD5 not validated | Verify Content-MD5 if provided |

## Positive Security Controls Observed

1. **Authentication enforced**: All endpoints use `Depends(get_current_user)`
2. **Input validation**: Pydantic schemas validate file size, duration, content type
3. **UUID session IDs**: Provides obscurity (but not a substitute for authorization)
4. **Session expiration**: 1-hour expiry limits attack window
5. **Proper error handling**: Custom exceptions with appropriate HTTP status codes

## Evidence

| File | Lines | Finding |
|------|-------|---------|
| `backend/api/routers/upload.py` | 86-285 | No user_id passed to service methods |
| `backend/api/services/upload_service.py` | 329-367 | _get_session lacks ownership check |
| `backend/api/services/upload_service.py` | 219-227 | No content validation on assembled file |
| `docs/engineering/API.md` | 1096-1097 | Rate limits specified but not implemented |

## Inputs

- `backend/api/routers/upload.py`
- `backend/api/services/upload_service.py`
- `backend/api/schemas/upload.py`
- `backend/api/models/upload.py`
- `backend/tests/test_upload.py`
- `frontend/src/lib/upload/api.ts`
- `docs/engineering/API.md`
- `docs/engineering/DATA_MODEL.md`
- `specs/bdd/upload.feature`
