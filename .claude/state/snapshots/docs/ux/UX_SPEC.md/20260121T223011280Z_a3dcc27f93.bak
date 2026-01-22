# PunchAnalytics UX Specification

## Inputs
- docs/product/PRD.md
- docs/product/REQUIREMENTS_BASELINE.md
- docs/product/MARKET_BENCHMARK.md
- docs/product/STORY_MAP.md
- docs/ux/UX_CONTRACT.md
- docs/ux/DESIGN_SYSTEM.md

---

## Scope

### Launch Scope (P0)
This specification covers the complete user experience for all P0 user stories:
- US-001: User Authentication (Kakao/Google OAuth)
- US-002: Video Upload (file selection, validation, progress)
- US-003: Subject Selection (thumbnail grid, tap-to-select)
- US-004: Body Specification Input (height, weight, experience, stance)
- US-005: Pose Estimation Processing (status tracking)
- US-006: Stamp Generation (key moment detection)
- US-007: LLM Strategic Analysis (feedback generation)
- US-008: Report Generation (metrics visualization)
- US-009: Report Sharing (unique URL, copy link)
- US-010: Report History (dashboard, navigation)

### Non-Scope
- Real-time analysis features
- Video playback with overlay
- Coach annotation system
- Progress comparison between reports
- Push notifications
- Payment/subscription flows

---

## Entry points

### 1. Landing Page (Unauthenticated)
| Property | Value |
|----------|-------|
| URL | `/` |
| Access | Public |
| Purpose | Introduction and login CTA |
| Primary Action | "Get Started" / "시작하기" leading to login |

### 2. Direct Report Link (Public Shared)
| Property | Value |
|----------|-------|
| URL | `/report/{share_hash}` |
| Access | Public (if sharing enabled) |
| Purpose | View shared report without authentication |
| Behavior | Read-only view; no edit/delete options |

### 3. OAuth Callback
| Property | Value |
|----------|-------|
| URL | `/auth/callback/{provider}` |
| Access | System-managed |
| Purpose | Handle OAuth redirect |
| Behavior | Process token, redirect to dashboard or original destination |

### 4. Deep Link to Report
| Property | Value |
|----------|-------|
| URL | `/dashboard/report/{report_id}` |
| Access | Authenticated owner only |
| Purpose | Direct navigation to owned report |
| Behavior | Require auth; show full report with edit/share options |

---

## Primary flows

### Flow 1: First-Time User Journey (US-001 through US-008)

```
Landing Page
    |
    v
[Get Started] --> Login Options
    |               |
    |    +----------+----------+
    |    |                     |
    v    v                     v
[Kakao OAuth]           [Google OAuth]
    |                          |
    +----------+---------------+
               |
               v
        OAuth Provider
               |
               v
        Callback Handler
               |
               v
         Dashboard (empty state)
               |
               v
        [Upload Video]
               |
               v
         Upload Screen
               |
    +----------+----------+
    |                     |
    v                     v
File Selection     Drag & Drop
    |                     |
    +----------+----------+
               |
               v
         Validation
               |
    +----------+----------+
    |                     |
    v                     v
 Pass                   Fail
    |                     |
    v                     v
Upload Progress      Error Message
    |                     |
    v                     |
Upload Complete          |
    |                     |
    v                     |
Subject Selection <------+
    |
    v
Thumbnail Grid
    |
    v
[Tap Subject]
    |
    v
Selection Confirmed
    |
    v
Body Spec Form
    |
    v
[Start Analysis]
    |
    v
Processing Status
    |
    v
Analysis Complete
    |
    v
Report View
```

#### Step Details

