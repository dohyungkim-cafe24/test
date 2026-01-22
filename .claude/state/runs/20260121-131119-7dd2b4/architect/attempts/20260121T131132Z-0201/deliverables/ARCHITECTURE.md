# PunchAnalytics - System Architecture

## Inputs

- `docs/product/REQUIREMENTS_BASELINE.md`
- `docs/product/MARKET_BENCHMARK.md`
- `docs/product/STORY_MAP.md`
- `docs/product/PRD.md`
- `features.json`
- `specs/bdd/TRACEABILITY.json`
- `specs/bdd/BDD_INDEX.json`
- `docs/ux/UX_CONTRACT.md`
- `docs/ux/DESIGN_SYSTEM.md`

---

## Overview

PunchAnalytics is an AI-powered boxing sparring analysis platform that transforms smartphone video into strategic coaching feedback. The system processes uploaded sparring videos through a pose estimation pipeline (MediaPipe), detects key moments (strikes, defensive actions), and generates LLM-based coaching reports.

### System Context Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                    USERS                                         │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐                    │
│  │  Amateur      │    │  Coaches      │    │  Shared Link  │                    │
│  │  Boxers       │    │  (view shared)│    │  Viewers      │                    │
│  └───────┬───────┘    └───────┬───────┘    └───────┬───────┘                    │
└──────────┼────────────────────┼────────────────────┼────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              PUNCHANALYTICS                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                        Frontend (Next.js)                                │    │
│  │  @F001 Auth │ @F002 Upload │ @F003-F004 Config │ @F008-F010 Reports      │    │
│  └───────────────────────────────────────┬─────────────────────────────────┘    │
│                                          │                                       │
│  ┌───────────────────────────────────────┴─────────────────────────────────┐    │
│  │                        Backend API (FastAPI)                             │    │
│  │  REST Endpoints │ Auth Middleware │ Job Queue │ WebSocket (status)       │    │
│  └───────────────────────────────────────┬─────────────────────────────────┘    │
│                                          │                                       │
│  ┌───────────────────────────────────────┴─────────────────────────────────┐    │
│  │                     Processing Pipeline (Workers)                        │    │
│  │  @F005 Pose Est. │ @F006 Stamps │ @F007 LLM Analysis                     │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   PostgreSQL    │  │  Object Storage │  │   Redis         │                  │
│  │   (metadata)    │  │  (S3/videos)    │  │   (cache/queue) │                  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────────┘
           │                                          │
           ▼                                          ▼
┌─────────────────────────────┐        ┌─────────────────────────────┐
│     EXTERNAL SERVICES       │        │     IDENTITY PROVIDERS      │
│  ┌───────────────────────┐  │        │  ┌───────────────────────┐  │
│  │  LLM API (GPT-4)      │  │        │  │  Kakao OAuth 2.0      │  │
│  │  - Strategic analysis │  │        │  │  Google OAuth 2.0     │  │
│  └───────────────────────┘  │        │  └───────────────────────┘  │
└─────────────────────────────┘        └─────────────────────────────┘
```

---

## Goals

1. **Enable end-to-end video analysis within 5 minutes** (p95 latency requirement)
2. **Support 100+ concurrent active users** without degradation
3. **Provide real-time progress feedback** during video processing
4. **Ensure data privacy** with private-by-default reports
5. **Enable frictionless sharing** via unique URLs with social previews

## Non-goals

1. Real-time live video analysis during sparring
2. Multi-person automatic tracking (manual subject selection required)
3. Custom ML model training (use pre-trained MediaPipe)
4. Payment processing or subscription management
5. Native mobile applications (responsive web only)

---

## Components

### Frontend (Next.js 14 App Router) @F001-F010

**Technology:** Next.js 14 with App Router, TypeScript, Material UI v5 (M3 tokens)

**Responsibilities:**
- Server-side rendering for public pages (landing, shared reports)
- Client-side auth state management via OAuth callbacks
- Chunked video upload with progress tracking
- Real-time processing status via WebSocket/SSE
- Report visualization with Chart.js

**Key modules:**

| Module | Feature | Description |
|--------|---------|-------------|
| `/app/(auth)` | @F001 | OAuth login/callback, session management |
| `/app/upload` | @F002 | Video upload with resumable chunked upload |
| `/app/configure` | @F003, @F004 | Subject selection, body specs form |
| `/app/processing` | @F005-F007 | Status polling, progress display |
| `/app/report/[id]` | @F008, @F009 | Report view, share controls |
| `/app/dashboard` | @F010 | Report history list |
| `/app/share/[hash]` | @F009 | Public shared report view |

**State Management:**
- Server Components for initial data fetch
- React Context for auth state
- SWR for client-side data caching with revalidation

---

### Backend API (FastAPI) @F001-F010

**Technology:** FastAPI (Python 3.11+), async I/O, Pydantic v2

**Responsibilities:**
- REST API endpoints for all features
- OAuth 2.0 callback handling and session management
- Job dispatch to processing workers
- WebSocket endpoints for real-time status updates
- Signed URL generation for video uploads/downloads

**API Layer Structure:**

```
/api/v1
├── /auth          @F001
│   ├── /kakao/callback
│   ├── /google/callback
│   └── /logout
├── /upload        @F002
│   ├── /initiate
│   ├── /chunk/{upload_id}
│   └── /complete/{upload_id}
├── /analysis      @F003, @F004
│   ├── /thumbnails/{video_id}
│   ├── /subject/{video_id}
│   └── /body-specs/{video_id}
├── /processing    @F005, @F006, @F007
│   └── /status/{analysis_id}
├── /reports       @F008, @F009, @F010
│   ├── /{report_id}
│   ├── /{report_id}/share
│   └── /list
└── /ws
    └── /status/{analysis_id}
