# PunchAnalytics Implementation Plan

## Inputs

- `docs/product/REQUIREMENTS_BASELINE.md` - Frozen requirements and quality bar
- `docs/product/MARKET_BENCHMARK.md` - Competitor analysis and market expectations
- `docs/product/STORY_MAP.md` - User stories US-001 through US-010 (P0 Launch scope)
- `docs/ux/UX_CONTRACT.md` - UX non-negotiables and quality criteria
- `docs/ux/DESIGN_SYSTEM.md` - Material Design 3 tokens and components
- `features.json` - Feature registry with BDD traces
- `specs/bdd/TRACEABILITY.json` - US to Feature to Scenario mapping
- `specs/bdd/BDD_INDEX.json` - All Gherkin scenarios by feature
- `docs/engineering/ARCHITECTURE.md` - System design and component mapping
- `docs/engineering/API.md` - REST API specification
- `docs/engineering/DATA_MODEL.md` - PostgreSQL schema and S3 storage

---

## Goals and Scope

### Goal
Deliver a production-ready AI-powered boxing sparring analysis platform that enables amateur boxers to receive strategic coaching feedback from smartphone video uploads.

### Launch Scope (P0)
All 10 features (F001-F010) are P0 Launch blockers:

| Feature | Name | Category |
|---------|------|----------|
| F001 | User Authentication | Web/Auth |
| F002 | Video Upload | Web/Upload |
| F003 | Subject Selection | Web |
| F004 | Body Specification Input | Web/Form |
| F005 | Pose Estimation Processing | Backend |
| F006 | Stamp Generation | Backend |
| F007 | LLM Strategic Analysis | Backend |
| F008 | Report Display | Web |
| F009 | Report Sharing | Web |
| F010 | Report History Dashboard | Web |

### Non-scope
- Real-time live video analysis
- Multi-person automatic tracking
- Payment processing
- Native mobile apps
- Community features beyond sharing

---

## Milestones

### M1: Core Infrastructure (Foundation)
**Target:** Week 1
**Features:** F001

**Exit criteria:**
- OAuth login functional with Kakao and Google
- JWT session management working
- Protected route middleware deployed
- User table migrations complete

### M2: Upload and Selection (Input Flow)
**Target:** Week 2
**Features:** F002, F003, F004

**Exit criteria:**
- Chunked upload with resume capability functional
- Thumbnail extraction pipeline working
- Subject selection UI complete with bounding box storage
- Body specs form with validation and persistence

### M3: Processing Pipeline (Backend Core)
**Target:** Week 3-4
**Features:** F005, F006, F007

**Exit criteria:**
- MediaPipe pose estimation extracting 33 joints
- Stamp detection identifying strikes and defensive actions
- LLM analysis generating structured coaching feedback
- Processing status updates via WebSocket
- p95 processing time under 5 minutes

### M4: Report and Sharing (Output Flow)
**Target:** Week 5
**Features:** F008, F009, F010

**Exit criteria:**
- Report display with all sections rendering correctly
- Metrics visualization with Chart.js
- Share link generation and public access working
- Dashboard listing reports with navigation
- All UI states (loading/empty/error/success) implemented

---

## Critical Path

```
F001 (Auth) ──► F002 (Upload) ──► F003 (Subject) ──► F004 (Body Specs)
                     │
                     ▼
              F005 (Pose Est.) ──► F006 (Stamps) ──► F007 (LLM)
                                                        │
                                                        ▼
                              F010 (Dashboard) ◄── F008 (Report) ──► F009 (Share)
```

**Blocking dependencies:**
1. F001 must complete before any authenticated feature
2. F002 must complete before F003 (thumbnails extracted from uploaded video)
3. F003 must complete before F005 (subject bounding box needed for tracking)
4. F005 must complete before F006 (pose data required for stamp detection)
5. F006 must complete before F007 (stamps included in LLM prompt)
6. F007 must complete before F008 (analysis content rendered in report)

---

## Work Breakdown

### Frontend (Next.js 14)