| Step | Screen | User Action | System Response | Duration |
|------|--------|-------------|-----------------|----------|
| 1 | Landing | Tap "Get Started" | Show login options | Instant |
| 2 | Login | Tap provider button | Redirect to OAuth | Instant |
| 3 | OAuth | Complete login | Redirect to app | 2-10s |
| 4 | Dashboard | View empty state | Show upload CTA | Instant |
| 5 | Upload | Select file | Validate file | 1-3s |
| 6 | Upload | Watch progress | Update progress bar | 30s-3min |
| 7 | Subject | Tap on self | Highlight selection | Instant |
| 8 | Subject | Tap "Confirm" | Navigate to form | Instant |
| 9 | Body Spec | Fill form | Inline validation | Real-time |
| 10 | Body Spec | Tap "Start Analysis" | Begin processing | Instant |
| 11 | Processing | Wait | Poll status every 5s | 2-5min |
| 12 | Complete | Tap "View Report" | Navigate to report | Instant |

### Flow 2: Returning User Upload (US-002 through US-008)

```
Dashboard (with history)
    |
    v
[Upload New Video]
    |
    v
Upload Screen
    |
    v
(Same as Flow 1 from step 5)
    |
    v
Body Spec Form (pre-filled from last upload)
    |
    v
(Continue to report)
```

#### Optimizations for Returning Users
- Body specs pre-filled from previous upload
- Skip tutorial hints
- Faster form completion expected (under 30 seconds)

### Flow 3: Report Sharing (US-009)

```
Report View
    |
    v
[Share Button]
    |
    v
Share Dialog
    |
    +----------+----------+
    |                     |
    v                     v
First Share          Previously Shared
    |                     |
    v                     v
Generate URL         Show Existing URL
    |                     |
    +----------+----------+
               |
               v
        [Copy Link]
               |
               v
         Toast: "Link copied"
```

#### Share Toggle States
| State | Action Available | URL Status |
|-------|------------------|------------|
| Private (default) | Enable sharing | No URL |
| Shared | Copy link, Disable sharing | URL active |
| Disabled after sharing | Re-enable sharing | Previous URL invalidated |

### Flow 4: Report History Navigation (US-010)

```
Dashboard
    |
    v
Report List (sorted by date)
    |
    +----------+----------+
    |                     |
    v                     v
[Tap Report]       [Delete Report]
    |                     |
    v                     v
Report View        Confirmation Dialog
                          |
                   +------+------+
                   |             |
                   v             v
                Cancel        Confirm
                   |             |
                   v             v
              (no change)   Delete & Toast
```

### Flow 5: Logout (US-001)

```
Any Authenticated Screen
    |
    v
[Profile Menu] --> [Logout]
    |
    v
Confirmation Dialog (optional)
    |
    v
Session Cleared
    |
    v
Redirect to Landing
```

---

## Edge cases

### Upload Edge Cases

| Scenario | Behavior |
|----------|----------|
| Network disconnects during upload | Pause upload; show "Connection lost" with resume option when reconnected |
| User cancels upload at 90% | Confirm cancellation; discard partial upload |
| File passes validation but server rejects | Show server error message; allow retry |
| Multiple rapid file selections | Cancel previous, start new upload |
| Browser tab closed during upload | Upload stops; partial data cleaned up server-side |

### Processing Edge Cases

| Scenario | Behavior |
|----------|----------|
| User navigates away during processing | Processing continues; notification available on return |
| Processing exceeds 5 minutes | Show "Taking longer than expected" message; continue polling |
| Pose estimation fails on partial frames | Continue if under 20% failure; fail if over |
| LLM API unavailable | Retry 3 times with exponential backoff; show manual retry option |
| Server restart during processing | Job resumes from checkpoint; no user action needed |

### Authentication Edge Cases

| Scenario | Behavior |
|----------|----------|
| OAuth denied by user | Return to login screen with "Login cancelled" message |
| OAuth token expires during session | Show session expired dialog; re-authenticate preserving context |
| User logs in on different device | New session; no session conflict handling needed (stateless) |
| OAuth provider unavailable | Show provider-specific error; suggest alternative provider |

### Report Edge Cases

| Scenario | Behavior |
|----------|----------|
| Shared link accessed after owner deletes report | 404 page: "Report not found" |
| Shared link accessed after owner disables sharing | 403 page: "Sharing disabled" |
| Owner views shared link of own report | Full owner view (with edit/delete options) |
| Very long report content | Lazy load sections; collapsible cards |

### Form Edge Cases

