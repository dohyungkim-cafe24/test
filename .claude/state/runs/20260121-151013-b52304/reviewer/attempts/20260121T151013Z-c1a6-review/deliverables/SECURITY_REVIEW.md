# SECURITY_REVIEW.md

## Verdict
PASS

## Threat model (lightweight)

### Assets
1. **User videos** - personal sparring footage, privacy-sensitive
2. **Subject selections** - bounding box data for tracking user in video
3. **Thumbnail images** - extracted frames with detected persons

### Entry points
1. `GET /analysis/thumbnails/{video_id}` - retrieves thumbnails for a video
2. `POST /analysis/subject/{video_id}` - creates/updates subject selection

### Trust boundaries
1. Client (untrusted) <-> API (JWT required)
2. API <-> Database (trusted, internal)
3. API <-> Storage (trusted, internal)

### Attacker goals
1. **IDOR**: Access another user's video thumbnails or subject data
2. **Data exfiltration**: Enumerate video IDs to find valid targets
3. **Injection**: Manipulate person_id or thumbnail_id to cause unexpected behavior
4. **Denial of service**: Exhaust resources via malformed requests

## Findings

### IDOR Protection (PASS)

**Video ownership verification implemented correctly:**
- `subject_service.py:271-302`: `_get_video()` checks `video.user_id != user_id`
- Returns same error message for not-found and unauthorized (lines 296, 300)
- Prevents enumeration attacks

**Thumbnail scoped to video:**
- `subject_service.py:344-346`: Thumbnail lookup includes `Thumbnail.video_id == video_id`
- Cannot access thumbnails from other videos

### Authentication (PASS)

**Both endpoints require authentication:**
- `routers/subject.py:45,86`: `Depends(get_current_user)` on both endpoints
- Test `test_get_thumbnails_requires_auth` verifies 401 response without auth

### Input Validation (PASS)

**UUID path parameters:**
- FastAPI automatically validates UUID format in path
- Invalid UUIDs return 422 Unprocessable Entity

**thumbnail_id validation:**
- `routers/subject.py:100-105`: Explicit UUID parsing with 422 error on failure

**person_id validation:**
- `subject_service.py:219-230`: Validated against `detected_persons` array
- Invalid person_id returns PersonNotFoundError (404)

### Injection Resistance (PASS)

**SQLAlchemy ORM prevents SQL injection:**
- All queries use parameterized statements via SQLAlchemy
- No raw SQL construction

**No command injection vectors:**
- No shell commands or system calls
- Storage keys are generated, not user-controlled in dangerous ways

### Information Leakage (LOW RISK)

**m3 from code review:**
- `PersonNotFoundError` message includes thumbnail UUID
- Risk: Low - attacker already knows the video_id and thumbnail_id they submitted
- Recommendation: Use generic message for defense-in-depth

### Logging/PII (PASS)

- No PII logged in reviewed code
- Error messages don't expose sensitive data

### Rate Limiting (OUT OF SCOPE)

- Rate limiting should be handled at infrastructure level (API gateway)
- Not a blocker for this feature

## Required changes
None. Security posture is acceptable.

## Evidence

### IDOR Test Case (Critical Path)

File: `subject_service.py`, Lines 290-300
```python
# Verify ownership - same error to prevent enumeration
if video.user_id != user_id:
    raise VideoNotFoundError(f"Video not found: {video_id}")
```

The error message is identical for both cases, preventing attackers from distinguishing between "video doesn't exist" and "video exists but belongs to another user".

### Authentication Enforcement

File: `routers/subject.py`, Lines 43-46
```python
async def get_thumbnails(
    video_id: Annotated[UUID, Path(description="Video ID")],
    current_user: Annotated[dict, Depends(get_current_user)],
):
```

The `get_current_user` dependency is imported from `api.routers.auth` and raises 401 if no valid Bearer token is present.

### Test Evidence

File: `test_subject.py`, Lines 442-453
```python
def test_get_thumbnails_requires_auth(self, mock_user):
    """Thumbnails endpoint requires authentication."""
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    client = TestClient(app)

    video_id = uuid4()
    response = client.get(f"/api/v1/analysis/thumbnails/{video_id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

## Inputs

- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/routers/subject.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/services/subject_service.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/schemas/subject.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/tests/test_subject.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/routers/auth.py` (auth pattern reference)
