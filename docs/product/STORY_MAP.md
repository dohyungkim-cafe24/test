# PunchAnalytics - Story Map

## Inputs
- docs/product/PRD.md
- docs/product/REQUIREMENTS_BASELINE.md
- docs/product/MARKET_BENCHMARK.md

---

## Vision

**Enable any boxer to receive national-team-level strategic feedback on their sparring sessions through AI-powered video analysis.**

PunchAnalytics transforms smartphone video into actionable coaching insights, democratizing access to expert-level fight analysis that was previously available only to elite athletes with dedicated coaching staff.

---

## Backbone

The user journey consists of six core activities:

```
[Authenticate] → [Upload Video] → [Configure Analysis] → [Process Video] → [Review Report] → [Share & Track]
```

### Activity 1: Authenticate
**User goal:** Quickly access the platform with minimal friction

### Activity 2: Upload Video
**User goal:** Submit sparring footage for analysis

### Activity 3: Configure Analysis
**User goal:** Identify myself in the video and provide context for accurate analysis

### Activity 4: Process Video
**User goal:** Understand that analysis is in progress and know when it will complete

### Activity 5: Review Report
**User goal:** Understand my strengths, weaknesses, and specific improvements to make

### Activity 6: Share & Track
**User goal:** Share insights with coach/community and track improvement over time

---

## Launch

The Launch scope delivers a complete, minimal user journey from signup through report sharing.

### P0 - Must Have (Launch blockers)

- US-001
- US-002
- US-003
- US-004
- US-005
- US-006
- US-007
- US-008
- US-009
- US-010

---

## US-001: User Authentication

**As a** boxer seeking analysis
**I want** to sign up and log in using my existing social accounts
**So that** I can quickly access the platform without creating new credentials

**Priority:** P0

**Acceptance Criteria:**
- AC-001: When user clicks "Login with Kakao," they are redirected to Kakao OAuth, and upon successful authentication, redirected back to the app with an active session
- AC-002: When user clicks "Login with Google," they are redirected to Google OAuth, and upon successful authentication, redirected back to the app with an active session
- AC-003: When user's OAuth token expires, they are prompted to re-authenticate without losing their session data
- AC-004: When user clicks "Logout," their session is terminated and they are redirected to the landing page
- AC-005: When an unauthenticated user attempts to access protected routes, they are redirected to the login page

**Notes:**
- Kakao OAuth is primary for Korean market; Google OAuth provides international coverage
- No email/password authentication in MVP

---

## US-002: Video Upload

**As a** boxer with sparring footage
**I want** to upload my video to the platform
**So that** I can receive AI analysis of my performance

**Priority:** P0

**Acceptance Criteria:**
- AC-006: When user selects a video file (MP4, MOV, or WebM) under 500MB and 1-3 minutes duration, the upload begins with a progress indicator
- AC-007: When upload completes successfully, user is navigated to the subject selection screen
- AC-008: When user selects a file exceeding 500MB, an error message displays: "Video file too large. Please upload a file under 500MB."
- AC-009: When user selects a video shorter than 1 minute or longer than 3 minutes, an error message displays: "Video must be between 1 and 3 minutes."
- AC-010: When user selects an unsupported file format, an error message displays: "Unsupported format. Please upload MP4, MOV, or WebM."
- AC-011: When network interruption occurs during upload, the upload resumes automatically when connection is restored
- AC-012: When user cancels upload, the partial upload is discarded and user remains on the upload screen

**Notes:**
- Chunked upload implementation required for resumability
- Client-side validation before upload initiation

---

## US-003: Subject Selection

**As a** user who uploaded a sparring video with multiple people
**I want** to identify which person is me in the video
**So that** the analysis focuses on my performance, not my sparring partner

**Priority:** P0

**Acceptance Criteria:**
- AC-013: When video upload completes, the system extracts thumbnail frames and displays a grid of candidate frames showing different people in the video
- AC-014: When user taps on a person in a thumbnail, that person is highlighted with a selection indicator
- AC-015: When user confirms selection, the selected subject's bounding box is stored for tracking throughout analysis
- AC-016: When user wants to change selection before confirmation, they can tap a different person to update the selection
- AC-017: When only one person is detected in the video, that person is auto-selected with option to confirm or re-upload

