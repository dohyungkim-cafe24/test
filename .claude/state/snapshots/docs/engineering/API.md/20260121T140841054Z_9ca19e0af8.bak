# PunchAnalytics - API Specification

## Inputs

- `docs/product/REQUIREMENTS_BASELINE.md`
- `docs/product/STORY_MAP.md`
- `features.json`
- `specs/bdd/TRACEABILITY.json`
- `specs/bdd/BDD_INDEX.json`
- `docs/ux/UX_CONTRACT.md`

---

## Problem Summary

PunchAnalytics requires a REST API that supports:
1. OAuth-based authentication with Kakao and Google providers (@F001)
2. Resumable video upload with progress tracking (@F002)
3. Subject selection and body specification capture (@F003, @F004)
4. Real-time processing status updates (@F005, @F006, @F007)
5. Report retrieval and sharing controls (@F008, @F009, @F010)

The API must handle:
- Files up to 500MB with resumable upload capability
- Processing latency of up to 5 minutes per video
- 100+ concurrent users without degradation
- p95 response time under 500ms for non-processing endpoints

---

## Base URL

```
Production: https://api.punchanalytics.com/api/v1
Staging:    https://api.staging.punchanalytics.com/api/v1
```

---

## Authentication

### Overview @F001

PunchAnalytics uses OAuth 2.0 with JWT for session management.

**Flow:**
1. Frontend initiates OAuth with provider (Kakao/Google)
2. Provider redirects to callback URL with authorization code
3. Backend exchanges code for provider tokens
4. Backend creates or updates user record
5. Backend issues JWT access token and refresh token
6. Frontend stores tokens and includes in subsequent requests

### Headers

```
Authorization: Bearer <access_token>
```

### Token Lifecycle

| Token | Expiry | Storage | Refresh |
|-------|--------|---------|---------|
| Access Token | 15 minutes | Memory/localStorage | Via refresh endpoint |
| Refresh Token | 7 days | HttpOnly cookie | Re-authenticate |

### OAuth Endpoints

#### GET /auth/kakao @F001

Initiates Kakao OAuth flow.

**Response:** 302 Redirect to Kakao authorization URL

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `redirect_uri` | string | No | Post-auth redirect (default: app dashboard) |

---

#### GET /auth/kakao/callback @F001

Handles Kakao OAuth callback.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `code` | string | Yes | Authorization code from Kakao |
| `state` | string | Yes | CSRF token |

**Success Response (302):**
Redirect to frontend with tokens set in HttpOnly cookies.

**Error Response (400):**
```json
{
  "error": "oauth_error",
  "error_description": "Authorization code invalid or expired"
}
```

---

#### GET /auth/google @F001

Initiates Google OAuth flow.

**Response:** 302 Redirect to Google authorization URL

---

#### GET /auth/google/callback @F001

Handles Google OAuth callback. Same structure as Kakao callback.

---

#### POST /auth/refresh @F001

Refreshes access token using refresh token cookie.

**Request:** No body (refresh token read from cookie)

