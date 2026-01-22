# Security Review: F010 - Report History Dashboard

**Feature:** F010 - Report History Dashboard
**Date:** 2026-01-22
**Reviewer:** reviewer subagent

## Verdict
PASS

## Threat model (lightweight)

### Assets
- User report data (analysis results, performance metrics)
- Report metadata (video IDs, timestamps, thumbnails)
- Soft-delete state (deleted_at timestamps)

### Entry points
1. `GET /api/v1/dashboard/reports` - List reports
2. `DELETE /api/v1/reports/{report_id}` - Soft delete report
3. `POST /api/v1/reports/{report_id}/restore` - Restore deleted report

### Trust boundaries
- **Frontend to Backend**: Bearer token authentication (JWT)
- **Backend to Database**: User ID filtering on all queries
- **Backend to CDN**: Thumbnail URL generation (currently placeholder)

### Attacker goals
1. Access another user's reports (IDOR)
2. Delete another user's reports
3. Enumerate report IDs
4. Bypass authentication

## Findings

### Authorization Controls: ADEQUATE

**Owner-only access enforcement:**
- `dashboard_service.py:188` - Delete validates `report.user_id != user_id`
- `dashboard_service.py:255` - Restore validates ownership
- `dashboard_service.py:90-94` - List filters by `user_id`

**IDOR Protection:**
- All queries filter by authenticated user's ID
- Report IDs are UUIDs (not enumerable)
- Ownership check occurs before any mutation

### Authentication: ADEQUATE

- All endpoints use `Depends(get_current_user)` dependency
- 401 returned for missing/invalid tokens (router lines 47, 77-78, 121-122)
- Frontend API client handles 401 and throws `DashboardError`

### Soft Delete with Restore: ADEQUATE

- Soft delete sets `deleted_at` timestamp (`dashboard_service.py:200-201`)
- Restore window enforced at 10 seconds (`RESTORE_WINDOW_SECONDS = 10`)
- Restore validates both ownership AND window expiry (`dashboard_service.py:271-284`)
- Hard delete expected via background job (not in this PR scope)

### Input Validation: ADEQUATE

- Report ID validated as UUID via FastAPI Path dependency
- Pagination params validated with `ge=1, le=50` constraints
- No user-controlled strings directly interpolated in queries (SQLAlchemy ORM)

### Logging: ADEQUATE (no PII leakage)

- Logs include `user_id`, `report_id` as UUIDs (line 138-147, 206-213)
- No email, name, or sensitive data in log messages
- Warning logs for denied access attempts (line 189-196)

### Minor Observations (not blocking)

1. **No rate limiting on delete/restore endpoints**
   - An authenticated attacker could rapidly delete/restore reports.
   - Recommend adding rate limiting in production.

2. **Thumbnail URL construction**
   - Currently returns placeholder `cdn.example.com`.
   - When implementing real CDN, ensure signed URLs or access control to prevent thumbnail enumeration.

## Required changes
None.

## Evidence

| Security Control | Location | Status |
|------------------|----------|--------|
| AuthN required | `dashboard.py:49, 85, 129` via `Depends(get_current_user)` | OK |
| Owner-only list | `dashboard_service.py:90` `user_id == user_id` filter | OK |
| Owner-only delete | `dashboard_service.py:188` ownership check | OK |
| Owner-only restore | `dashboard_service.py:255` ownership check | OK |
| UUID report IDs | Schema uses UUID type | OK |
| Restore window enforced | `dashboard_service.py:271-284` time check | OK |
| No SQL injection | SQLAlchemy ORM with bound parameters | OK |
| No PII in logs | Logs use UUIDs only | OK |

## Inputs
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/services/dashboard_service.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/routers/dashboard.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/api/routers/auth.py`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/frontend/src/lib/dashboard/api.ts`
- `/Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/backend/tests/test_dashboard.py`