```

**Middleware:**
- CORS (configured for frontend origin)
- Rate limiting (upload: 5/hour/user, API: 100/min/user)
- Request ID injection for tracing
- Auth middleware (JWT validation)

---

### Processing Pipeline (Celery Workers) @F005, @F006, @F007

**Technology:** Celery with Redis broker, MediaPipe Python, OpenAI API

**Responsibilities:**
- Asynchronous video processing
- Pose estimation (33-joint extraction)
- Stamp detection (strike/defense classification)
- LLM analysis generation
- Status updates to Redis

**Pipeline Stages:**

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│  1. Thumbnail  │────▶│  2. Pose       │────▶│  3. Stamp      │────▶│  4. LLM        │
│  Extraction    │     │  Estimation    │     │  Generation    │     │  Analysis      │
│                │     │                │     │                │     │                │
│  @F003         │     │  @F005         │     │  @F006         │     │  @F007         │
│  - 10 frames   │     │  - MediaPipe   │     │  - Velocity    │     │  - GPT-4       │
│  - 1s interval │     │  - 33 joints   │     │  - Trajectory  │     │  - Prompt eng  │
│  - Person det  │     │  - Subject trk │     │  - Confidence  │     │  - Retry logic │
└────────────────┘     └────────────────┘     └────────────────┘     └────────────────┘
        │                      │                      │                      │
        └──────────────────────┴──────────────────────┴──────────────────────┘
                                        │
                                        ▼
                            ┌────────────────────────┐
                            │  5. Report Generation  │
                            │  @F008                 │
                            │  - Metrics calc        │
                            │  - JSON structure      │
                            │  - DB persist          │
                            └────────────────────────┘
```

**Worker Configuration:**
- 2 workers per CPU core (configurable)
- Task timeout: 5 minutes per video (hard limit)
- Retry policy: 3 attempts with exponential backoff (LLM calls)
- Priority queues: thumbnail (high), pose (medium), llm (low)

---

### Data Storage

**PostgreSQL 15** (primary database):
- User accounts and profiles
- Video metadata (not binary)
- Analysis records and status
- Reports (structured JSON)
- Stamps with timestamps
- Share links

**S3-Compatible Object Storage** (video/media):
- Raw uploaded videos
- Extracted thumbnails
- Processed pose data (JSON)

**Redis 7** (cache/queue):
- Celery task broker
- Session cache
- Processing status pub/sub
- Rate limiting counters

---

## Data Flow

### Upload-to-Report Flow

```
User              Frontend           API             Workers           Storage
 │                   │                │                 │                 │
 │──Upload Video────▶│                │                 │                 │
 │                   │──Init Upload──▶│                 │                 │
 │                   │◀──Upload URL───│                 │                 │
 │                   │                │                 │                 │
 │                   │──Chunk 1──────▶│─────────────────────────────────▶│ S3
 │                   │──Chunk 2──────▶│                 │                 │
 │                   │──Chunk N──────▶│                 │                 │
 │                   │──Complete─────▶│                 │                 │
 │                   │◀──Video ID─────│                 │                 │
 │                   │                │                 │                 │
 │◀─Thumbnails──────│◀───────────────│◀──Thumbnails───│◀────────────────│
 │                   │                │                 │                 │
 │──Select Subject─▶│──Subject ID───▶│                 │                 │
 │──Body Specs─────▶│──Body Specs───▶│                 │                 │
 │──Start Analysis─▶│──Start────────▶│                 │                 │
 │                   │◀──Analysis ID──│──Queue Job────▶│                 │
 │                   │                │                 │                 │
 │                   │◀──Status WS────│◀──Progress─────│──Pose Est.────▶│
 │                   │◀──Status WS────│◀──Progress─────│──Stamps───────▶│
 │                   │◀──Status WS────│◀──Progress─────│──LLM─────────▶│
 │                   │◀──Complete─────│◀──Complete─────│──Report───────▶│ DB
 │                   │                │                 │                 │
 │◀─View Report─────│◀─Report Data───│                 │                 │
 │                   │                │                 │                 │
```

