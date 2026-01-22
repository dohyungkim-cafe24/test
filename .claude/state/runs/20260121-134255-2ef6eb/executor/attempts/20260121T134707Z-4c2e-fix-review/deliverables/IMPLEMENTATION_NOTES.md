# Implementation Notes: F001 Security Fixes

## Overview

This attempt addresses all security findings from the code review (REQUEST_CHANGES verdict).

## Fixes Applied

### B1: CSRF State Token Validation (BLOCKER)
- **File**: `backend/api/services/state_store.py` (NEW)
- **Change**: Created server-side state storage using Redis (with in-memory fallback)
- **Mechanism**:
  - `store_state()`: Generates and stores CSRF token with TTL
  - `validate_state()`: Validates and consumes token (single-use)
- **File**: `backend/api/services/oauth_service.py`
- **Change**: `generate_state()` and `validate_state()` now use server-side storage

### B2/M2: Refresh Token Database Storage (BLOCKER/MAJOR)
- **File**: `backend/api/services/token_service.py` (NEW)
- **Change**: Implemented full refresh token lifecycle:
  - `create_refresh_token()`: Stores token hash in database
  - `validate_refresh_token()`: Validates against DB with expiry check
  - `revoke_refresh_token()`: Marks token as revoked
- **File**: `backend/api/routers/auth.py`
- **Change**: OAuth callbacks now persist refresh tokens to database

### M1: Access Token URL Exposure (MAJOR)
- **File**: `backend/api/routers/auth.py`
- **Change**: Changed from `?access_token=` to `#access_token=`
- **Rationale**: URL fragments are not sent to servers, not logged, not in browser history
- **File**: `frontend/src/lib/auth/context.tsx`
- **Change**: Updated token extraction to read from `window.location.hash`

### M3: User Persistence (MAJOR)
- **File**: `backend/api/services/user_service.py` (NEW)
- **Change**: `upsert_user()` creates or updates user on OAuth callback
- **File**: `backend/api/routers/auth.py`
- **Change**: Both Kakao and Google callbacks now persist user to database

### m1: Open Redirect Prevention (MINOR)
- **File**: `backend/api/routers/auth.py`
- **Change**: Added `validate_redirect_path()` with allowlist
- **Allowed paths**: `/dashboard`, `/upload`, `/history`, `/settings`, `/profile`

### m4: Hardcoded Secret Key (MINOR)
- **File**: `backend/api/config.py`
- **Change**: Added fail-fast check that raises error in production if default key is used

## New Files Created

1. `backend/api/services/database.py` - Async DB session management
2. `backend/api/services/state_store.py` - CSRF state storage (Redis + memory fallback)
3. `backend/api/services/user_service.py` - User CRUD operations
4. `backend/api/services/token_service.py` - Refresh token management

## Modified Files

1. `backend/api/services/oauth_service.py` - Async state methods, removed NotImplementedError
2. `backend/api/routers/auth.py` - Complete rewrite with security fixes
3. `backend/api/config.py` - Production safety check for secret key
4. `backend/api/main.py` - Lifespan with DB/Redis init
5. `backend/requirements.txt` - Added aiosqlite for testing
6. `frontend/src/lib/auth/context.tsx` - Read token from URL fragment
7. `backend/tests/conftest.py` - Mock services for testing
8. `backend/tests/test_auth.py` - New security fix tests

## Inputs
- CODE_REVIEW.md from reviewer attempt
- `backend/api/routers/auth.py`
- `backend/api/services/oauth_service.py`
- `backend/api/models/user.py`
- `backend/api/config.py`
- `frontend/src/lib/auth/context.tsx`
