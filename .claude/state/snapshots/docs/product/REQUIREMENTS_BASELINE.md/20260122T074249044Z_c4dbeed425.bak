# PunchAnalytics - Requirements Baseline

## Inputs
- docs/DOC_CONTRACT.md
- docs/product/PRD.md
- docs/product/MARKET_BENCHMARK.md
- User prompt (project context captured verbatim below)

---

## Raw input

**User requirement (verbatim):**

> PunchAnalytics is an AI-powered boxing sparring strategy analysis platform.
>
> **Key Features:**
> 1. **Pose Estimation -> XYZ coordinate extraction + stamp generation** to convert video data
> 2. **LLM Analyst** -> National team-level strategic feedback
> 3. **Sharing System** -> Report sharing via unique URL
>
> **User Journey:**
> 1. Sign up/Login: Simple SNS login (Kakao/Google)
> 2. Video Upload: 1-3 minute sparring video upload
> 3. Target Selection: Select analysis subject (self) from thumbnail + input body specs (height, weight, experience, style)
> 4. AI Analysis: XYZ coordinate extraction via Pose Estimation + stamps (key striking moments)
> 5. Report Generation: LLM analyst produces data-driven strengths/weaknesses/improvements
> 6. Share & Save: Share analysis report via unique URL to community or coach
>
> **Technical Stack Logic:**
> - Movement Tracking: MediaPipe (or similar) for 33 joint XYZ coordinates
> - Stamp Function: Auto-marking key moments (jab, straight, guard down) by detecting speed changes and trajectory inflection points
> - Data Formatting: Convert to JSON text logs for LLM consumption
>
> **Key Success Factor (KSF):**
> Providing LLM with difficult-to-measure metrics like:
> - Reach-to-distance maintenance ratio
> - Upper body tilt during punches (balance)
> - Guard recovery speed

---

## Interpretation

The user requires a consumer-facing web application that:
1. Authenticates users via OAuth (Kakao primary for Korean market, Google as secondary)
2. Accepts video uploads of boxing sparring sessions (1-3 minutes duration)
3. Allows users to identify themselves in multi-person footage via thumbnail selection
4. Collects physical attributes to contextualize analysis
5. Processes video through a pose estimation pipeline to extract skeletal data
6. Identifies key moments (strikes, defensive actions) via movement pattern detection
7. Feeds structured data to an LLM to generate strategic coaching feedback
8. Presents analysis in a readable report format
9. Enables sharing reports via unique, shareable URLs

The product targets amateur boxers in Korea seeking professional-grade coaching feedback without access to elite coaching staff.

---

## In scope

### Authentication (US-001)
- Kakao OAuth 2.0 login
- Google OAuth 2.0 login
- Session management with secure token handling
- Account creation with minimal required fields

### Video Upload (US-002)
- File upload supporting MP4, MOV, WebM formats
- Video duration validation (1-3 minutes)
- File size limit enforcement (configurable, target 500MB max)
- Upload progress indication
- Resumable upload support for mobile networks

### Subject Selection (US-003)
- Frame extraction for thumbnail generation
- Grid display of candidate frames
- User tap-to-select subject identification
- Visual confirmation of selected subject

### Body Specification Input (US-004)
- Height input (cm)
- Weight input (kg)
- Experience level selection (beginner/intermediate/advanced/competitive)
- Fighting style selection (orthodox/southpaw)

### Pose Estimation Processing (US-005)
- MediaPipe 33-joint coordinate extraction
- Frame-by-frame XYZ position data
- Processing status tracking
- Error handling for unprocessable videos

### Stamp Generation (US-006)
- Speed change detection algorithm
- Trajectory inflection point identification
- Strike type classification (jab, straight, hook, uppercut)
- Defensive action detection (guard up/down, slip, duck)
- Timestamp and frame number association

### LLM Analysis (US-007)
- JSON data formatting for LLM input
- Strategic analysis prompt execution
- Metrics extraction:
  - Reach-to-distance maintenance ratio
  - Upper body tilt during punches
  - Guard recovery speed
  - Punch frequency and rhythm patterns
  - Defensive positioning assessment
- Strengths/weaknesses/improvements output structure

### Report Generation (US-008)
- Structured report rendering (HTML/React)
- Metrics visualization (charts, indicators)
- Timestamp-linked key moments
- Actionable improvement recommendations
- Report persistence in database