| Module | Features | Components |
|--------|----------|------------|
| `/app/(auth)` | F001 | Login page, OAuth callbacks, logout |
| `/app/upload` | F002 | Upload dropzone, progress bar, validation UI |
| `/app/configure` | F003, F004 | Thumbnail grid, subject selector, body specs form |
| `/app/processing` | F005-F007 | Status page, progress indicators |
| `/app/report/[id]` | F008, F009 | Report sections, metrics charts, share controls |
| `/app/dashboard` | F010 | Report list, empty state, delete confirmation |
| `/app/share/[hash]` | F009 | Public report view |

### Backend API (FastAPI)

| Route Group | Features | Endpoints |
|-------------|----------|-----------|
| `/api/v1/auth` | F001 | OAuth callbacks, refresh, logout, me |
| `/api/v1/upload` | F002 | Initiate, chunk, complete, cancel |
| `/api/v1/analysis` | F003, F004 | Thumbnails, subject, body-specs, start |
| `/api/v1/processing` | F005-F007 | Status endpoint, WebSocket |
| `/api/v1/reports` | F008-F010 | Get, list, share controls |

### Processing Workers (Celery)

| Task | Feature | Description |
|------|---------|-------------|
| `extract_thumbnails` | F003 | Extract 10 frames at 1s intervals |
| `pose_estimation` | F005 | MediaPipe 33-joint extraction |
| `stamp_detection` | F006 | Velocity and trajectory analysis |
| `llm_analysis` | F007 | GPT-4 strategic feedback |
| `generate_report` | F008 | Metrics calculation, report persistence |

### Data Layer

| Storage | Tables/Keys | Features |
|---------|-------------|----------|
| PostgreSQL | users, refresh_tokens | F001 |
| PostgreSQL | videos, upload_sessions, upload_chunks | F002 |
| PostgreSQL | thumbnails, subjects | F003 |
| PostgreSQL | body_specs | F004 |
| PostgreSQL | analyses | F005-F007 |
| PostgreSQL | stamps | F006 |
| PostgreSQL | reports, share_links | F008-F010 |
| S3 | videos/{user_id}/{video_id}.mp4 | F002 |
| S3 | thumbnails/{video_id}/ | F003 |
| S3 | pose_data/{analysis_id}/ | F005 |

---

## Feature Execution Cards

### F001: User Authentication

**Intent:** Enable boxers to access the platform via social accounts without creating new credentials.

**JTBD:** When I want to analyze my sparring video, I want to log in with my existing Kakao or Google account so I can quickly get started.

**Acceptance Criteria (BDD):**
- specs/bdd/auth.feature#Successful Kakao OAuth login
- specs/bdd/auth.feature#Successful Google OAuth login
- specs/bdd/auth.feature#User logs out successfully
- specs/bdd/auth.feature#Unauthenticated user redirected to login
- specs/bdd/auth.feature#Session expiration prompts re-authentication
- specs/bdd/auth.feature#OAuth login cancelled by user
- specs/bdd/auth.feature#OAuth provider unavailable

**UX Contract References:**
- UX_CONTRACT.md: Mobile-first responsive, WCAG 2.1 AA
- DESIGN_SYSTEM.md: Primary button (Login with Kakao), Secondary button (Login with Google)

**API References:**
- GET /auth/kakao, GET /auth/kakao/callback
- GET /auth/google, GET /auth/google/callback
- POST /auth/refresh, POST /auth/logout, GET /auth/me

**Data Model References:**
- users table (id, email, name, provider, provider_id)
- refresh_tokens table (token_hash, expires_at)

**Implementation Notes:**
1. Use next-auth or custom OAuth handler with PKCE
2. JWT access tokens (15 min), refresh tokens in HttpOnly cookies (7 days)
3. Middleware for protected routes
4. Store Kakao/Google user profile on first login

**Test Plan:**
- Unit: Token generation, validation, expiry logic
- Integration: OAuth callback handling, token refresh flow
- Runtime: Full login flow with real Kakao/Google test accounts
- Screenshots: Login page, OAuth redirect, dashboard after login