**Notes:**
- Frame extraction at 1-second intervals provides sufficient candidate variety
- Selection UI should show enlarged view on tap for confirmation

---

## US-004: Body Specification Input

**As a** user preparing my video for analysis
**I want** to input my physical attributes
**So that** the analysis can be contextualized to my body type and experience level

**Priority:** P0

**Acceptance Criteria:**
- AC-018: User can input height in centimeters (numeric input, 100-250cm range)
- AC-019: User can input weight in kilograms (numeric input, 30-200kg range)
- AC-020: User can select experience level from: Beginner (0-1 year), Intermediate (1-3 years), Advanced (3-5 years), Competitive (5+ years)
- AC-021: User can select fighting stance: Orthodox or Southpaw
- AC-022: When all required fields are completed, the "Start Analysis" button becomes enabled
- AC-023: When user submits with invalid numeric values, inline validation errors display immediately
- AC-024: User's body specs are persisted and pre-filled for subsequent uploads

**Notes:**
- Metric units only for MVP (Korean market standard)
- Experience level influences LLM analysis framing

---

## US-005: Pose Estimation Processing

**As a** system processing uploaded video
**I want** to extract skeletal coordinates from each frame
**So that** movement patterns can be analyzed for strategic feedback

**Priority:** P0

**Acceptance Criteria:**
- AC-025: System processes video frames and extracts 33-joint XYZ coordinates using MediaPipe
- AC-026: System tracks the selected subject across frames using bounding box correlation
- AC-027: When pose estimation succeeds, coordinate data is stored in structured JSON format
- AC-028: When pose estimation fails for more than 20% of frames, analysis is marked as failed with error: "Unable to track subject clearly. Please upload video with better lighting or camera angle."
- AC-029: Processing progress is logged and retrievable via status endpoint

**Notes:**
- Background job processing with status polling
- Partial frame failures acceptable if under threshold

---

## US-006: Stamp Generation

**As a** system analyzing pose data
**I want** to identify key moments in the sparring session
**So that** the analysis highlights significant actions like punches and defensive movements

**Priority:** P0

**Acceptance Criteria:**
- AC-030: System detects strikes (jab, straight, hook, uppercut) by analyzing arm velocity and trajectory patterns
- AC-031: System detects defensive actions (guard up, guard down, slip, duck) by analyzing torso and arm positioning
- AC-032: Each detected action is timestamped with frame number and confidence score
- AC-033: Stamps are stored with action type, timestamp, body side (left/right), and confidence
- AC-034: When no significant actions are detected, analysis proceeds with generic movement feedback

**Notes:**
- Velocity threshold and trajectory algorithms require domain expert tuning
- False positive rate target: under 10%

---

## US-007: LLM Strategic Analysis

**As a** system with pose data and stamps
**I want** to generate strategic coaching feedback via LLM
**So that** users receive national-team-level insights on their performance

**Priority:** P0

**Acceptance Criteria:**
- AC-035: System formats pose data and stamps into structured JSON for LLM consumption
- AC-036: System calculates derived metrics: reach-to-distance ratio, upper body tilt during punches, guard recovery speed, punch frequency
- AC-037: LLM generates analysis containing: 3-5 strengths, 3-5 weaknesses, 3-5 specific improvement recommendations
- AC-038: Analysis output is specific to user's experience level (beginner advice vs advanced refinement)
- AC-039: When LLM API fails, system retries 3 times with exponential backoff; on final failure, user is notified with option to retry manually
- AC-040: Analysis includes disclaimer: "This AI analysis is for training purposes only and is not a substitute for professional coaching."

**Notes:**
- Prompt engineering critical for quality output
- Temperature setting low (0.3) for consistent analysis

---

## US-008: Report Generation

**As a** user whose video has been analyzed
**I want** to view my analysis in a readable report format
**So that** I can understand and act on the feedback

**Priority:** P0

**Acceptance Criteria:**
- AC-041: Report displays summary section with overall performance assessment
- AC-042: Report displays strengths section with 3-5 specific positive observations
- AC-043: Report displays weaknesses section with 3-5 specific areas for improvement
- AC-044: Report displays recommendations section with 3-5 actionable drills or focus areas
- AC-045: Report displays key moments section with timestamps linked to specific stamps
- AC-046: Report displays calculated metrics with visual indicators (charts or gauges)
- AC-047: Report page loads within 1.5 seconds
- AC-048: Report renders correctly on mobile (375px) and desktop (1280px) viewports