| Scenario | Behavior |
|----------|----------|
| User enters height with units (e.g., "175cm") | Strip non-numeric; accept 175 |
| User uses decimal for height | Accept decimal; round to nearest cm |
| User pastes invalid data | Validate and show error immediately |
| Back button from body spec form | Confirm abandonment; video stays uploaded |

---

## Screens & routes

### Route Table

| Route | Screen | Auth Required | SEO |
|-------|--------|---------------|-----|
| `/` | Landing Page | No | Yes |
| `/login` | Login Options | No | No |
| `/auth/callback/kakao` | OAuth Callback | No | No |
| `/auth/callback/google` | OAuth Callback | No | No |
| `/dashboard` | Report Dashboard | Yes | No |
| `/upload` | Video Upload | Yes | No |
| `/upload/{upload_id}/select` | Subject Selection | Yes | No |
| `/upload/{upload_id}/specs` | Body Specification | Yes | No |
| `/upload/{upload_id}/processing` | Processing Status | Yes | No |
| `/dashboard/report/{report_id}` | Report View (Owner) | Yes | No |
| `/report/{share_hash}` | Report View (Public) | No | Yes |
| `/404` | Not Found | No | No |
| `/error` | Error Page | No | No |

### Screen Specifications

#### Landing Page (`/`)
| Element | Specification |
|---------|---------------|
| Hero Section | Product value proposition, hero image/animation |
| CTA | "Get Started" / "시작하기" primary button |
| Features | 3 key benefits with icons |
| Footer | Links to privacy policy, terms |