**Success Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 900
}
```

**Error Response (401):**
```json
{
  "error": "invalid_refresh_token",
  "error_description": "Refresh token expired or revoked"
}
```

---

#### POST /auth/logout @F001

Terminates session and clears tokens.

**Request:** No body

**Success Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

---

#### GET /auth/me @F001

Returns current user profile.

**Success Response (200):**
```json
{
  "id": "usr_a1b2c3d4",
  "email": "user@example.com",
  "name": "Kim Boxer",
  "provider": "kakao",
  "avatar_url": "https://...",
  "created_at": "2026-01-15T09:00:00Z",
  "body_specs": {
    "height_cm": 175,
    "weight_kg": 70,
    "experience_level": "intermediate",
    "stance": "orthodox"
  }
}
```

---

## Endpoints

### Video Upload @F002

#### POST /upload/initiate @F002

Initiates a chunked upload session.

**Request:**
```json
{
  "filename": "sparring_2026_01_20.mp4",
  "file_size": 157286400,
  "content_type": "video/mp4",
  "duration_seconds": 120
}
```

**Success Response (201):**
```json
{
  "upload_id": "upl_x1y2z3",
  "chunk_size": 5242880,
  "total_chunks": 30,
  "expires_at": "2026-01-21T15:00:00Z"
}
```

**Validation:**
- `file_size`: max 524,288,000 bytes (500MB)
- `duration_seconds`: 60-180 (1-3 minutes)
- `content_type`: video/mp4, video/quicktime, video/webm

---

#### PUT /upload/chunk/{upload_id}/{chunk_number} @F002

Uploads a single chunk.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `upload_id` | string | Upload session ID |
| `chunk_number` | integer | 0-indexed chunk number |

**Headers:**
```
Content-Type: application/octet-stream
Content-Length: <chunk_size>
Content-MD5: <base64_md5>
```

**Request Body:** Raw binary chunk data

**Success Response (200):**
```json
{
  "chunk_number": 5,
  "received_bytes": 5242880,
  "total_received": 31457280,
  "progress_percent": 20
}
```

**Error Response (409 - Chunk already uploaded):**
```json
{
  "error": "chunk_exists",
  "error_description": "Chunk 5 already uploaded",
  "chunk_number": 5
}
```

---

#### POST /upload/complete/{upload_id} @F002

Finalizes upload and triggers thumbnail extraction.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `upload_id` | string | Upload session ID |

**Success Response (200):**
```json
{
  "video_id": "vid_abc123",
  "status": "processing_thumbnails",
  "duration_seconds": 120,
  "file_size": 157286400
}
```

---

#### DELETE /upload/{upload_id} @F002

Cancels an in-progress upload.

**Success Response (200):**
```json
{
  "message": "Upload cancelled",
  "upload_id": "upl_x1y2z3"
}
```

---

### Analysis Configuration @F003, @F004

#### GET /analysis/thumbnails/{video_id} @F003

Returns extracted thumbnails for subject selection.

**Success Response (200):**
```json
{
  "video_id": "vid_abc123",
  "status": "ready",
  "thumbnails": [
    {
      "frame_number": 30,
      "timestamp_seconds": 1.0,
      "url": "https://cdn.punchanalytics.com/thumbnails/vid_abc123/frame_030.jpg",
      "detected_persons": [
        {
          "person_id": "p1",
          "bounding_box": {
            "x": 120,
            "y": 80,
            "width": 200,
            "height": 400
          },
          "confidence": 0.95
        },
        {
          "person_id": "p2",
          "bounding_box": {
            "x": 450,
            "y": 90,
            "width": 180,
            "height": 380
          },
          "confidence": 0.92
        }
      ]
    }
  ],
  "total_frames": 10
}
```

**Error Response (202 - Still processing):**
```json
{
  "video_id": "vid_abc123",
  "status": "extracting",
  "progress_percent": 40,
  "estimated_seconds": 15
}
```

---

#### POST /analysis/subject/{video_id} @F003

Selects the analysis subject.

**Request:**
```json
{
  "person_id": "p1",
  "frame_number": 30
}
```

**Success Response (200):**
```json
{
  "video_id": "vid_abc123",
  "subject_id": "subj_def456",
  "person_id": "p1",
  "confirmed": true
}
```

---

#### POST /analysis/body-specs/{video_id} @F004

Submits body specifications.

**Request:**
```json
{
  "height_cm": 175,
  "weight_kg": 70,
  "experience_level": "intermediate",
  "stance": "orthodox"
}
```

**Validation:**
- `height_cm`: 100-250 (integer)
- `weight_kg`: 30-200 (integer)
- `experience_level`: "beginner" | "intermediate" | "advanced" | "competitive"
- `stance`: "orthodox" | "southpaw"

**Success Response (200):**
```json
{
  "video_id": "vid_abc123",
  "body_specs_id": "bs_ghi789",
  "saved": true,
  "persist_to_profile": true
}
```

---

#### POST /analysis/start/{video_id} @F005

Starts the analysis pipeline.

**Request:**
```json
{
  "subject_id": "subj_def456",
  "body_specs_id": "bs_ghi789"
}
```

**Success Response (202):**
```json
{
  "analysis_id": "anl_jkl012",
  "video_id": "vid_abc123",
  "status": "queued",
  "estimated_minutes": 3,
  "websocket_url": "wss://api.punchanalytics.com/ws/status/anl_jkl012"
}
```

---

### Processing Status @F005, @F006, @F007

#### GET /processing/status/{analysis_id} @F005

Returns current processing status.

**Success Response (200 - In progress):**
```json
{
  "analysis_id": "anl_jkl012",
  "status": "processing",
  "current_stage": "pose_estimation",
  "stages": [
    {
      "name": "thumbnail_extraction",
      "status": "completed",
      "started_at": "2026-01-21T13:00:00Z",
      "completed_at": "2026-01-21T13:00:15Z"
    },
    {
      "name": "pose_estimation",
      "status": "processing",
      "started_at": "2026-01-21T13:00:15Z",
      "progress_percent": 65,
      "frames_processed": 1950,
      "total_frames": 3000
    },
    {
      "name": "stamp_generation",
      "status": "pending"
    },
    {
      "name": "llm_analysis",
      "status": "pending"
    },
    {
      "name": "report_generation",
      "status": "pending"
    }
  ],
  "estimated_completion": "2026-01-21T13:03:30Z"
}
```

**Success Response (200 - Completed):**
```json
{
  "analysis_id": "anl_jkl012",
  "status": "completed",
  "report_id": "rpt_mno345",
  "completed_at": "2026-01-21T13:03:28Z",
  "total_duration_seconds": 208
}
```

**Success Response (200 - Failed):**
```json
{
  "analysis_id": "anl_jkl012",
  "status": "failed",
  "failed_stage": "pose_estimation",
  "error": {
    "code": "POSE_QUALITY_LOW",
    "message": "Unable to track subject clearly in video",
    "user_action": "Please upload video with better lighting or camera angle"
  },
  "failed_at": "2026-01-21T13:02:00Z"
}
```

---

#### WebSocket /ws/status/{analysis_id} @F005

Real-time status updates via WebSocket.

**Connection:**
```
wss://api.punchanalytics.com/ws/status/{analysis_id}?token={access_token}
```

**Server Messages:**

```json
// Progress update
{
  "type": "progress",
  "stage": "pose_estimation",
  "progress_percent": 70,
  "message": "Processing frame 2100 of 3000"
}

