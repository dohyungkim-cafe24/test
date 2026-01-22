# Security Review: F001 User Authentication

## Verdict
NEEDS_CHANGES

## Threat Model (Lightweight)

### Assets
- User credentials/identity (OAuth tokens)
- JWT access tokens (15-minute validity)
- Refresh tokens (7-day validity)
- User profile data (email, name, avatar)
- Session state

### Entry Points
1. `GET /api/v1/auth/kakao` - OAuth initiation
2. `GET /api/v1/auth/kakao/callback` - OAuth callback (receives code/state)
3. `GET /api/v1/auth/google` - OAuth initiation
4. `GET /api/v1/auth/google/callback` - OAuth callback
5. `POST /api/v1/auth/refresh` - Token refresh (reads cookie)
6. `POST /api/v1/auth/logout` - Session termination
7. `GET /api/v1/auth/me` - Protected user profile endpoint
8. Frontend localStorage - Token storage

### Trust Boundaries
- **External OAuth Providers** (Kakao, Google) -> Backend API
- **Browser/Client** -> Backend API
- **Backend API** -> Database (not yet integrated)

### Attacker Goals
1. Steal user sessions/tokens
2. Impersonate users
3. Access protected resources without authentication
4. Perform CSRF attacks to hijack OAuth flows
5. Exfiltrate user PII

## Findings

### Critical

**S1. CSRF Vulnerability in OAuth Flow**
- **File**: `/projects/punch-analytics/backend/api/routers/auth.py`, lines 114-124
- **Issue**: State parameter is generated but never validated against server-side storage. Attacker can forge state parameter.
- **Attack**: Attacker initiates OAuth flow, captures state, then uses CSRF to force victim to complete login with attacker's code
- **Recommendation**: Store state in Redis with 10-minute TTL, validate on callback, delete after use

### High

**S2. Token Exposure via URL**
- **File**: `/projects/punch-analytics/backend/api/routers/auth.py`, lines 150, 245
- **Issue**: Access token passed in URL query string after OAuth callback
- **Attack**: Token appears in browser history, server access logs, referrer headers, shared screenshots
- **Recommendation**: Use POST-redirect pattern with token in response body, or use URL fragment (#access_token=)

**S3. Insecure Default Secret Key**
- **File**: `/projects/punch-analytics/backend/api/config.py`, line 22
- **Issue**: Default secret key `"change-me-in-production"` is hardcoded and weak
- **Attack**: If deployed with default, attacker can forge JWTs
- **Recommendation**: Remove default, require explicit configuration, validate key strength

**S4. Open Redirect Potential**
- **File**: `/projects/punch-analytics/backend/api/routers/auth.py`, lines 82, 180
- **Issue**: `redirect_uri` parameter not validated, stored in state, used in final redirect
- **Attack**: `?redirect_uri=https://evil.com` could redirect authenticated user to phishing site
- **Recommendation**: Validate against allowlist or require relative paths only

### Medium

**S5. Token in Client-Side Storage (XSS Risk)**
- **File**: `/projects/punch-analytics/frontend/src/lib/auth/context.tsx`, lines 71-84
- **Issue**: Access token stored in localStorage, accessible to any JS on the page
- **Attack**: XSS vulnerability anywhere in app could steal token
- **Recommendation**: Use memory-only storage; rely on HttpOnly refresh cookie for persistence

**S6. Missing Token Revocation**
- **File**: `/projects/punch-analytics/backend/api/services/oauth_service.py`, lines 268-283
- **Issue**: `validate_refresh_token()` not implemented; tokens cannot be revoked
- **Attack**: Stolen refresh token valid for 7 days with no way to revoke
- **Recommendation**: Implement token revocation list, check on each refresh

**S7. Logout Does Not Revoke Server-Side Token**
- **File**: `/projects/punch-analytics/backend/api/routers/auth.py`, lines 336-338
- **Issue**: Comment says "would also revoke token in database" but not implemented
- **Attack**: Logout only clears cookie; if token was stolen, it remains valid
- **Recommendation**: Implement server-side revocation on logout

### Low

**S8. Missing Rate Limiting**
- **Files**: All auth endpoints
- **Issue**: No rate limiting on auth endpoints
- **Attack**: Brute force on token refresh, OAuth callback flooding
- **Recommendation**: Add rate limiting middleware (e.g., slowapi)

**S9. Verbose Error Messages**
- **File**: `/projects/punch-analytics/backend/api/services/oauth_service.py`, lines 124, 147, etc.
- **Issue**: Error messages include raw provider response text
- **Attack**: Information disclosure; may reveal internal details
- **Recommendation**: Log detailed errors server-side, return generic messages to client

## Security Checklist

| Check | Status | Notes |
|-------|--------|-------|
| Input validation | PARTIAL | Query params used but redirect_uri not validated |
| AuthN | IMPLEMENTED | OAuth + JWT flow works |
| AuthZ | IMPLEMENTED | get_current_user dependency |
| CSRF protection | MISSING | State not validated server-side |
| XSS protection | PARTIAL | React escaping, but token in localStorage |
| Secrets management | NEEDS_WORK | Hardcoded default secret |
| Token security | PARTIAL | HttpOnly refresh cookie, but access token in URL |
| Session management | INCOMPLETE | Refresh validation not implemented |
| Rate limiting | MISSING | No rate limiting |
| Logging | NEEDS_WORK | No security event logging |
| Error handling | NEEDS_WORK | Too verbose externally |

## Required Changes

### Must Fix (Before Merge)
1. **Implement CSRF state validation** with server-side storage (S1)
2. **Remove access token from URL** - use fragment or response body (S2)
3. **Remove default secret key** or validate environment (S3)
4. **Validate redirect_uri** against allowlist (S4)

### Should Fix (Before Production)
5. Implement refresh token persistence and validation (S6)
6. Implement token revocation on logout (S7)
7. Add rate limiting to auth endpoints (S8)
8. Consider memory-only token storage on frontend (S5)

## Evidence

### Positive Security Observations
- Refresh token uses HttpOnly cookie (prevents JS access)
- Secure flag set for cookies in production
- SameSite=Lax prevents basic CSRF on cookies
- JWT includes type claim to prevent token confusion
- Password not used (OAuth-only reduces attack surface)
- CORS properly configured per environment
- HS256 algorithm is appropriate for single-server JWT

### OAuth Flow Analysis
The OAuth implementation follows the standard authorization code flow:
1. Generate state with CSRF token
2. Redirect to provider
3. Receive callback with code
4. Exchange code for tokens
5. Create local session

However, step 1 and 3 lack server-side state binding, breaking CSRF protection.

## Inputs
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/routers/auth.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/services/oauth_service.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/config.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/schemas/auth.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/models/user.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/main.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/frontend/src/lib/auth/context.tsx`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/frontend/src/lib/auth/api.ts`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/frontend/src/middleware.ts`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/frontend/src/components/auth/AuthGuard.tsx`