#### Login Options (`/login`)
| Element | Specification |
|---------|---------------|
| Headline | "Welcome to PunchAnalytics" / "PunchAnalytics에 오신 것을 환영합니다" |
| Kakao Button | Yellow (#FEE500), Kakao logo, "Login with Kakao" / "카카오로 로그인" |
| Google Button | White with outline, Google logo, "Login with Google" / "Google로 로그인" |
| Divider | "or" / "또는" between options |
| Legal | Privacy policy link, terms link |

#### Dashboard (`/dashboard`)
| Element | Specification |
|---------|---------------|
| App Bar | Logo, profile menu (avatar, logout) |
| FAB | "Upload Video" floating action button (mobile) |
| Primary Button | "Upload Video" (desktop) |
| Report List | Cards with thumbnail, date, summary indicator |
| Empty State | Illustration + "No reports yet" + upload CTA |

#### Upload Screen (`/upload`)
| Element | Specification |
|---------|---------------|
| Drop Zone | Dashed border area, icon, "Drop video here or tap to browse" |
| File Input | Hidden, triggered by drop zone |
| Guidelines | Format, size, duration requirements |
| Progress Card | Appears after file selection |
| Cancel Button | Available during upload |

#### Subject Selection (`/upload/{id}/select`)
| Element | Specification |
|---------|---------------|
| Instruction | "Tap on yourself in the video" / "영상에서 자신을 선택하세요" |
| Thumbnail Grid | 6-9 frames, 2-3 columns |
| Selected Indicator | Blue ring + checkmark overlay |
| Enlarged Preview | Modal or inline enlarged view of selection |
| Confirm Button | "Confirm Selection" / "선택 확인", enabled after selection |

#### Body Specification (`/upload/{id}/specs`)
| Element | Specification |
|---------|---------------|
| Form Title | "Your Profile" / "프로필 입력" |
| Height Field | Numeric input, suffix "cm", range 100-250 |
| Weight Field | Numeric input, suffix "kg", range 30-200 |
| Experience Select | Dropdown: Beginner/Intermediate/Advanced/Competitive |
| Stance Select | Segmented button: Orthodox / Southpaw |
| Submit Button | "Start Analysis" / "분석 시작" |

#### Processing Status (`/upload/{id}/processing`)
| Element | Specification |
|---------|---------------|
| Video Thumbnail | Static thumbnail of uploaded video |
| Status Indicator | Circular progress + step label |
| Step Progress | "Step 1/3: Analyzing movements..." |
| Time Estimate | "Estimated time: 3 minutes" |
| Elapsed Time | "Started: 2 minutes ago" |

#### Report View (`/dashboard/report/{id}` or `/report/{hash}`)
| Element | Specification |
|---------|---------------|
| Header | Title, date, video thumbnail |
| Summary Card | Overall assessment paragraph |
| Metrics Grid | 4 metric cards (reach ratio, guard speed, tilt, frequency) |
| Strengths Section | Expandable card, 3-5 bullet points |
| Weaknesses Section | Expandable card, 3-5 bullet points |
| Recommendations | Expandable card, 3-5 actionable items |
| Key Moments | Horizontal scroll of timestamp cards |
| Disclaimer | AI disclaimer text at bottom |
| Share Button | Owner only; opens share dialog |
| Delete Button | Owner only; confirms deletion |

---

## Components

### Custom Components (Beyond M3 Baseline)

#### Video Drop Zone
| Property | Value |
|----------|-------|
| Height | 200px (mobile), 300px (desktop) |
| Border | 2px dashed `colors.outline`, 12px radius |
| Icon | `cloud_upload`, 48px |
| Hover State | Border solid, background 4% primary |
| Active State | Border primary, background 8% primary |

#### Subject Thumbnail
| Property | Value |
|----------|-------|
| Size | 100px x 100px (mobile), 150px x 150px (desktop) |
| Border Radius | 8px |
| Selection Ring | 3px solid primary, 4px offset |
| Checkmark | 24px badge, top-right corner |

#### Metric Card
| Property | Value |
|----------|-------|
| Layout | Value top (Display Small), label bottom (Body Small) |
| Left Border | 4px, color based on positive/negative |
| Padding | 16px |
| Background | Surface variant |

#### Timestamp Card
| Property | Value |
|----------|-------|
| Layout | Thumbnail left, text right |
| Thumbnail | 64px x 64px |
| Title | Action type (Title Small) |
| Subtitle | Timestamp "0:34" (Body Small) |
| Height | 80px |

#### Processing Step Indicator
| Property | Value |
|----------|-------|
| Layout | Vertical stepper |
| Active Step | Primary color, filled circle |
| Completed Step | Primary color, checkmark |
| Pending Step | Outline variant, empty circle |
| Connector | 2px line, outline variant (completed: primary) |

### Component States Reference

All components follow the state specifications in UI_STATES.md:
- Loading: Skeleton variants defined
- Empty: Empty state messaging defined
- Error: Inline and page-level error variants
- Validation: Form field error states
- Success: Confirmation feedback

---

## UI states

Reference: `docs/ux/UI_STATES.md`

### State Summary by Screen

| Screen | Loading | Empty | Error | Validation | Success |
|--------|---------|-------|-------|------------|---------|
| Landing | Page skeleton | N/A | Server error | N/A | N/A |
| Login | OAuth redirect spinner | N/A | OAuth error | N/A | Redirect |
| Dashboard | List skeleton | No reports | Load error | N/A | N/A |
| Upload | Upload progress | N/A | File/network error | File validation | Upload complete |
| Subject Select | Thumbnail skeleton | No subjects | Extraction error | N/A | Selection confirmed |
| Body Spec | N/A | N/A | Submit error | Field validation | Analysis started |
| Processing | Progress indicator | N/A | Analysis error | N/A | Complete |
| Report | Section skeletons | N/A | Load error | N/A | N/A |

---

## Instrumentation

### Event Taxonomy

| Event Name | Parameters | Trigger |
|------------|------------|---------|
| `page_view` | `page_name`, `route` | Route change |
| `login_start` | `provider` | OAuth button tap |
| `login_complete` | `provider`, `is_new_user` | OAuth callback success |
| `login_error` | `provider`, `error_type` | OAuth callback failure |
| `logout` | - | Logout action |
| `upload_start` | `file_size`, `file_type`, `duration` | File selected |
| `upload_progress` | `percent`, `bytes_uploaded` | Every 10% milestone |
| `upload_complete` | `upload_id`, `duration_seconds` | Upload success |
| `upload_error` | `error_type`, `file_size` | Upload failure |
| `upload_cancel` | `percent_complete` | User cancellation |
| `subject_select` | `thumbnail_index` | Subject tapped |
| `subject_confirm` | `upload_id` | Selection confirmed |
| `specs_submit` | `height`, `weight`, `experience`, `stance` | Form submitted |
| `processing_start` | `upload_id` | Analysis begins |
| `processing_complete` | `upload_id`, `duration_seconds` | Analysis success |
| `processing_error` | `upload_id`, `error_type`, `step` | Analysis failure |
| `report_view` | `report_id`, `is_owner`, `source` | Report loaded |
| `report_share_enable` | `report_id` | Sharing enabled |
| `report_share_copy` | `report_id` | Link copied |
| `report_share_disable` | `report_id` | Sharing disabled |
| `report_delete` | `report_id` | Report deleted |

### Conversion Funnels

#### Primary Funnel: Upload to Report
1. `upload_start`
2. `upload_complete`
3. `subject_confirm`
4. `specs_submit`
5. `processing_complete`
6. `report_view`

#### Share Funnel
1. `report_view` (is_owner=true)
2. `report_share_enable`
3. `report_share_copy`

---

## Validation plan

### Automated Tests

| Test Type | Coverage | Tool |
|-----------|----------|------|
| Unit Tests | Component rendering, state logic | Jest + Testing Library |
| Integration Tests | User flows, API integration | Cypress |
| Visual Regression | Screenshot comparison | Percy or Chromatic |
| Accessibility | aXe audit | cypress-axe |
| Performance | Lighthouse CI | Lighthouse |

### Manual QA Checklist

#### Mobile Testing (375px iPhone SE)
- [ ] Landing page renders correctly
- [ ] Login buttons are tap-accessible
- [ ] File picker opens from drop zone tap
- [ ] Upload progress visible during upload
- [ ] Thumbnail grid scrollable
- [ ] Subject selection tap target sufficient
- [ ] Form fields accessible with keyboard
- [ ] Report sections collapsible
- [ ] Share dialog functional

#### Desktop Testing (1280px)
- [ ] Landing page hero section properly sized
- [ ] Drag and drop functional in upload
- [ ] Thumbnail grid shows more columns
- [ ] Report layout optimized for wider screen
- [ ] Keyboard navigation complete

#### Cross-Browser
- [ ] Chrome (latest)
- [ ] Safari (latest)
- [ ] Firefox (latest)
- [ ] Samsung Internet (mobile)
- [ ] Kakao In-App Browser

#### Accessibility
- [ ] Keyboard-only navigation complete flow
- [ ] Screen reader announces all states
- [ ] Color contrast passes AA
- [ ] Focus indicators visible
- [ ] Error messages announced

### Evidence Collection

| Evidence Type | Location | Naming Convention |
|---------------|----------|-------------------|
| Journey Screenshots | `evidence/ux/journeys/` | `{US-ID}_{step}_{viewport}.png` |
| State Screenshots | `evidence/ux/states/` | `{screen}_{state}_{viewport}.png` |
| Accessibility Report | `evidence/ux/a11y/` | `axe_report_{date}.json` |
| Performance Report | `evidence/ux/perf/` | `lighthouse_{page}_{date}.json` |

---

## Open questions

### Resolved Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| Support video trimming in-app? | No | Out of scope for MVP; reduces complexity |
| Maximum video duration? | 3 minutes | Balances processing cost and user need |
| Maximum file size? | 500MB | Supports HD video for 3 minutes |
| Email verification required? | No | Reduce friction; OAuth provides verified email |

### Deferred to Post-Launch

| Question | Deferral Reason | Impact |
|----------|-----------------|--------|
| Should we add video preview before upload confirmation? | Adds complexity; not critical for MVP | Minor UX improvement |
| Should processing notification be push or in-app? | Push notifications require additional infrastructure | Users must check app for status |
| Should we show pose skeleton overlay on report? | P1 feature (US-011) | Report shows text-only analysis |
| Should we support batch uploads? | Low priority; single video flow sufficient | Users upload one at a time |