// Stage complete
{
  "type": "stage_complete",
  "stage": "pose_estimation",
  "next_stage": "stamp_generation"
}

// Analysis complete
{
  "type": "complete",
  "report_id": "rpt_mno345"
}

// Error
{
  "type": "error",
  "code": "POSE_QUALITY_LOW",
  "message": "Unable to track subject clearly",
  "user_action": "Please upload video with better lighting"
}
```

---

### Reports @F008, @F009, @F010

#### GET /reports/{report_id} @F008

Returns full report data.

**Success Response (200):**
```json
{
  "report_id": "rpt_mno345",
  "video_id": "vid_abc123",
  "analysis_id": "anl_jkl012",
  "created_at": "2026-01-21T13:03:28Z",
  "video_duration_seconds": 120,
  "body_specs": {
    "height_cm": 175,
    "weight_kg": 70,
    "experience_level": "intermediate",
    "stance": "orthodox"
  },
  "summary": {
    "overall_assessment": "Solid intermediate-level technique with room for improvement in defensive positioning",
    "performance_score": 72
  },
  "strengths": [
    {
      "title": "Consistent Jab Mechanics",
      "description": "Your jab demonstrates good extension and snap. Shoulder rotation averages 42 degrees, which is within optimal range.",
      "metric_reference": "jab_extension_ratio"
    },
    {
      "title": "Punch Frequency",
      "description": "You maintain an active offensive pace with 2.3 punches per 10 seconds, above average for your experience level.",
      "metric_reference": "punch_frequency"
    }
  ],
  "weaknesses": [
    {
      "title": "Guard Recovery Delay",
      "description": "After throwing combinations, your guard takes 0.8 seconds to return to defensive position. Target is under 0.5 seconds.",
      "metric_reference": "guard_recovery_speed"
    },
    {
      "title": "Upper Body Tilt",
      "description": "You lean forward 15 degrees during straights, exposing your chin. Maintain more upright posture.",
      "metric_reference": "upper_body_tilt"
    }
  ],
  "recommendations": [
    {
      "title": "Guard Recovery Drill",
      "description": "Practice shadowboxing with immediate guard return after each punch. Use a mirror to confirm hand position.",
      "priority": "high",
      "drill_type": "shadowboxing"
    },
    {
      "title": "Balance Work",
      "description": "Perform heavy bag work while focusing on staying centered. Film yourself from the side to check tilt.",
      "priority": "medium",
      "drill_type": "heavy_bag"
    }
  ],
  "metrics": {
    "punch_frequency": {
      "value": 2.3,
      "unit": "punches_per_10s",
      "benchmark_min": 1.5,
      "benchmark_max": 3.0,
      "percentile": 65
    },
    "jab_extension_ratio": {
      "value": 0.92,
      "unit": "ratio",
      "benchmark_min": 0.85,
      "benchmark_max": 1.0,
      "percentile": 78
    },
    "guard_recovery_speed": {
      "value": 0.8,
      "unit": "seconds",
      "benchmark_min": 0.3,
      "benchmark_max": 0.5,
      "percentile": 35
    },
    "upper_body_tilt": {
      "value": 15,
      "unit": "degrees",
      "benchmark_min": 0,
      "benchmark_max": 10,
      "percentile": 28
    },
    "reach_distance_ratio": {
      "value": 0.78,
      "unit": "ratio",
      "benchmark_min": 0.70,
      "benchmark_max": 0.85,
      "percentile": 55
    }
  },
  "stamps": [
    {
      "stamp_id": "stmp_001",
      "timestamp_seconds": 12.5,
      "frame_number": 375,
      "action_type": "jab",
      "side": "left",
      "confidence": 0.94,
      "thumbnail_url": "https://cdn.punchanalytics.com/stamps/rpt_mno345/stmp_001.jpg"
    },
    {
      "stamp_id": "stmp_002",
      "timestamp_seconds": 15.2,
      "frame_number": 456,
      "action_type": "straight",
      "side": "right",
      "confidence": 0.91
    },
    {
      "stamp_id": "stmp_003",
      "timestamp_seconds": 23.8,
      "frame_number": 714,
      "action_type": "guard_down",
      "side": "both",
      "confidence": 0.88
    }
  ],
  "disclaimer": "This AI analysis is for training purposes only and is not a substitute for professional coaching. Always train under proper supervision.",
  "sharing": {
    "is_shared": false,
    "share_url": null
  }
}
```

---

#### POST /reports/{report_id}/share @F009

Enables or updates sharing for a report.

**Request:**
```json
{
  "enabled": true
}
```

**Success Response (200 - Enabled):**
```json
{
  "report_id": "rpt_mno345",
  "is_shared": true,
  "share_hash": "Xk9mPq2r",
  "share_url": "https://punchanalytics.com/share/Xk9mPq2r",
  "created_at": "2026-01-21T14:00:00Z"
}
```

**Success Response (200 - Disabled):**
```json
{
  "report_id": "rpt_mno345",
  "is_shared": false,
  "share_hash": null,
  "share_url": null,
  "revoked_at": "2026-01-21T14:05:00Z"
}
```

---

#### GET /reports/{report_id}/share @F009

Returns sharing status for a report.

**Success Response (200):**
```json
{
  "report_id": "rpt_mno345",
  "is_shared": true,
  "share_hash": "Xk9mPq2r",
  "share_url": "https://punchanalytics.com/share/Xk9mPq2r",
  "views": 12,
  "created_at": "2026-01-21T14:00:00Z"
}
```

---

#### GET /share/{share_hash} @F009

Public endpoint for viewing shared reports (no authentication required).

**Success Response (200):**
Same structure as GET /reports/{report_id}, but without owner-specific fields.

**Error Response (404):**
```json
{
  "error": "not_found",
  "error_description": "This report is no longer shared or does not exist"
}
```

**Response Headers:**
```
Cache-Control: public, max-age=300
X-Robots-Tag: noindex
```

**Open Graph Meta (for social preview):**
```html
<meta property="og:title" content="Boxing Analysis Report - PunchAnalytics">
<meta property="og:description" content="Performance score: 72/100. View detailed analysis.">
<meta property="og:image" content="https://cdn.punchanalytics.com/og/rpt_mno345.png">
<meta property="og:url" content="https://punchanalytics.com/share/Xk9mPq2r">
```

---

#### GET /reports @F010

Lists user's reports.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 20 | Max results (1-100) |
| `offset` | integer | 0 | Pagination offset |
| `sort` | string | "created_at:desc" | Sort field and direction |

**Success Response (200):**
```json
{
  "reports": [
    {
      "report_id": "rpt_mno345",
      "video_id": "vid_abc123",
      "created_at": "2026-01-21T13:03:28Z",
      "video_duration_seconds": 120,
      "performance_score": 72,
      "thumbnail_url": "https://cdn.punchanalytics.com/thumbnails/vid_abc123/frame_030.jpg",
      "is_shared": true
    },
    {
      "report_id": "rpt_xyz789",
      "video_id": "vid_def456",
      "created_at": "2026-01-14T10:15:00Z",
      "video_duration_seconds": 95,
      "performance_score": 68,
      "thumbnail_url": "https://cdn.punchanalytics.com/thumbnails/vid_def456/frame_030.jpg",
      "is_shared": false
    }
  ],
  "pagination": {
    "total": 5,
    "limit": 20,
    "offset": 0,
    "has_more": false
  }
}
```

**Success Response (200 - Empty):**
```json
{
  "reports": [],
  "pagination": {
    "total": 0,
    "limit": 20,
    "offset": 0,
    "has_more": false
  }
}
```

---

#### DELETE /reports/{report_id} @F010

Soft-deletes a report.

**Success Response (200):**
```json
{
  "report_id": "rpt_mno345",
  "deleted": true,
  "deleted_at": "2026-01-21T15:00:00Z"
}
```

---

## Errors

### Error Response Format

All error responses follow this structure:

```json
{
  "error": "error_code",
  "error_description": "Human-readable description",
  "details": {
    "field": "Additional context (optional)"
  },
  "request_id": "req_abc123xyz"
}
```

### Error Codes

#### Authentication Errors (401, 403)

| Code | HTTP | Description |
|------|------|-------------|
| `unauthorized` | 401 | Missing or invalid access token |
| `token_expired` | 401 | Access token has expired |
| `invalid_refresh_token` | 401 | Refresh token invalid or expired |
| `forbidden` | 403 | User does not have access to this resource |
| `oauth_error` | 400 | OAuth flow error (code invalid, state mismatch) |

#### Validation Errors (400, 422)

| Code | HTTP | Description |
|------|------|-------------|
| `validation_error` | 422 | Request body failed validation |
| `invalid_file_type` | 400 | Unsupported file format |
| `file_too_large` | 400 | File exceeds 500MB limit |
| `duration_invalid` | 400 | Video duration outside 1-3 minute range |
| `chunk_mismatch` | 400 | Chunk MD5 does not match |

#### Resource Errors (404, 409)

| Code | HTTP | Description |
|------|------|-------------|
| `not_found` | 404 | Requested resource does not exist |
| `upload_not_found` | 404 | Upload session not found or expired |
| `chunk_exists` | 409 | Chunk already uploaded |
| `analysis_in_progress` | 409 | Analysis already running for this video |

#### Processing Errors (500, 502)

| Code | HTTP | Description |
|------|------|-------------|
| `processing_failed` | 500 | Analysis pipeline failed |
| `pose_quality_low` | 422 | Video quality insufficient for analysis |
| `subject_tracking_lost` | 422 | Could not track subject through video |
| `llm_unavailable` | 502 | LLM API unavailable after retries |
| `internal_error` | 500 | Unexpected server error |

#### Rate Limiting (429)

| Code | HTTP | Description |
|------|------|-------------|
| `rate_limit_exceeded` | 429 | Too many requests |
| `upload_limit_exceeded` | 429 | Upload limit (5/hour) exceeded |

**Rate Limit Response:**
```json
{
  "error": "rate_limit_exceeded",
  "error_description": "Too many requests. Please wait before retrying.",
  "details": {
    "retry_after_seconds": 60,
    "limit": 100,
    "window": "1 minute"
  }
}
```

**Response Headers:**
```
Retry-After: 60
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1705845600
```

---

## Examples

### Example 1: Complete Upload Flow @F002

```bash
# 1. Initiate upload
curl -X POST https://api.punchanalytics.com/api/v1/upload/initiate \
  -H "Authorization: Bearer eyJhbG..." \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "sparring.mp4",
    "file_size": 52428800,
    "content_type": "video/mp4",
    "duration_seconds": 120
  }'

