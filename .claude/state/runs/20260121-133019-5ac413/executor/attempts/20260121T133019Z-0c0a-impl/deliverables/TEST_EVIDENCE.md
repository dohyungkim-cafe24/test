# Test Evidence: F001 User Authentication

## Inputs

- `specs/bdd/auth.feature` - Gherkin scenarios
- `features.json` - Acceptance criteria AC-001 through AC-005
- `docs/engineering/API.md` - API specifications

## Commands

### Backend Unit Tests

```bash
PYTHONPATH=/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend \
  /Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/.venv/bin/pytest \
  /Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/tests/test_auth.py -v
```

**Output:**
```
============================= test session starts ==============================
platform darwin -- Python 3.13.5, pytest-9.0.2, pluggy-1.6.0
plugins: anyio-4.12.1, asyncio-1.3.0
asyncio: mode=Mode.AUTO

collected 14 items

tests/test_auth.py::TestKakaoOAuth::test_kakao_auth_redirects_to_provider PASSED [  7%]
tests/test_auth.py::TestKakaoOAuth::test_kakao_callback_with_valid_code_creates_session PASSED [ 14%]
tests/test_auth.py::TestKakaoOAuth::test_kakao_callback_with_invalid_code_returns_error PASSED [ 21%]
tests/test_auth.py::TestKakaoOAuth::test_kakao_callback_preserves_redirect_uri PASSED [ 28%]
tests/test_auth.py::TestGoogleOAuth::test_google_auth_redirects_to_provider PASSED [ 35%]
tests/test_auth.py::TestGoogleOAuth::test_google_callback_with_valid_code_creates_session PASSED [ 42%]
tests/test_auth.py::TestSessionManagement::test_refresh_token_returns_new_access_token PASSED [ 50%]
tests/test_auth.py::TestSessionManagement::test_refresh_with_expired_token_returns_401 PASSED [ 57%]
tests/test_auth.py::TestSessionManagement::test_logout_clears_session PASSED [ 64%]
tests/test_auth.py::TestAuthGuard::test_protected_route_without_token_returns_401 PASSED [ 71%]
tests/test_auth.py::TestAuthGuard::test_protected_route_with_valid_token_returns_user PASSED [ 78%]
tests/test_auth.py::TestAuthGuard::test_protected_route_with_expired_token_returns_401 PASSED [ 85%]
tests/test_auth.py::TestOAuthErrorHandling::test_kakao_callback_cancelled_by_user PASSED [ 92%]
tests/test_auth.py::TestOAuthErrorHandling::test_google_callback_missing_state_returns_error PASSED [100%]

============================== 14 passed in 0.10s ==============================
```

**Result:** 14/14 PASSED

## Test Coverage by Acceptance Criteria

| AC | Test | Result |
|----|------|--------|
| AC-001 | `test_kakao_auth_redirects_to_provider` | PASS |
| AC-001 | `test_kakao_callback_with_valid_code_creates_session` | PASS |
| AC-002 | `test_google_auth_redirects_to_provider` | PASS |
| AC-002 | `test_google_callback_with_valid_code_creates_session` | PASS |
| AC-003 | `test_refresh_token_returns_new_access_token` | PASS |
| AC-003 | `test_refresh_with_expired_token_returns_401` | PASS |
| AC-004 | `test_logout_clears_session` | PASS |
| AC-005 | `test_protected_route_without_token_returns_401` | PASS |
| AC-005 | `test_protected_route_with_valid_token_returns_user` | PASS |
| AC-005 | `test_protected_route_with_expired_token_returns_401` | PASS |

## Additional Tests

| Test | Description | Result |
|------|-------------|--------|
| `test_kakao_callback_with_invalid_code_returns_error` | OAuth error handling | PASS |
| `test_kakao_callback_preserves_redirect_uri` | State preservation | PASS |
| `test_kakao_callback_cancelled_by_user` | User cancel flow | PASS |
| `test_google_callback_missing_state_returns_error` | CSRF protection | PASS |

## Evidence Files

- `evidence/unit_tests.log` - Full pytest output

## Notes

- Tests mock external OAuth provider calls (Kakao/Google APIs) at service boundary
- Database operations are mocked (requires integration tests for full coverage)
- Frontend tests would require Jest setup with React Testing Library
- Runtime verification requires deployed environment with real OAuth credentials