---

## Trade-offs

### Decision 1: FastAPI vs Node.js Backend

**Chosen:** FastAPI (Python)

**Rationale:**
- MediaPipe has first-class Python bindings; Node.js would require Python subprocess or WASM
- Celery is the most mature task queue for long-running ML workloads
- Type hints with Pydantic provide comparable DX to TypeScript

**Trade-off:**
- Lose shared code between frontend and backend
- Need to maintain two language ecosystems

**Alternatives rejected:**
- Node.js: Would require Python subprocess for MediaPipe, adding complexity
- Go: Excellent performance but poor ML library ecosystem

---

### Decision 2: Chunked Upload vs Direct S3 Upload

**Chosen:** Backend-mediated chunked upload with signed URLs

**Rationale:**
- Enables resumable uploads for mobile networks (competitor gap)
- Allows server-side validation before accepting chunks
- Maintains upload rate limiting at application layer

**Trade-off:**
- Backend must handle chunk assembly
- Slightly higher latency than direct-to-S3

**Alternatives rejected:**
- Direct S3 presigned POST: No resumability, harder to rate limit
- tus protocol: Additional infrastructure complexity

---

### Decision 3: WebSocket vs Polling for Status Updates

**Chosen:** WebSocket with SSE fallback

**Rationale:**
- Processing takes 2-5 minutes; polling every 5s creates unnecessary load
- WebSocket provides instant status updates for better UX
- SSE fallback handles environments where WebSocket fails

**Trade-off:**
- More complex connection management
- Need to handle reconnection logic

**Alternatives rejected:**
- Polling only: Wasteful for long-running processes
- Push notifications: Overkill for in-session updates (P1 feature for background)

---

### Decision 4: Synchronous vs Asynchronous Pose Estimation

**Chosen:** Asynchronous (Celery workers)

**Rationale:**
- Video processing is CPU-intensive (2-5 minutes)
- Blocking API requests would exhaust connection pool
- Worker isolation prevents cascading failures

**Trade-off:**
- Added infrastructure (Redis, Celery)
- More complex deployment

**Alternatives rejected:**
- Synchronous processing: Would block API and cause timeouts
- Serverless functions: Cold start latency too high for MediaPipe

---

### Decision 5: Single LLM Call vs Multi-Turn

**Chosen:** Single comprehensive prompt with structured output

**Rationale:**
- Reduces API latency (1 call instead of 3-5)
- GPT-4 handles multi-aspect analysis well in single prompt
- Consistent output structure for parsing

**Trade-off:**
- Less flexibility for complex follow-up analysis
- Larger token consumption per call

**Alternatives rejected:**
- Multi-turn conversation: Higher latency, more failure points
- Multiple parallel calls: Hard to maintain coherent analysis

---

## Observability

### Logging

**Structured JSON logging with:**
- Request ID (correlation)
- User ID (when authenticated)
- Analysis ID (for processing)
- Timestamp (ISO8601)
- Level (DEBUG/INFO/WARN/ERROR)

**Key log events:**

| Event | Level | Fields | Purpose |
|-------|-------|--------|---------|
| `upload.started` | INFO | user_id, file_size, content_type | Track upload initiation |
| `upload.chunk` | DEBUG | upload_id, chunk_num, bytes | Debug upload issues |
| `upload.completed` | INFO | upload_id, video_id, duration_ms | Upload success metric |
| `processing.started` | INFO | analysis_id, video_id, user_id | Pipeline start |
| `processing.stage` | INFO | analysis_id, stage, progress_pct | Progress tracking |
| `processing.failed` | ERROR | analysis_id, stage, error_type, message | Failure diagnosis |
| `processing.completed` | INFO | analysis_id, total_duration_ms | Success metric |
| `llm.request` | INFO | analysis_id, prompt_tokens | Cost tracking |
| `llm.response` | INFO | analysis_id, completion_tokens, duration_ms | Performance |
| `llm.error` | ERROR | analysis_id, error_type, retry_count | Retry debugging |