# Response:
# {
#   "upload_id": "upl_x1y2z3",
#   "chunk_size": 5242880,
#   "total_chunks": 10
# }

# 2. Upload chunks (repeat for each chunk)
curl -X PUT "https://api.punchanalytics.com/api/v1/upload/chunk/upl_x1y2z3/0" \
  -H "Authorization: Bearer eyJhbG..." \
  -H "Content-Type: application/octet-stream" \
  -H "Content-MD5: rL0Y20zC+Fzt72VPzMSk2A==" \
  --data-binary @chunk_0.bin

# 3. Complete upload
curl -X POST https://api.punchanalytics.com/api/v1/upload/complete/upl_x1y2z3 \
  -H "Authorization: Bearer eyJhbG..."

# Response:
# {
#   "video_id": "vid_abc123",
#   "status": "processing_thumbnails"
# }
```

### Example 2: Subject Selection @F003

```bash
# 1. Get thumbnails (poll until ready)
curl https://api.punchanalytics.com/api/v1/analysis/thumbnails/vid_abc123 \
  -H "Authorization: Bearer eyJhbG..."

# 2. Select subject
curl -X POST https://api.punchanalytics.com/api/v1/analysis/subject/vid_abc123 \
  -H "Authorization: Bearer eyJhbG..." \
  -H "Content-Type: application/json" \
  -d '{
    "person_id": "p1",
    "frame_number": 30
  }'
