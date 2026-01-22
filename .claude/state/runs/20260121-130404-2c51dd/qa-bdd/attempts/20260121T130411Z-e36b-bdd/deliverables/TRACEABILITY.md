# BDD Traceability Matrix

## Inputs
- docs/product/PRD.md
- docs/product/REQUIREMENTS_BASELINE.md
- docs/product/MARKET_BENCHMARK.md
- docs/product/STORY_MAP.md
- docs/ux/UX_CONTRACT.md
- docs/ux/DESIGN_SYSTEM.md
- docs/ux/UX_SPEC.md
- docs/ux/IA_MAP.md
- docs/ux/UI_STATES.md
- docs/ux/COPY.md

---

## Scope

This traceability matrix covers all **Launch (P0)** user stories as defined in `docs/product/STORY_MAP.md`:

| User Story | Feature | Priority | Status |
|------------|---------|----------|--------|
| US-001 | F001: User Authentication | P0 | Covered |
| US-002 | F002: Video Upload | P0 | Covered |
| US-003 | F003: Subject Selection | P0 | Covered |
| US-004 | F004: Body Specification Input | P0 | Covered |
| US-005 | F005: Pose Estimation Processing | P0 | Covered |
| US-006 | F006: Stamp Generation | P0 | Covered |
| US-007 | F007: LLM Strategic Analysis | P0 | Covered |
| US-008 | F008: Report Display | P0 | Covered |
| US-009 | F009: Report Sharing | P0 | Covered |
| US-010 | F010: Report History Dashboard | P0 | Covered |

---

## Traceability

```yaml
traceability:
  - user_story: US-001
    feature: F001
    gherkin_file: auth.feature
    scenarios:
      - "Successful Kakao OAuth login"
      - "Successful Google OAuth login"
      - "User logs out successfully"
      - "Unauthenticated user redirected to login"
      - "Session expiration prompts re-authentication"
      - "OAuth login cancelled by user"
      - "OAuth provider unavailable"

  - user_story: US-002
    feature: F002
    gherkin_file: upload.feature
    scenarios:
      - "Successful video upload with valid file"
      - "Upload shows progress indicator"
      - "File exceeds maximum size limit"
      - "Video duration too short"
      - "Video duration too long"
      - "Unsupported file format rejected"
      - "Upload resumes after network interruption"
      - "User cancels upload in progress"
      - "Upload area shows empty state initially"

  - user_story: US-003
    feature: F003
    gherkin_file: subject-selection.feature
    scenarios:
      - "Thumbnail grid displays extracted frames"
      - "User selects subject from thumbnail"
      - "User changes selection before confirmation"
      - "User confirms subject selection"
      - "Single person auto-selected"
      - "No subjects detected in video"
      - "Thumbnail extraction loading state"

  - user_story: US-004
    feature: F004
    gherkin_file: body-specs.feature
    scenarios:
      - "User enters valid body specifications"
      - "Height below minimum shows validation error"
      - "Height above maximum shows validation error"
      - "Weight below minimum shows validation error"
      - "Weight above maximum shows validation error"
      - "All fields required for submission"
      - "Body specs pre-filled for returning user"
      - "Invalid number format shows error"

  - user_story: US-005
    feature: F005
    gherkin_file: processing.feature
    scenarios:
      - "Pose estimation extracts joint coordinates"
      - "Subject tracking maintains across frames"
      - "Processing status shows step progress"
      - "Pose estimation fails with poor video quality"
      - "Processing takes longer than expected"

  - user_story: US-006
    feature: F006
    gherkin_file: processing.feature
    scenarios:
      - "Strike detection identifies punch types"
      - "Defensive action detection identifies guards"
      - "Stamps include confidence scores"
      - "No significant actions detected"

  - user_story: US-007
    feature: F007
    gherkin_file: processing.feature
    scenarios:
      - "LLM generates strategic analysis"
      - "Analysis adapts to beginner experience level"
      - "Analysis adapts to competitive experience level"
      - "LLM API failure triggers retry"
      - "LLM API exhausts retries"

  - user_story: US-008
    feature: F008
    gherkin_file: report.feature
    scenarios:
      - "Report displays summary section"
      - "Report displays strengths section"
      - "Report displays weaknesses section"
      - "Report displays recommendations section"
      - "Report displays key moments with timestamps"
      - "Report displays metrics with visualizations"
      - "Report includes AI disclaimer"
      - "Report loads within performance target"
      - "Report displays correctly on mobile viewport"
      - "Report displays correctly on desktop viewport"

  - user_story: US-009
    feature: F009
    gherkin_file: sharing.feature
    scenarios:
      - "Report shows share button in private state"
      - "User enables sharing and gets unique URL"
      - "User copies share link to clipboard"
      - "Shared report accessible without login"
      - "User disables sharing"
      - "Disabled share link returns error"
      - "User re-enables sharing gets new URL"
      - "Shared report displays social preview"

  - user_story: US-010
    feature: F010
    gherkin_file: dashboard.feature
    scenarios:
      - "Dashboard displays report list sorted by date"
      - "Report list item shows thumbnail and summary"
      - "User navigates to report from list"
      - "User deletes report with confirmation"
      - "Dashboard shows empty state for new user"
      - "Dashboard loading state shows skeletons"
```