---

### Metrics (RED/USE)

**Request metrics (Prometheus):**

| Metric | Type | Labels | Purpose |
|--------|------|--------|---------|
| `http_requests_total` | Counter | method, path, status | Request volume |
| `http_request_duration_seconds` | Histogram | method, path | Latency distribution |
| `http_request_size_bytes` | Histogram | method, path | Payload sizes |

**Processing metrics:**

| Metric | Type | Labels | Purpose |
|--------|------|--------|---------|
| `processing_jobs_total` | Counter | stage, status | Job completion |
| `processing_duration_seconds` | Histogram | stage | Stage latency |
| `processing_queue_size` | Gauge | queue | Backlog monitoring |
| `pose_estimation_joints_detected` | Histogram | | Quality tracking |
| `stamps_detected_total` | Counter | type | Action detection |
| `llm_tokens_used` | Counter | direction | Cost tracking |

**Resource metrics (USE):**

| Metric | Type | Labels | Purpose |
|--------|------|--------|---------|
| `cpu_usage_percent` | Gauge | service | Utilization |
| `memory_usage_bytes` | Gauge | service | Memory pressure |
| `disk_usage_percent` | Gauge | mount | Storage capacity |
| `db_connections_active` | Gauge | pool | Connection saturation |
| `redis_memory_used_bytes` | Gauge | | Cache pressure |

---

### Tracing (OpenTelemetry)

**Trace spans for key flows:**

```
upload_video (root)
├── validate_file
├── initiate_upload
├── chunk_upload (N chunks)
└── complete_upload

process_analysis (root)
├── extract_thumbnails
├── pose_estimation
│   ├── decode_video
│   ├── mediapipe_inference
│   └── subject_tracking
├── stamp_generation
│   ├── velocity_detection
│   └── action_classification
├── llm_analysis
│   ├── format_prompt
│   ├── api_call
│   └── parse_response
└── generate_report
```

---

### Alerting

| Alert | Condition | Severity | Response |
|-------|-----------|----------|----------|
| High error rate | 5xx > 1% over 5 min | Critical | Page on-call |
| Processing queue backlog | Queue > 50 jobs for 10 min | Warning | Scale workers |
| LLM API failures | Retry exhaustion > 5% | High | Check API status |
| Upload failures | Error rate > 5% | High | Check S3 connectivity |
| Database connections | Pool > 80% utilized | Warning | Review connection leaks |
| Processing latency | p95 > 6 min | Warning | Investigate slow videos |

---

## Security

### Authentication and Authorization @F001

**AuthN model:**
- OAuth 2.0 with PKCE for Kakao and Google
- JWT access tokens (15-minute expiry)
- Refresh tokens (7-day expiry, stored server-side)
- Session cookies (HttpOnly, Secure, SameSite=Strict)

**AuthZ model:**
- Users can only access their own resources (videos, reports)
- Shared reports are read-only for non-owners
- No role-based access in V1 (single user type)

### Trust Boundaries

