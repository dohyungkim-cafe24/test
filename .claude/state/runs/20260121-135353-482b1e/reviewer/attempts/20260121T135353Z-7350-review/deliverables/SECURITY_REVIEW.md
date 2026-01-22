# Security Review: F001 User Authentication (Security Fixes)

## Verdict
PASS

## Summary

The security fixes address all previously identified vulnerabilities. The OAuth implementation now follows security best practices: CSRF tokens are validated server-side with single-use semantics, refresh tokens are stored hashed in the database, access tokens are delivered via URL fragments (not logged server-side), and production deployment requires explicit secret key configuration.

## Threat Model (Lightweight)

### Assets
1. **User credentials**: OAuth tokens from Kakao/Google providers
2. **Session tokens**: JWT access tokens (short-lived), refresh tokens (long-lived)
3. **User data**: Profile information, email, provider IDs
4. **Application secrets**: JWT signing key, OAuth client secrets

### Entry Points
1. `/api/v1/auth/kakao` - OAuth initiation
2. `/api/v1/auth/kakao/callback` - OAuth callback (receives code + state)
3. `/api/v1/auth/google` - OAuth initiation
4. `/api/v1/auth/google/callback` - OAuth callback
5. `/api/v1/auth/refresh` - Token refresh (receives cookie)
6. `/api/v1/auth/logout` - Session termination
7. `/api/v1/auth/me` - Protected resource (requires Bearer token)

### Trust Boundaries
1. **Browser <-> Backend**: HTTPS required in production, CORS configured
2. **Backend <-> OAuth Providers**: TLS via httpx client
3. **Backend <-> Database**: Connection pooling, parameterized queries via SQLAlchemy
4. **Backend <-> Redis**: State token storage

### Attacker Goals
1. Hijack user sessions (session fixation, token theft)
2. Bypass authentication (forged tokens, CSRF attacks)
3. Access other users' data (IDOR)
4. Redirect users to malicious sites (open redirect)
5. Enumerate valid users/accounts

## Findings

### Critical
None.

### High
None.

### Medium
None.

### Low

#### L1: Memory store fallback may reduce CSRF protection in edge cases
- **File**: `state_store.py`, lines 71-75
- **Risk**: If Redis fails after state creation but before validation, the in-memory store on a different server instance would not have the token.
- **Mitigation in place**: Single-server dev scenario; Redis is intended for production.
- **Recommendation**: Add health check for Redis; consider sticky sessions or fail-fast on Redis unavailability in production.

#### L2: No rate limiting on authentication endpoints
- **Files**: `auth.py` endpoints
- **Risk**: Brute force attempts on refresh token endpoint, OAuth abuse.
- **Mitigation**: OAuth providers have their own rate limits; refresh tokens are 256-bit random.
- **Recommendation**: Add rate limiting middleware (e.g., slowapi) for production.

#### L3: IP address stored in refresh token record
- **File**: `token_service.py`, line 41
- **Risk**: Potential PII; needs proper data retention/deletion.
- **Mitigation**: IP is used for session tracking, not logged externally.
- **Recommendation**: Document retention policy; ensure GDPR/privacy compliance.

## Security Checklist

| Control | Status | Notes |
|---------|--------|-------|
| CSRF Protection | PASS | Server-side state validation, single-use tokens |
| Token Storage | PASS | Refresh tokens hashed (SHA-256) in DB |
| Token Transmission | PASS | Access token in URL fragment, refresh in HttpOnly cookie |
| Secret Management | PASS | Production fails fast on default secret |
| Input Validation | PASS | Redirect URI allowlist, state parsing |
| Session Expiration | PASS | Access token 15min, refresh token 7 days, DB revocation |
| Logout | PASS | Server-side revocation + cookie deletion |
| XSS Protection | PASS | HttpOnly cookies, no sensitive data in DOM |
| CORS | PASS | Configured per environment |
| SQL Injection | PASS | SQLAlchemy ORM with parameterized queries |

## Required Changes
None. Security posture is acceptable for the current stage.

## Recommendations (Non-Blocking)

1. **Rate Limiting**: Add rate limiting on `/auth/refresh` and OAuth endpoints before production launch.

2. **Token Rotation**: Implement refresh token rotation (issue new refresh token on each use, revoke previous) to limit window of token compromise.

3. **Security Logging**: Add structured audit logging for security events:
   - Successful/failed logins
   - Token refresh attempts
   - Logout events
   - Invalid state token attempts

4. **Redis Availability**: In production, consider failing fast if Redis is unavailable rather than falling back to memory store.

5. **HSTS**: Ensure HSTS headers are set at the infrastructure level for production.

## Evidence

### CSRF Validation (B1 Fix)
```python
# state_store.py:83-126
async def validate_state(state: str) -> tuple[bool, Optional[str]]:
    # ... parses state, looks up in Redis/memory, deletes on use (single-use)
    if redis_client:
        stored_redirect = await redis_client.getdel(key)  # Atomic get+delete
```

```python
# auth.py:169-175
is_valid, redirect_path = await oauth_service.validate_state(state)
if not is_valid:
    error_params = urlencode({"error": "invalid_state", ...})
    return RedirectResponse(...)
```

### Refresh Token Storage (B2/M2 Fix)
```python
# token_service.py:15-45
async def create_refresh_token(session, user_id, token_hash, expires_at, ...):
    token = RefreshToken(user_id=user_id, token_hash=token_hash, ...)
    session.add(token)

# oauth_service.py:284-293
def hash_refresh_token(self, token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
```

### Fragment Token Delivery (M1 Fix)
```python
# auth.py:221
redirect_url = f"{settings.frontend_url}{redirect_path or '/dashboard'}#access_token={jwt_access_token}"
```

```typescript
// context.tsx:166-172
const hash = window.location.hash;
if (hash) {
    const hashParams = new URLSearchParams(hash.substring(1));
    urlToken = hashParams.get('access_token');
```

### Production Secret Check (m4 Fix)
```python
# config.py:52-57
def __init__(self, **kwargs):
    super().__init__(**kwargs)
    if self.is_production and self.secret_key == "dev-only-change-me-in-production":
        raise ValueError("SECRET_KEY must be set in production environment")
```

### Open Redirect Prevention (m1 Fix)
```python
# auth.py:32, 40-70
ALLOWED_REDIRECT_PATHS = {"/dashboard", "/upload", "/history", "/settings", "/profile"}

def validate_redirect_path(redirect_uri: Optional[str]) -> Optional[str]:
    if parsed.scheme or parsed.netloc:  # Reject absolute URLs
        return None
    if path in ALLOWED_REDIRECT_PATHS:
        return path
    return None  # Reject unknown paths
```

## Inputs
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/routers/auth.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/services/oauth_service.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/services/state_store.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/services/user_service.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/services/token_service.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/services/database.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/config.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/main.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/models/user.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/frontend/src/lib/auth/context.tsx`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/tests/test_auth.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/tests/conftest.py`
