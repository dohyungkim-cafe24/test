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
{
  "traceability": [
    {
      "user_story": "US-001",
      "feature": "F001",
      "gherkin_file": "specs/bdd/auth.feature",
      "scenarios": [
        "OAuth login cancelled by user",
        "OAuth provider unavailable",
        "Session expiration prompts re-authentication",
        "Successful Google OAuth login",
        "Successful Kakao OAuth login",
        "Unauthenticated user redirected to login",
        "User logs out successfully"
      ]
    },
    {
      "user_story": "US-002",
      "feature": "F002",
      "gherkin_file": "specs/bdd/upload.feature",
      "scenarios": [
        "File exceeds maximum size limit",
        "Successful video upload with valid file",
        "Unsupported file format rejected",
        "Upload area shows empty state initially",
        "Upload resumes after network interruption",
        "Upload shows progress indicator",
        "User cancels upload in progress",
        "Video duration too long",
        "Video duration too short"
      ]
    },
    {
      "user_story": "US-003",
      "feature": "F003",
      "gherkin_file": "specs/bdd/subject-selection.feature",
      "scenarios": [
        "No subjects detected in video",
        "Single person auto-selected",
        "Thumbnail extraction loading state",
        "Thumbnail grid displays extracted frames",
        "User changes selection before confirmation",
        "User confirms subject selection",
        "User selects subject from thumbnail"
      ]
    },
    {
      "user_story": "US-004",
      "feature": "F004",
      "gherkin_file": "specs/bdd/body-specs.feature",
      "scenarios": [
        "All fields required for submission",
        "Body specs pre-filled for returning user",
        "Height above maximum shows validation error",
        "Height below minimum shows validation error",
        "Invalid number format shows error",
        "User enters valid body specifications",
        "Weight above maximum shows validation error",
        "Weight below minimum shows validation error"
      ]
    },
    {
      "user_story": "US-005",
      "feature": "F005",
      "gherkin_file": "specs/bdd/processing.feature",
      "scenarios": [
        "Pose estimation extracts joint coordinates",
        "Pose estimation fails with poor video quality",
        "Processing status shows step progress",
        "Processing takes longer than expected",
        "Subject tracking maintains across frames"
      ]
    },
    {
      "user_story": "US-005",
      "feature": "F006",
      "gherkin_file": "specs/bdd/processing.feature",
      "scenarios": [
        "Defensive action detection identifies guards",
        "No significant actions detected",
        "Stamps include confidence scores",
        "Strike detection identifies punch types"
      ]
    },
    {
      "user_story": "US-005",
      "feature": "F007",
      "gherkin_file": "specs/bdd/processing.feature",
      "scenarios": [
        "Analysis adapts to beginner experience level",
        "Analysis adapts to competitive experience level",
        "LLM API exhausts retries",
        "LLM API failure triggers retry",
        "LLM generates strategic analysis"
      ]
    },
    {
      "user_story": "US-006",
      "feature": "F005",
      "gherkin_file": "specs/bdd/processing.feature",
      "scenarios": [
        "Pose estimation extracts joint coordinates",
        "Pose estimation fails with poor video quality",
        "Processing status shows step progress",
        "Processing takes longer than expected",
        "Subject tracking maintains across frames"
      ]
    },
    {
      "user_story": "US-006",
      "feature": "F006",
      "gherkin_file": "specs/bdd/processing.feature",
      "scenarios": [
        "Defensive action detection identifies guards",
        "No significant actions detected",
        "Stamps include confidence scores",
        "Strike detection identifies punch types"
      ]
    },
    {
      "user_story": "US-006",
      "feature": "F007",
      "gherkin_file": "specs/bdd/processing.feature",
      "scenarios": [
        "Analysis adapts to beginner experience level",
        "Analysis adapts to competitive experience level",
        "LLM API exhausts retries",
        "LLM API failure triggers retry",
        "LLM generates strategic analysis"
      ]
    },
    {
      "user_story": "US-007",
      "feature": "F005",
      "gherkin_file": "specs/bdd/processing.feature",
      "scenarios": [
        "Pose estimation extracts joint coordinates",
        "Pose estimation fails with poor video quality",
        "Processing status shows step progress",
        "Processing takes longer than expected",
        "Subject tracking maintains across frames"
      ]
    },
    {
      "user_story": "US-007",
      "feature": "F006",
      "gherkin_file": "specs/bdd/processing.feature",
      "scenarios": [
        "Defensive action detection identifies guards",
        "No significant actions detected",
        "Stamps include confidence scores",
        "Strike detection identifies punch types"
      ]
    },
    {
      "user_story": "US-007",
      "feature": "F007",
      "gherkin_file": "specs/bdd/processing.feature",
      "scenarios": [
        "Analysis adapts to beginner experience level",
        "Analysis adapts to competitive experience level",
        "LLM API exhausts retries",
        "LLM API failure triggers retry",
        "LLM generates strategic analysis"
      ]
    },
    {
      "user_story": "US-008",
      "feature": "F008",
      "gherkin_file": "specs/bdd/report.feature",
      "scenarios": [
        "Report displays correctly on desktop viewport",
        "Report displays correctly on mobile viewport",
        "Report displays key moments with timestamps",
        "Report displays metrics with visualizations",
        "Report displays recommendations section",
        "Report displays strengths section",
        "Report displays summary section",
        "Report displays weaknesses section",
        "Report includes AI disclaimer",
        "Report loads within performance target"
      ]
    },
    {
      "user_story": "US-009",
      "feature": "F009",
      "gherkin_file": "specs/bdd/sharing.feature",
      "scenarios": [
        "Disabled share link returns error",
        "Report shows share button in private state",
        "Shared report accessible without login",
        "Shared report displays social preview",
        "User copies share link to clipboard",
        "User disables sharing",
        "User enables sharing and gets unique URL",
        "User re-enables sharing gets new URL"
      ]
    },
    {
      "user_story": "US-010",
      "feature": "F010",
      "gherkin_file": "specs/bdd/dashboard.feature",
      "scenarios": [
        "Dashboard displays report list sorted by date",
        "Dashboard loading state shows skeletons",
        "Dashboard shows empty state for new user",
        "Report list item shows thumbnail and summary",
        "User deletes report with confirmation",
        "User navigates to report from list"
      ]
    }
  ]
}
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