```
┌─────────────────────────────────────────────────────────────────────┐
│                         UNTRUSTED                                    │
│  - User-uploaded video files (malware scanning required)            │
│  - OAuth callback parameters                                         │
│  - All client-side form inputs                                       │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                          Input Validation
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         SEMI-TRUSTED                                 │
│  - LLM API responses (may hallucinate, need sanitization)           │
│  - MediaPipe output (validated structure, not content)              │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                           Sanitization
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          TRUSTED                                     │
│  - Database records (written by validated application logic)        │
│  - Internal service-to-service calls (VPC-internal, mTLS)           │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Protection

| Data Type | Classification | At Rest | In Transit | Retention |
|-----------|---------------|---------|------------|-----------|
| User profile (email, name) | PII | AES-256 | TLS 1.3 | Account lifetime |
| OAuth tokens | Secret | AES-256 | TLS 1.3 | Token expiry |
| Video files | User content | AES-256 (S3 SSE) | TLS 1.3 | Until deleted |
| Pose data (JSON) | Derived | AES-256 | TLS 1.3 | Report lifetime |
| Analysis reports | User content | AES-256 | TLS 1.3 | Until deleted |

### Input Validation

| Input | Validation | Rejection |
|-------|------------|-----------|
| Video file | Magic bytes (MP4/MOV/WebM), size < 500MB, duration 1-3 min | 400 Bad Request |
| OAuth state | CSRF token match | 403 Forbidden |
| Body specs | Height 100-250cm, Weight 30-200kg, enum values | 422 Validation Error |
| Report ID | UUID format, ownership check | 403/404 |
| Share hash | 8-char alphanumeric, active check | 404 |

### Secrets Management

- Application secrets in environment variables (not in code)
- OAuth client secrets in cloud secret manager
- Database credentials rotated monthly
- LLM API keys scoped to project

---

## Deployment

### Infrastructure (Cloud-agnostic, reference: AWS)

| Component | Service | Sizing (initial) |
|-----------|---------|------------------|
| Frontend | Vercel / CloudFront + S3 | Edge-distributed |
| Backend API | ECS Fargate / Cloud Run | 2 vCPU, 4GB RAM, 2-4 instances |
| Workers | ECS Fargate (CPU-optimized) | 4 vCPU, 8GB RAM, 2-8 instances |
| Database | RDS PostgreSQL | db.t3.medium, Multi-AZ |
| Object Storage | S3 | Standard tier, lifecycle to IA after 30 days |
| Cache/Queue | ElastiCache Redis | cache.t3.micro, single node |
| CDN | CloudFront | For static assets and shared reports |

### Scaling Strategy

| Component | Trigger | Action |
|-----------|---------|--------|
| API instances | CPU > 70% for 2 min | Add instance (max 8) |
| Worker instances | Queue depth > 20 | Add instance (max 16) |
| Database | Connection count > 80% | Consider read replica |

### Rollout Plan

1. **Blue-green deployment** for API changes (zero-downtime)
2. **Canary release** for worker algorithm changes (10% traffic, monitor errors)
3. **Feature flags** for frontend features (gradual rollout)
4. **Database migrations** run before deployment (backward compatible)

---

## Failure Modes and Mitigations

| Failure Mode | Detection | Mitigation | Recovery |
|--------------|-----------|------------|----------|
| S3 unavailable | Upload errors spike | Show "Service temporarily unavailable" | Automatic when S3 recovers |
| Worker crash mid-processing | Job timeout | Auto-retry from last checkpoint | Job restarts from last stage |
| LLM API rate limit | 429 responses | Exponential backoff, queue | Automatic after cooldown |
| LLM API down | Connection errors | Retry 3x, then fail with user notification | User can retry manually |
| Database connection exhaustion | Pool timeout errors | Connection pooling, query optimization | Scale connection pool |
| Redis unavailable | Queue operations fail | Fallback to polling for status | Automatic when Redis recovers |
| Video too dark/blurry | Pose estimation < 80% frames | Fail with "improve video quality" message | User uploads better video |
| Subject lost during video | Tracking confidence drops | Partial analysis with warning | User can accept or re-upload |

---

## Open Questions

| Question | Impact | Decision Owner | Deadline |
|----------|--------|----------------|----------|
| Should we implement client-side video compression? | Upload time, storage cost | Engineering | Before F002 implementation |
| What is the MediaPipe confidence threshold for acceptable pose? | Analysis quality | ML Engineer | Before F005 implementation |
| Should share links expire by default? | Privacy vs UX | Product | Before F009 implementation |
| GPU workers for faster pose estimation? | Processing latency, cost | Engineering + SRE | Before production scaling |

---

## Appendix: Feature to Component Mapping

| Feature | Frontend | Backend | Workers | Storage |
|---------|----------|---------|---------|---------|
| @F001 Auth | `/app/(auth)/*` | `/api/v1/auth/*` | - | PostgreSQL (users) |
| @F002 Upload | `/app/upload` | `/api/v1/upload/*` | - | S3 (videos) |
| @F003 Subject Selection | `/app/configure/subject` | `/api/v1/analysis/thumbnails/*` | Thumbnail task | S3 (thumbnails) |
| @F004 Body Specs | `/app/configure/specs` | `/api/v1/analysis/body-specs/*` | - | PostgreSQL (body_specs) |
| @F005 Pose Estimation | `/app/processing` | `/api/v1/processing/status/*` | Pose task | S3 (pose_data) |
| @F006 Stamp Generation | `/app/processing` | - | Stamp task | PostgreSQL (stamps) |
| @F007 LLM Analysis | `/app/processing` | - | LLM task | PostgreSQL (analysis) |
| @F008 Report Display | `/app/report/[id]` | `/api/v1/reports/{id}` | - | PostgreSQL (reports) |
| @F009 Report Sharing | `/app/report/[id]`, `/app/share/[hash]` | `/api/v1/reports/{id}/share` | - | PostgreSQL (share_links) |
| @F010 Dashboard | `/app/dashboard` | `/api/v1/reports/list` | - | PostgreSQL (reports) |