### Report Sharing (US-009)
- Unique URL generation per report
- Public access to shared reports (no auth required)
- Optional sharing toggle (default private)
- Copy-to-clipboard functionality
- Social sharing meta tags (OG tags for Kakao, Twitter cards)

### Report History (US-010)
- List view of user's past reports
- Sort by date
- Quick access to view or share

---

## Out of scope

1. **Real-time analysis**: No live video streaming or in-session feedback
2. **Multi-person tracking**: User must manually select the analysis subject
3. **Opponent analysis**: Focus is on user's own technique, not opponent scouting
4. **Video editing**: No in-app trimming, cropping, or enhancement
5. **Wearable integration**: No support for external sensors or devices
6. **Payment processing**: No subscriptions, purchases, or monetization features
7. **Community features**: No public feeds, comments, or social interactions beyond sharing
8. **Coach accounts**: No differentiated coach role or annotation capabilities
9. **Multi-language**: Korean and English only; no additional localization
10. **Offline mode**: Requires internet connection for all features
11. **Native mobile apps**: Web-only (responsive); native iOS/Android apps are deferred

---

## Non-negotiables

1. **User data privacy**: Video files and analysis reports are private by default; sharing is explicit opt-in only
2. **Analysis accuracy disclaimer**: Reports must include clear disclaimers that AI analysis is not a substitute for professional coaching
3. **Processing reliability**: If pose estimation fails, the system must notify the user with actionable guidance (e.g., "Video quality too low; please re-upload with better lighting")
4. **No mock data in production**: All analysis must be generated from actual video processing and LLM inference; no simulated or hard-coded results
5. **Secure authentication**: OAuth tokens must be handled securely; no plain-text credential storage
6. **Graceful degradation**: System must handle LLM API failures without data loss; queued retries with user notification

---

## Quality bar

### Testing
- **Unit test coverage**: Minimum 80% coverage for business logic (pose processing, stamp detection, report generation)
- **Integration tests**: API endpoint tests for all user-facing routes
- **E2E tests**: Automated browser tests for critical user journeys (signup, upload, view report, share)
- **Performance tests**: Load testing for concurrent video uploads (target: 50 concurrent uploads without degradation)
- **Manual QA**: Domain expert review of 10 sample analyses before launch

### Security
- **Authentication**: OAuth 2.0 with Kakao and Google; PKCE flow for mobile web
- **Authorization**: Users can only access their own videos and reports; shared reports are read-only
- **Data protection**: Videos stored with encryption at rest (AES-256); HTTPS-only transport
- **Input validation**: Strict validation on all user inputs; file type verification via magic bytes
- **Rate limiting**: Upload endpoint limited to 5 uploads per user per hour; API rate limiting to prevent abuse

### Performance
- **Video upload**: Support files up to 500MB; chunked upload with resume capability
- **Processing latency**: p95 upload-to-report completion under 5 minutes for 3-minute videos
- **Page load**: Initial page load under 2 seconds (LCP); report page under 1.5 seconds
- **API response**: p95 under 500ms for non-processing endpoints
- **Concurrent users**: Support 100 concurrent active users without degradation

### UX
- **Design system**: Material Design 3 compliance for consistent, modern interface
- **Responsive design**: Functional on mobile (375px+) and desktop (1280px+) viewports
- **Loading states**: Skeleton loaders for async content; progress bars for uploads and processing
- **Error handling**: User-friendly error messages with actionable guidance; no raw error codes
- **Accessibility**: WCAG 2.1 AA compliance for core user flows
- **Korean localization**: All user-facing copy available in Korean; proper hangul rendering

---

## Assumptions

1. **User has access to sparring video**: Users can record their own sparring sessions or have someone record for them
2. **Video quality is sufficient**: Standard smartphone cameras (720p+) provide adequate resolution for pose estimation
3. **Single subject per analysis**: Users analyze themselves; multi-person analysis is not needed for MVP
4. **Internet connectivity**: Users have stable internet for upload (minimum 1 Mbps upload speed)
5. **MediaPipe accuracy**: MediaPipe pose estimation provides sufficient accuracy for boxing movement analysis without custom model training
6. **LLM capability**: Current LLM models (GPT-4 class) can generate meaningful boxing strategy feedback when provided structured pose data
7. **Korean market fit**: Kakao OAuth is the primary authentication method for Korean users
8. **Boxing terminology**: Users understand basic boxing terminology (jab, straight, hook, guard, etc.)