**Definition of Done:**
- [ ] OAuth flow completes for both providers
- [ ] Protected routes redirect to login
- [ ] Session persists across page refresh
- [ ] Logout clears all tokens
- [ ] BDD scenarios pass with runtime evidence
- [ ] Mobile and desktop screenshots captured

---

### F002: Video Upload

**Intent:** Accept sparring footage for AI analysis with reliable delivery on mobile networks.

**JTBD:** When I have a sparring video on my phone, I want to upload it reliably even on spotty connections so my analysis is not lost.

**Acceptance Criteria (BDD):**
- specs/bdd/upload.feature#Successful video upload with valid file
- specs/bdd/upload.feature#Upload shows progress indicator
- specs/bdd/upload.feature#File exceeds maximum size limit
- specs/bdd/upload.feature#Video duration too short
- specs/bdd/upload.feature#Video duration too long
- specs/bdd/upload.feature#Unsupported file format rejected
- specs/bdd/upload.feature#Upload resumes after network interruption
- specs/bdd/upload.feature#User cancels upload in progress
- specs/bdd/upload.feature#Upload area shows empty state initially

**UX Contract References:**
- UX_CONTRACT.md: Progress visibility, under 5 min processing
- UI_STATES.md: Empty, Loading (progress), Error (validation), Success (uploaded)
- DESIGN_SYSTEM.md: Linear progress indicator, error messages

**API References:**
- POST /upload/initiate
- PUT /upload/chunk/{upload_id}/{chunk_number}
- POST /upload/complete/{upload_id}
- DELETE /upload/{upload_id}

**Data Model References:**
- videos table (storage_key, upload_status, duration_seconds)
- upload_sessions table (chunks_received, status)
- upload_chunks table (chunk_number, storage_key)
- S3: videos/{user_id}/{video_id}.mp4

**Implementation Notes:**
1. Client-side validation before upload (size, duration via video element)
2. Chunked upload (5MB chunks) with MD5 verification
3. Resume by checking which chunks uploaded
4. Validate file magic bytes server-side (not just content-type)
5. Extract video metadata after assembly (ffprobe)

**Test Plan:**
- Unit: Chunk assembly, MD5 validation, file type detection
- Integration: Full upload flow, resume after interrupt
- Runtime: Upload real video files on throttled network
- Screenshots: Empty state, uploading progress, validation errors

**Definition of Done:**
- [ ] Files up to 500MB upload successfully
- [ ] Progress bar updates in real-time
- [ ] Upload resumes after network drop
- [ ] Invalid files rejected with clear messages
- [ ] BDD scenarios pass with runtime evidence
- [ ] Mobile viewport upload tested

---

### F003: Subject Selection

**Intent:** Identify the user in multi-person sparring footage for focused analysis.

**JTBD:** When my sparring video has multiple people, I want to tap on myself so the AI analyzes my technique, not my partner's.

**Acceptance Criteria (BDD):**
- specs/bdd/subject-selection.feature#Thumbnail grid displays extracted frames
- specs/bdd/subject-selection.feature#User selects subject from thumbnail
- specs/bdd/subject-selection.feature#User changes selection before confirmation
- specs/bdd/subject-selection.feature#User confirms subject selection
- specs/bdd/subject-selection.feature#Single person auto-selected
- specs/bdd/subject-selection.feature#No subjects detected in video
- specs/bdd/subject-selection.feature#Thumbnail extraction loading state

**UX Contract References:**
- UX_CONTRACT.md: Touch targets 48x48px minimum
- UI_STATES.md: Loading (skeleton), Empty (no persons), Success (selected)
- DESIGN_SYSTEM.md: Filled card, selection indicator (primary color border)

**API References:**
- GET /analysis/thumbnails/{video_id}
- POST /analysis/subject/{video_id}

**Data Model References:**
- thumbnails table (frame_number, detected_persons JSONB)
- subjects table (person_id, initial_bbox)
- S3: thumbnails/{video_id}/frame_{N}.jpg

**Implementation Notes:**
1. Celery task extracts 10 frames at 1s intervals
2. MediaPipe person detection on each frame
3. Store bounding boxes in detected_persons JSONB
4. Frontend renders thumbnails with person overlays
5. Selection stores bounding box for tracking