**Notes:**
- Timestamp links are informational (no video playback in MVP)
- Charts use simple visualization library (Chart.js or similar)

---

## US-009: Report Sharing

**As a** user with a completed analysis report
**I want** to share my report with my coach or training community
**So that** I can get feedback and discuss improvements

**Priority:** P0

**Acceptance Criteria:**
- AC-049: Report page displays "Share" button (default state: private/not shared)
- AC-050: When user clicks "Share," a unique URL is generated and displayed
- AC-051: Shared URL is accessible without authentication (public read-only)
- AC-052: "Copy Link" button copies URL to clipboard with confirmation toast
- AC-053: Shared report displays social preview cards (Open Graph) when pasted in Kakao, Twitter, or other platforms
- AC-054: User can disable sharing, which invalidates the shared URL
- AC-055: User can re-enable sharing, which generates a new unique URL

**Notes:**
- Shared URLs use short hash (8 characters) for cleaner sharing
- No expiration on shared links in MVP

---

## US-010: Report History

**As a** returning user
**I want** to view my past analysis reports
**So that** I can track my improvement over time and revisit feedback

**Priority:** P0

**Acceptance Criteria:**
- AC-056: Dashboard displays list of user's past reports sorted by date (newest first)
- AC-057: Each list item shows: video thumbnail, analysis date, overall score/summary indicator
- AC-058: Clicking a list item navigates to the full report
- AC-059: User can delete a report from the list (with confirmation dialog)
- AC-060: When user has no reports, empty state displays with CTA to upload first video

**Notes:**
- No pagination needed for MVP (assume under 100 reports per user)
- Deletion is soft-delete for data recovery purposes

---

## P1 - Should Have (Post-launch)

### US-011: Video Overlay Visualization

**As a** user viewing my report
**I want** to see my pose skeleton overlaid on the video
**So that** I can visually understand the analysis points

**Priority:** P1

**Acceptance Criteria:**
- AC-061: Report includes video player with pose skeleton overlay option
- AC-062: Skeleton overlay toggles on/off
- AC-063: Stamps are highlighted on the timeline for easy navigation

---

### US-012: Progress Comparison

**As a** returning user with multiple analyses
**I want** to compare my reports over time
**So that** I can see measurable improvement in specific metrics

**Priority:** P1

**Acceptance Criteria:**
- AC-064: User can select two reports to compare side-by-side
- AC-065: Comparison view shows metric changes (improved/declined/unchanged)
- AC-066: Trend charts display progression across multiple reports

---

### US-013: Coach Annotations

**As a** coach viewing a shared report
**I want** to add comments and annotations
**So that** I can provide additional guidance to my athlete

**Priority:** P1

**Acceptance Criteria:**
- AC-067: Shared reports display "Add Comment" option (requires coach authentication)
- AC-068: Comments are timestamped and attributed to coach
- AC-069: Report owner is notified when new comments are added

---

### US-014: Processing Notifications

**As a** user who submitted a video for analysis
**I want** to receive a notification when processing completes
**So that** I don't have to keep checking the app

**Priority:** P1

**Acceptance Criteria:**
- AC-070: User can opt-in to browser push notifications
- AC-071: Notification is sent when report is ready with link to view
- AC-072: Notification is sent if processing fails with error details

---

## P2 - Nice to Have (Future)

### US-015: Multi-Person Tracking

**As a** user with complex sparring footage
**I want** the system to automatically identify and track multiple people
**So that** I don't have to manually select my subject

**Priority:** P2

---

### US-016: Opponent Analysis

**As a** competitive boxer
**I want** analysis of my opponent's patterns in the same video
**So that** I can prepare counter-strategies

**Priority:** P2

---

### US-017: Community Feed

**As a** user who wants to learn from others
**I want** to browse publicly shared reports from the community
**So that** I can see different styles and common feedback

**Priority:** P2

---

### US-018: Subscription Tiers

**As a** business operator
**I want** to offer premium analysis features for paying users
**So that** the platform can generate revenue

**Priority:** P2

---

### US-019: Additional Combat Sports

**As a** martial artist practicing MMA, Muay Thai, or Taekwondo
**I want** analysis tailored to my sport
**So that** I receive relevant feedback beyond boxing

**Priority:** P2