---

## Coverage Summary

### Scenario Categories

| Category | Count | Purpose |
|----------|-------|---------|
| Happy Path | 27 | Core functionality working as expected |
| Validation Error | 9 | Input validation and user guidance |
| Error/Failure | 11 | System errors, network failures, service unavailability |
| Empty State | 4 | First-use and zero-data states |
| Loading State | 4 | Asynchronous operation feedback |
| Permission/Auth | 3 | Access control and session management |

### Total Scenarios by Feature

| Feature | Scenarios | UI | Backend |
|---------|-----------|----|---------|
| F001 Authentication | 7 | Yes | - |
| F002 Upload | 9 | Yes | - |
| F003 Subject Selection | 7 | Yes | - |
| F004 Body Specs | 8 | Yes | - |
| F005 Pose Estimation | 5 | - | Yes |
| F006 Stamp Generation | 4 | - | Yes |
| F007 LLM Analysis | 5 | - | Yes |
| F008 Report Display | 10 | Yes | - |
| F009 Sharing | 8 | Yes | - |
| F010 Dashboard | 6 | Yes | - |
| **Total** | **69** | **55** | **14** |

---

## UX Contract Coverage

### Non-Negotiables (from UX_CONTRACT.md)

| Requirement | Scenario Coverage |
|-------------|-------------------|
| Mobile-first responsive (375px+) | Report displays correctly on mobile viewport |
| Progress visibility | Upload shows progress indicator; Processing status shows step progress |
| Error recovery | All error scenarios include actionable guidance |
| Korean localization | Copy from COPY.md integrated in scenarios |
| WCAG 2.1 AA | Touch targets verified in mobile scenarios |
| Private by default | Report shows share button in private state |
| AI disclaimer | Report includes AI disclaimer |

### Quality Bar (from UX_CONTRACT.md)

| Criterion | Scenario Coverage |
|-----------|-------------------|
| Page load < 2s | Report loads within performance target |
| Report load < 1.5s | Report loads within performance target |
| Touch targets 48x48px | Report displays correctly on mobile viewport |
| Loading indicators | All loading state scenarios |
| Error messaging | All validation and error scenarios |

---

## PRD Requirements Coverage

### Launch Scope (from PRD.md)

All 10 user stories in the core user journey are covered:
1. OAuth login (US-001) - 7 scenarios
2. Video upload (US-002) - 9 scenarios
3. Subject selection (US-003) - 7 scenarios
4. Body specs input (US-004) - 8 scenarios
5. Pose estimation (US-005) - 5 scenarios
6. Stamp generation (US-006) - 4 scenarios
7. LLM analysis (US-007) - 5 scenarios
8. Report viewing (US-008) - 10 scenarios
9. Report sharing (US-009) - 8 scenarios
10. Report history (US-010) - 6 scenarios

### Quality Guardrails (from PRD.md)

| Guardrail | Scenario Coverage |
|-----------|-------------------|
| Upload-to-report < 5 min | Processing takes longer than expected |
| Pose estimation > 95% success | Pose estimation fails with poor video quality |
| LLM failure < 2% | LLM API failure triggers retry; LLM API exhausts retries |
| Report load < 2s | Report loads within performance target |

---

## Acceptance Criteria Mapping

All acceptance criteria from STORY_MAP.md are covered by scenarios:

- AC-001 to AC-005: auth.feature
- AC-006 to AC-012: upload.feature
- AC-013 to AC-017: subject-selection.feature
- AC-018 to AC-024: body-specs.feature
- AC-025 to AC-029: processing.feature (pose)
- AC-030 to AC-034: processing.feature (stamps)
- AC-035 to AC-040: processing.feature (LLM)
- AC-041 to AC-048: report.feature
- AC-049 to AC-055: sharing.feature
- AC-056 to AC-060: dashboard.feature