**Test Plan:**
- Unit: Bounding box calculation, person detection threshold
- Integration: Thumbnail extraction pipeline
- Runtime: Select subject in uploaded video
- Screenshots: Loading skeletons, thumbnail grid, selection highlight

**Definition of Done:**
- [ ] Thumbnails display after upload completes
- [ ] Tap on person highlights selection
- [ ] Confirmation stores bounding box
- [ ] Single person auto-selected with confirm prompt
- [ ] BDD scenarios pass with runtime evidence

---

### F004: Body Specification Input

**Intent:** Capture physical attributes to contextualize analysis for the user's body type.

**JTBD:** When I'm about to analyze my video, I want to enter my height and weight so the AI understands my reach and gives relevant feedback.

**Acceptance Criteria (BDD):**
- specs/bdd/body-specs.feature#User enters valid body specifications
- specs/bdd/body-specs.feature#Height below/above minimum/maximum shows validation error
- specs/bdd/body-specs.feature#Weight below/above minimum/maximum shows validation error
- specs/bdd/body-specs.feature#All fields required for submission
- specs/bdd/body-specs.feature#Body specs pre-filled for returning user
- specs/bdd/body-specs.feature#Invalid number format shows error

**UX Contract References:**
- UX_CONTRACT.md: Form validation inline, returning user pre-fill
- UI_STATES.md: Error (validation), Success (enabled submit)
- DESIGN_SYSTEM.md: Text input, dropdown/select, primary button

**API References:**
- POST /analysis/body-specs/{video_id}
- GET /auth/me (includes saved body_specs)

**Data Model References:**
- body_specs table (height_cm, weight_kg, experience_level, stance)
- users table (height_cm, weight_kg for pre-fill)

**Implementation Notes:**
1. Numeric inputs with increment/decrement buttons
2. Real-time inline validation
3. Persist to user profile for subsequent uploads
4. Experience level affects LLM prompt framing
5. Stance (orthodox/southpaw) affects metrics interpretation

**Test Plan:**
- Unit: Validation logic (ranges, required fields)
- Integration: Pre-fill from user profile, save to profile
- Runtime: Fill form with valid/invalid values
- Screenshots: Empty form, validation errors, complete form

**Definition of Done:**
- [ ] All fields validate correctly
- [ ] Submit enabled only when all fields valid
- [ ] Returning users see pre-filled values
- [ ] BDD scenarios pass with runtime evidence

---

### F005: Pose Estimation Processing

**Intent:** Extract skeletal coordinates from video for movement analysis.

**JTBD:** When I start analysis, I want the system to track my body movements frame by frame so it can identify my technique patterns.

**Acceptance Criteria (BDD):**
- specs/bdd/processing.feature#Pose estimation extracts joint coordinates
- specs/bdd/processing.feature#Subject tracking maintains across frames
- specs/bdd/processing.feature#Processing status shows step progress
- specs/bdd/processing.feature#Pose estimation fails with poor video quality
- specs/bdd/processing.feature#Processing takes longer than expected

**UX Contract References:**
- UX_CONTRACT.md: Progress visibility, processing under 5 minutes
- UI_STATES.md: Loading (progress steps), Error (failed with guidance)

**API References:**
- POST /analysis/start/{video_id}
- GET /processing/status/{analysis_id}
- WebSocket /ws/status/{analysis_id}

**Data Model References:**
- analyses table (status, current_stage, progress_percent)
- S3: pose_data/{analysis_id}/pose.json.gz

**Implementation Notes:**
1. Celery worker with MediaPipe pose landmarker
2. Track selected subject using initial bounding box
3. Extract 33 joints per frame (XYZ coordinates)
4. Store pose data as compressed JSON in S3
5. Update progress via Redis pub/sub
6. Fail if >20% frames have no pose detection

**Test Plan:**
- Unit: Joint coordinate extraction, tracking correlation
- Integration: Full pose pipeline with test video
- Runtime: Process real sparring video
- Evidence: Pose data JSON structure, status updates log

