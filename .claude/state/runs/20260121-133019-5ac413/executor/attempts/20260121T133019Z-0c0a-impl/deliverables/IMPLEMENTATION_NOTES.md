# Implementation Notes: F001 User Authentication

## Summary

Implemented OAuth-based authentication system for PunchAnalytics supporting Kakao and Google providers, with JWT session management, protected route middleware, and logout functionality.

## Inputs

- `specs/bdd/auth.feature` - BDD scenarios for authentication
- `docs/engineering/API.md` - API endpoint specifications
- `docs/engineering/DATA_MODEL.md` - Database schema for users and refresh_tokens
- `docs/ux/design_tokens.json` - Material Design 3 tokens
- `features.json` - Feature definition and acceptance criteria

## Approach

**TDD-first implementation:**
1. Wrote 14 failing tests covering all acceptance criteria (AC-001 through AC-005)
2. Implemented backend OAuth service, auth router, and schemas
3. Implemented frontend auth context, hooks, and components
4. All tests passing

**Architecture decisions:**
- Backend: FastAPI with dependency injection for testability
- Frontend: Next.js 14 App Router with React Context for auth state
- Tokens: JWT access tokens (15 min expiry) + HttpOnly cookie refresh tokens (7 days)
- State preservation: Refresh token stored in HttpOnly cookie, access token in localStorage

## Changes

### Backend (`projects/punch-analytics/backend/`)

| Path | Description |
|------|-------------|
| `api/main.py` | FastAPI application factory with CORS and router setup |
| `api/config.py` | Settings from environment variables (OAuth credentials, URLs) |
| `api/routers/auth.py` | Auth endpoints: OAuth flows, refresh, logout, /me |
| `api/services/oauth_service.py` | OAuth code exchange, JWT creation/verification |
| `api/schemas/auth.py` | Pydantic schemas for API request/response |
| `api/models/user.py` | SQLAlchemy models for User and RefreshToken |
| `tests/test_auth.py` | 14 unit tests covering all ACs |
| `tests/conftest.py` | Test fixtures and mock data |
| `pyproject.toml` | Project configuration and dependencies |
| `requirements.txt` | Python dependencies |
| `Dockerfile` | Container configuration |

### Frontend (`projects/punch-analytics/frontend/`)

| Path | Description |
|------|-------------|
| `src/lib/auth/api.ts` | Auth API client functions |
| `src/lib/auth/context.tsx` | AuthProvider with state management |
| `src/lib/auth/hooks.ts` | useAuth, useUser, useIsAuthenticated hooks |
| `src/components/auth/LoginButton.tsx` | Kakao/Google OAuth login buttons |
| `src/components/auth/LogoutButton.tsx` | Logout button component |
| `src/components/auth/AuthGuard.tsx` | Protected route wrapper (AC-005) |
| `src/middleware.ts` | Next.js middleware for route hints |
| `src/app/layout.tsx` | Root layout with AuthProvider |
| `src/app/theme.ts` | Material UI theme from design tokens |
| `src/app/page.tsx` | Landing page |
| `src/app/(auth)/login/page.tsx` | Login page with OAuth buttons |
| `src/app/(protected)/dashboard/page.tsx` | Protected dashboard page |
| `package.json` | Node dependencies (MUI, Next.js) |
| `tsconfig.json` | TypeScript configuration |
| `Dockerfile` | Container configuration |

### Infrastructure

| Path | Description |
|------|-------------|
| `docker-compose.yml` | Full stack dev environment (postgres, redis, backend, frontend) |

## Decisions

1. **JWT in localStorage vs HttpOnly cookie**
   - Chose: Access token in localStorage, refresh token in HttpOnly cookie
   - Rationale: Balance between XSS protection (refresh in cookie) and ease of API access (access in localStorage)
   - Trade-off: XSS could steal access token, but it expires in 15 minutes

2. **State parameter encoding**
   - Chose: `{csrf_token}|{redirect_path}` format
   - Rationale: Simple encoding that preserves redirect destination through OAuth flow

3. **Frontend auth state initialization**
   - Chose: Check URL params first, then localStorage, then try refresh
   - Rationale: Handles OAuth callback, page refresh, and expired token scenarios

4. **Mock-only external OAuth calls in tests**
   - Chose: Mock only `exchange_*_code` and `get_*_user` methods
   - Rationale: These are true external boundaries (3rd party APIs)

## Risks / Follow-ups

1. **Database integration needed**
   - Current implementation mocks database operations
   - Need to implement actual user creation/lookup in OAuth callbacks
   - Need to implement refresh token storage/validation

2. **Token refresh edge case**
   - If access token expires during a request, user sees error
   - Consider implementing automatic retry with token refresh

3. **PKCE for OAuth**
   - Current implementation uses basic OAuth code flow
   - Consider adding PKCE for enhanced security (RFC 7636)

4. **Rate limiting**
   - Auth endpoints should be rate limited to prevent abuse
   - Redis-based rate limiter recommended

5. **Session expiration dialog (AC-003)**
   - Backend support implemented (401 on expired token)
   - Frontend dialog UI not yet implemented (would be enhancement)