```

### Example 3: Start Analysis and Monitor @F005

```bash
# 1. Submit body specs
curl -X POST https://api.punchanalytics.com/api/v1/analysis/body-specs/vid_abc123 \
  -H "Authorization: Bearer eyJhbG..." \
  -H "Content-Type: application/json" \
  -d '{
    "height_cm": 175,
    "weight_kg": 70,
    "experience_level": "intermediate",
    "stance": "orthodox"
  }'

# 2. Start analysis
curl -X POST https://api.punchanalytics.com/api/v1/analysis/start/vid_abc123 \
  -H "Authorization: Bearer eyJhbG..." \
  -H "Content-Type: application/json" \
  -d '{
    "subject_id": "subj_def456",
    "body_specs_id": "bs_ghi789"
  }'

# Response includes WebSocket URL for real-time updates
```

### Example 4: WebSocket Status Monitoring @F005

```javascript
// JavaScript client example
const ws = new WebSocket(
  'wss://api.punchanalytics.com/ws/status/anl_jkl012?token=eyJhbG...'
);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch (data.type) {
    case 'progress':
      console.log(`${data.stage}: ${data.progress_percent}%`);
      break;
    case 'stage_complete':
      console.log(`${data.stage} complete, starting ${data.next_stage}`);
      break;
    case 'complete':
      console.log(`Report ready: ${data.report_id}`);
      ws.close();
      break;
    case 'error':
      console.error(`Error: ${data.message}`);
      ws.close();
      break;
  }
};
```

### Example 5: Share Report @F009

```bash
# Enable sharing
curl -X POST https://api.punchanalytics.com/api/v1/reports/rpt_mno345/share \
  -H "Authorization: Bearer eyJhbG..." \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# Response:
# {
#   "is_shared": true,
#   "share_url": "https://punchanalytics.com/share/Xk9mPq2r"
# }

# View shared report (no auth required)
curl https://api.punchanalytics.com/api/v1/share/Xk9mPq2r
```

---

## Idempotency

### Idempotent Operations

| Endpoint | Idempotency Key | Behavior |
|----------|-----------------|----------|
| PUT /upload/chunk/{id}/{num} | chunk_number | Returns success if chunk already uploaded |
| POST /analysis/start | video_id | Returns existing analysis if in progress |
| POST /reports/{id}/share | report_id + enabled | Toggle is idempotent |

### Non-Idempotent Operations

| Endpoint | Behavior |
|----------|----------|
| POST /upload/initiate | Always creates new upload session |
| POST /auth/refresh | Always issues new access token |

---

## Versioning

- Current version: `v1`
- Version in URL path: `/api/v1/...`
- Breaking changes will increment version
- Deprecation notice: 6 months before removal
- Version header for negotiation: `Accept: application/vnd.punchanalytics.v1+json`

---

## Rate Limits

| Endpoint Category | Limit | Window |
|-------------------|-------|--------|
| Authentication | 10 requests | 1 minute |
| Upload initiate | 5 requests | 1 hour |
| Upload chunk | 1000 requests | 1 hour |
| General API | 100 requests | 1 minute |
| WebSocket connections | 5 concurrent | per user |

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705845600
```