**Definition of Done:**
- [ ] 33 joints extracted per frame
- [ ] Subject tracked across video
- [ ] Progress updates via WebSocket
- [ ] Clear error message for unprocessable videos
- [ ] BDD scenarios pass with runtime evidence

---

### F006: Stamp Generation

**Intent:** Identify key moments (strikes, defensive actions) in the sparring session.

**JTBD:** When my video is analyzed, I want the system to mark the moments I threw punches or raised my guard so the report highlights my actual actions.

**Acceptance Criteria (BDD):**
- specs/bdd/processing.feature#Strike detection identifies punch types
- specs/bdd/processing.feature#Defensive action detection identifies guards
- specs/bdd/processing.feature#Stamps include confidence scores
- specs/bdd/processing.feature#No significant actions detected

**UX Contract References:**
- DESIGN_SYSTEM.md: Stamp timeline item component
- Boxing-specific colors: Strike (#E53935), Defense (#1976D2)

**API References:**
- Included in /processing/status response

**Data Model References:**
- stamps table (timestamp_seconds, action_type, side, confidence)

**Implementation Notes:**
1. Analyze arm joint velocity for strike detection
2. Analyze trajectory inflection points
3. Classify: jab, straight, hook, uppercut
4. Detect defensive: guard_up, guard_down, slip, duck
5. Store timestamp, action type, side (left/right), confidence
6. False positive rate target: under 10%

**Test Plan:**
- Unit: Velocity threshold, trajectory classification
- Integration: Stamp detection on pose data
- Runtime: Verify stamps match visible actions in video
- Evidence: Stamps JSON with timestamps

**Definition of Done:**
- [ ] Strikes classified by type
- [ ] Defensive actions detected
- [ ] Confidence scores attached
- [ ] Graceful handling when no actions detected
- [ ] BDD scenarios pass with runtime evidence

---

### F007: LLM Strategic Analysis

**Intent:** Generate national-team-level coaching feedback from pose data and stamps.

**JTBD:** When my video is processed, I want AI-generated strategic advice that tells me what I'm doing well and what specific drills I should practice.

**Acceptance Criteria (BDD):**
- specs/bdd/processing.feature#LLM generates strategic analysis
- specs/bdd/processing.feature#Analysis adapts to beginner experience level
- specs/bdd/processing.feature#Analysis adapts to competitive experience level
- specs/bdd/processing.feature#LLM API failure triggers retry
- specs/bdd/processing.feature#LLM API exhausts retries

**UX Contract References:**
- UX_CONTRACT.md: AI disclaimer required on every report

**API References:**
- Included in /processing/status response

**Data Model References:**
- reports table (strengths, weaknesses, recommendations, metrics JSONB)

**Implementation Notes:**
1. Format pose data and stamps as structured JSON
2. Calculate derived metrics:
   - Reach-to-distance maintenance ratio
   - Upper body tilt during punches
   - Guard recovery speed
   - Punch frequency
3. Build prompt with experience level context
4. Use GPT-4 with temperature 0.3 for consistency
5. Parse structured response (3-5 items per section)
6. Retry 3x with exponential backoff on failure
7. Include disclaimer in every report

**Test Plan:**
- Unit: Prompt formatting, response parsing, retry logic
- Integration: LLM call with test data
- Runtime: Generate analysis for real video
- Evidence: LLM response, metrics values

**Definition of Done:**
- [ ] Structured analysis generated
- [ ] Metrics calculated correctly
- [ ] Experience level affects advice tone
- [ ] Retry logic handles transient failures
- [ ] Disclaimer included
- [ ] BDD scenarios pass with runtime evidence

---

### F008: Report Display

**Intent:** Present analysis results in a readable, actionable format.

**JTBD:** When my analysis is complete, I want to see my strengths, weaknesses, and specific drills I should practice, with clear visualizations of my metrics.

**Acceptance Criteria (BDD):**
- specs/bdd/report.feature#Report displays summary section
- specs/bdd/report.feature#Report displays strengths section
- specs/bdd/report.feature#Report displays weaknesses section
- specs/bdd/report.feature#Report displays recommendations section
- specs/bdd/report.feature#Report displays key moments with timestamps
- specs/bdd/report.feature#Report displays metrics with visualizations
- specs/bdd/report.feature#Report includes AI disclaimer
- specs/bdd/report.feature#Report loads within performance target
- specs/bdd/report.feature#Report displays correctly on mobile viewport
- specs/bdd/report.feature#Report displays correctly on desktop viewport

**UX Contract References:**
- UX_CONTRACT.md: Report load under 1.5 seconds, responsive
- DESIGN_SYSTEM.md: Metric card, analysis section card, stamp timeline item

**API References:**
- GET /reports/{report_id}

**Data Model References:**
- reports table (performance_score, overall_assessment, strengths, weaknesses, recommendations, metrics)

**Implementation Notes:**
1. Server-side render for initial load
2. Summary section with performance score gauge
3. Strengths/weaknesses as collapsible cards
4. Recommendations with priority indicators
5. Metrics with Chart.js gauges/bars
6. Key moments section with stamp timeline
7. Responsive layout (single column mobile, two column desktop)

**Test Plan:**
- Unit: Component rendering, data transformation
- Integration: Full report page with test data
- Runtime: View generated report, measure load time
- Screenshots: Mobile 375px, desktop 1280px, all sections

**Definition of Done:**
- [ ] All sections render correctly
- [ ] Metrics visualized with charts
- [ ] Timestamps linked to stamps
- [ ] Page loads under 1.5 seconds
- [ ] Responsive on mobile and desktop
- [ ] Disclaimer visible
- [ ] BDD scenarios pass with runtime evidence

---

### F009: Report Sharing

**Intent:** Enable sharing analysis reports with coaches and the community.

**JTBD:** When I want feedback from my coach, I want to send them a link to my report without requiring them to sign up.

**Acceptance Criteria (BDD):**
- specs/bdd/sharing.feature#Report shows share button in private state
- specs/bdd/sharing.feature#User enables sharing and gets unique URL
- specs/bdd/sharing.feature#User copies share link to clipboard
- specs/bdd/sharing.feature#Shared report accessible without login
- specs/bdd/sharing.feature#User disables sharing
- specs/bdd/sharing.feature#Disabled share link returns error
- specs/bdd/sharing.feature#User re-enables sharing gets new URL
- specs/bdd/sharing.feature#Shared report displays social preview

**UX Contract References:**
- UX_CONTRACT.md: One-tap copy link, social preview cards
- DESIGN_SYSTEM.md: Toggle switch, snackbar/toast for confirmation

**API References:**
- GET /reports/{report_id}/share (get share status)
- POST /reports/{report_id}/share (enable sharing)
- DELETE /reports/{report_id}/share (disable sharing)

**Data Model References:**
- share_links table (share_hash, is_active, og_image_key)

**Implementation Notes:**
1. Share button shows current state (private/shared)
2. Enable generates 8-char hash (base62 UUID fragment)
3. Public route /share/{hash} renders report without auth
4. Generate OG image for social preview (report summary)
5. Disable invalidates link (returns 404)
6. Re-enable generates new hash

**Test Plan:**
- Unit: Hash generation, toggle logic
- Integration: Share flow, public access
- Runtime: Share link, access in incognito, verify social preview
- Screenshots: Private state, shared with URL, copied confirmation

**Definition of Done:**
- [ ] Share toggle works correctly
- [ ] Unique URL generated on enable
- [ ] Public access works without login
- [ ] Copy to clipboard with confirmation
- [ ] Social preview cards display correctly
- [ ] Disable invalidates link
- [ ] BDD scenarios pass with runtime evidence

---

### F010: Report History Dashboard

**Intent:** Enable users to track their improvement over time by viewing past reports.

**JTBD:** When I return to the app, I want to see all my past analyses so I can track my progress and revisit feedback.

**Acceptance Criteria (BDD):**
- specs/bdd/dashboard.feature#Dashboard displays report list sorted by date
- specs/bdd/dashboard.feature#Report list item shows thumbnail and summary
- specs/bdd/dashboard.feature#User navigates to report from list
- specs/bdd/dashboard.feature#User deletes report with confirmation
- specs/bdd/dashboard.feature#Dashboard shows empty state for new user
- specs/bdd/dashboard.feature#Dashboard loading state shows skeletons

**UX Contract References:**
- UX_CONTRACT.md: Under 2 second load, empty state with CTA
- UI_STATES.md: Loading (skeletons), Empty (upload CTA)
- DESIGN_SYSTEM.md: Elevated card, list item

**API References:**
- GET /reports/list
- DELETE /reports/{report_id}

**Data Model References:**
- reports table (user_id, created_at, deleted_at)

**Implementation Notes:**
1. List reports sorted by date descending
2. Show thumbnail, date, performance score indicator
3. Click navigates to full report
4. Delete shows confirmation dialog
5. Soft delete (set deleted_at)
6. Empty state shows "Upload your first video" CTA

**Test Plan:**
- Unit: List sorting, soft delete logic
- Integration: Dashboard with multiple reports
- Runtime: View dashboard, navigate, delete
- Screenshots: Loading skeletons, report list, empty state, delete dialog

**Definition of Done:**
- [ ] Reports listed by date
- [ ] Navigation to report works
- [ ] Delete with confirmation
- [ ] Empty state for new users
- [ ] Loading skeletons display
- [ ] BDD scenarios pass with runtime evidence

---

## Definition of Done (Global)

### Per-Feature DoD
- [ ] All acceptance criteria from features.json verified
- [ ] All BDD scenarios pass with runtime evidence
- [ ] Unit tests written (TDD: red/green/refactor)
- [ ] Integration tests pass
- [ ] UI states captured (loading/empty/error/success)
- [ ] Mobile (375px) and desktop (1280px) screenshots
- [ ] Code review completed
- [ ] No mock/stub code in production paths

### Release DoD
- [ ] All 10 features pass verification
- [ ] System E2E test: full user journey (upload to share)
- [ ] Performance: p95 processing under 5 minutes
- [ ] Performance: page loads under 2 seconds
- [ ] Security: OAuth tokens handled securely
- [ ] Accessibility: aXe audit with zero critical issues
- [ ] Korean localization complete
- [ ] Quality audit passes (rubric)
- [ ] HANDOFF.md published

---

## Risks and Mitigations

### R1: MediaPipe Accuracy Insufficient
**Likelihood:** Medium
**Impact:** High (core differentiator)
**Mitigation:**
- Test with 20+ real sparring videos before F005 complete
- Establish confidence threshold (95%+ joint detection for clear videos)
- Define "unprocessable video" criteria and clear user guidance
**Contingency:** If accuracy below threshold, evaluate pose estimation alternatives (e.g., OpenPose, custom model)

### R2: LLM Output Quality Inconsistent
**Likelihood:** Medium
**Impact:** High (user value)
**Mitigation:**
- Extensive prompt engineering with boxing domain expert review
- Temperature 0.3 for consistency
- Structured output format validation
- 10 sample analysis reviews before launch
**Contingency:** Add human review queue for edge cases

### R3: Video Processing Exceeds 5-Minute Target
**Likelihood:** Medium
**Impact:** Medium (UX expectation)
**Mitigation:**
- Profile each pipeline stage
- Optimize MediaPipe batch processing
- Scale workers based on queue depth
**Contingency:** GPU workers for faster inference

### R4: Upload Failures on Mobile Networks
**Likelihood:** Medium
**Impact:** Medium (competitor differentiation)
**Mitigation:**
- Implement resumable chunked upload from day 1
- Test on throttled connections (3G simulation)
- Client-side retry logic
**Contingency:** Reduce chunk size, add offline queue

### R5: OAuth Provider Downtime
**Likelihood:** Low
**Impact:** High (blocks all users)
**Mitigation:**
- Support both Kakao and Google
- Cache session tokens appropriately
- Clear error message when provider unavailable
**Contingency:** Implement email/password as backup auth (post-launch)

### R6: Rate Limit on LLM API
**Likelihood:** Medium
**Impact:** Medium (delays processing)
**Mitigation:**
- Implement exponential backoff with 3 retries
- Queue management for burst handling
- Monitor token usage
**Contingency:** Add LLM API quota alerts, consider self-hosted model

---

## Test Strategy

### Unit Testing
- **Framework:** pytest (backend), Jest (frontend)
- **Coverage target:** 80% for business logic
- **Focus areas:**
  - OAuth token validation
  - File validation (size, duration, format)
  - Pose data transformation
  - Stamp detection algorithms
  - LLM prompt formatting
  - Metrics calculation

### Integration Testing
- **Framework:** pytest with TestClient (FastAPI), Playwright (frontend)
- **Focus areas:**
  - OAuth callback flow
  - Chunked upload assembly
  - Processing pipeline (thumbnail to report)
  - API endpoint contracts

### End-to-End Testing
- **Framework:** Playwright
- **Critical journeys:**
  1. New user signup -> upload -> select subject -> body specs -> view report
  2. Return user -> dashboard -> view past report -> share
  3. Shared link viewer -> view report without login

### Performance Testing
- **Framework:** k6 or Locust
- **Targets:**
  - 50 concurrent uploads without degradation
  - 100 concurrent active users
  - p95 API response under 500ms
  - p95 processing under 5 minutes

### Visual Testing
- **Framework:** Playwright screenshots
- **Capture points:** All UI states per feature
- **Viewports:** 375px (mobile), 1280px (desktop)

### Accessibility Testing
- **Framework:** aXe-core via Playwright
- **Standard:** WCAG 2.1 AA
- **Focus:** Keyboard navigation, color contrast, labels

### Security Testing
- **OAuth token handling:** Ensure no leakage in logs/URL
- **Input validation:** Fuzz testing on file uploads
- **Authorization:** Verify users can only access own resources

---

## Execution Order

1. F001 - Authentication (foundation for all features)
2. F002 - Video Upload (enables content creation)
3. F003 - Subject Selection (depends on F002)
4. F004 - Body Specs (depends on F003 for flow)
5. F005 - Pose Estimation (depends on F003 for subject)
6. F006 - Stamp Generation (depends on F005)
7. F007 - LLM Analysis (depends on F006)
8. F008 - Report Display (depends on F007)
9. F009 - Report Sharing (depends on F008)
10. F010 - Dashboard (can parallel with F009)

---

## Per-Feature Loop Discipline

For each feature, follow this execution loop:

**Build (TDD)**
1. Write failing unit tests for acceptance criteria
2. Implement feature to pass tests
3. Write integration tests
4. Refactor

**Review**
1. Code review against DoD checklist
2. UX review against UX_CONTRACT
3. Security review for sensitive features (F001)

**Review-fix (TDD)**
1. Address review feedback
2. Add tests for edge cases found
3. Re-verify all tests pass

**Runtime test/debug**
1. Start application
2. Execute feature manually
3. Capture screenshots for all states
4. Record evidence (logs, metrics)

**System E2E/debug (if integration points)**
1. Test feature in context of full journey
2. Verify no regression on dependent features
3. Capture E2E evidence

---

## Rollout and Operational Readiness

### Pre-Launch Checklist
- [ ] All migrations applied to staging
- [ ] Environment variables configured (OAuth secrets, LLM API key)
- [ ] S3 buckets created with lifecycle rules
- [ ] Redis provisioned
- [ ] Monitoring dashboards created
- [ ] Alert thresholds configured
- [ ] Domain and SSL certificates ready

### Launch Sequence
1. Deploy backend API
2. Run database migrations
3. Deploy workers (scaled to 2 initially)
4. Deploy frontend
5. Smoke test all features
6. Enable traffic

### Post-Launch Monitoring
- **Metrics to watch:**
  - Error rate by endpoint
  - Processing queue depth
  - p95 processing latency
  - LLM API token consumption
  - Upload success rate
- **Alert triggers:**
  - Error rate > 1% for 5 minutes
  - Queue depth > 50 for 10 minutes
  - Processing p95 > 6 minutes

### Scaling Triggers
- API: CPU > 70% -> add instance (max 8)
- Workers: Queue > 20 -> add instance (max 16)
- Database: Connections > 80% -> add read replica
