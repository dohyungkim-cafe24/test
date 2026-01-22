# PunchAnalytics UX Report

## Inputs
- docs/product/REQUIREMENTS_BASELINE.md
- docs/product/MARKET_BENCHMARK.md
- docs/product/STORY_MAP.md
- docs/ux/UX_CONTRACT.md
- docs/ux/DESIGN_SYSTEM.md
- docs/ux/UX_SPEC.md
- docs/ux/UI_STATES.md
- docs/ux/IA_MAP.md
- docs/ux/COPY.md

---

## Summary

This UX report documents the design decisions, rationale, and open questions for PunchAnalytics, an AI-powered boxing sparring strategy analysis platform targeting amateur boxers in Korea.

### Deliverables Completed

| Deliverable | Status | Key Highlights |
|-------------|--------|----------------|
| DESIGN_SYSTEM.md | Complete | Material Design 3 baseline with boxing-specific color roles |
| design_tokens.json | Complete | 150+ tokens covering colors, typography, spacing, motion |
| UX_CONTRACT.md | Complete | Quality bar exceeds Fight AI benchmark (5 min vs 10+ hours) |
| UI_STATES.md | Complete | All 5 state categories fully specified for all screens |
| UX_SPEC.md | Complete | 5 primary flows, 10 screens, full component inventory |
| IA_MAP.md | Complete | 14 routes, 5 key flows documented |
| COPY.md | Complete | Full bilingual copy (English/Korean) with boxing glossary |

### Design Philosophy

1. **Mobile-first, touch-optimized**: Primary users will upload from smartphones used to record sparring
2. **Progressive disclosure**: Complex analysis data revealed through collapsible sections
3. **Encouraging tone**: Users are investing in self-improvement; feedback should motivate
4. **Korean market fit**: Kakao OAuth primary, Korean boxing terminology, metric units

### Competitive Differentiation

Based on MARKET_BENCHMARK.md analysis, this design addresses key competitor gaps:

| Gap | PunchAnalytics Solution |
|-----|------------------------|
| Fight AI: 10+ hour processing | Clear progress steps, 5-minute target with status updates |
| Fight AI: upload failures | Resumable chunked uploads with connection-lost recovery |
| Dartfish: enterprise-only pricing | Consumer-accessible web app, no hardware required |
| All competitors: no Korean support | Native Korean UI, Kakao OAuth, Korean boxing terminology |

---

## Decisions

### D1: Material Design 3 as Baseline

**Decision**: Adopt Material Design 3 (M3) as the foundational design system.

**Rationale**:
- Proven patterns reduce design/development time
- Robust accessibility built-in
- Consistent with modern mobile expectations
- Extensive component library available

**Trade-offs**:
- May feel less "unique" than fully custom design
- Mitigation: Boxing-specific color roles and metric visualizations add character

### D2: Linear Upload Wizard (Not Tabbed)

**Decision**: Implement upload flow as a linear wizard (file -> subject -> specs -> processing) rather than tabbed or free-form.

**Rationale**:
- First-time users need guidance through the process
- Prevents incomplete submissions
- Easier to track progress and provide contextual help
- Matches mental model of "step-by-step analysis"

**Trade-offs**:
- Less flexibility for power users
- Mitigation: Returning users get pre-filled body specs, reducing friction

### D3: Subject Selection via Tap-on-Thumbnail

**Decision**: Use thumbnail grid with tap-to-select for subject identification, rather than timeline scrubbing or automatic detection.

**Rationale**:
- Simpler implementation than full video player
- Users intuitively understand "tap on yourself"
- Avoids multi-person tracking complexity (out of scope)
- 6-9 frames provides sufficient selection options

**Trade-offs**:
- May not capture optimal frame for some videos
- Mitigation: Extract frames at 1-second intervals; allow re-upload if needed

### D4: Three-Step Processing Display

**Decision**: Show processing as three discrete steps (movements -> key moments -> insights) rather than single indeterminate progress.

**Rationale**:
- Makes 2-5 minute wait feel shorter
- Educates users about what the system does
- Provides meaningful progress indication
- Matches actual pipeline stages

**Trade-offs**:
- Steps may not take equal time
- Mitigation: Use indeterminate progress within each step; show time estimates

### D5: Private by Default, Explicit Sharing

**Decision**: Reports are private by default; sharing requires explicit toggle action.

**Rationale**:
- Respects user privacy (sparring footage is personal)
- Matches user expectation (REQUIREMENTS_BASELINE non-negotiable)
- Prevents accidental exposure
- Users who want to share can easily enable

**Trade-offs**:
- Fewer reports shared initially
- Mitigation: Prominent share button; easy one-tap enable flow

### D6: Single Report View for Owner and Viewer

**Decision**: Use same report component for authenticated owner view and public shared view, with conditional action buttons.

**Rationale**:
- Consistent experience
- Simpler implementation
- Easier maintenance
- Owner can preview exactly what others will see

**Trade-offs**:
- Must carefully hide owner-only actions for viewers
- Mitigation: Clear conditional rendering; test both paths

### D7: Bilingual Copy from Day One

**Decision**: Implement full Korean and English UI copy simultaneously, not as a later localization pass.

**Rationale**:
- Korean is primary market; English is secondary
- Avoids technical debt of retrofitting i18n
- Copy nuances differ between languages (not just translation)
- Boxing terminology needs domain-specific Korean terms

**Trade-offs**:
- More upfront copy work
- Mitigation: Complete COPY.md with both languages; use standard i18n library

### D8: Bottom FAB for Upload on Mobile

**Decision**: Use floating action button (FAB) for "Upload Video" on mobile dashboard, regular button on desktop.

**Rationale**:
- FAB is M3 standard for primary mobile action
- Always accessible regardless of scroll position
- Touch-friendly target size
- Desktop has more space for inline button

**Trade-offs**:
- FAB obscures some content at bottom
- Mitigation: Proper spacing; FAB only on dashboard screen

### D9: No In-App Video Playback for MVP

**Decision**: Report shows timestamps and thumbnails but no video player with overlay visualization.

**Rationale**:
- Video overlay is P1 feature (US-011)
- Reduces MVP complexity significantly
- Text-based analysis is still valuable
- Users can correlate timestamps with their original video

**Trade-offs**:
- Less engaging report experience
- Mitigation: Clear timestamp linking; include in P1 roadmap

### D10: 4-Second Toast Duration

**Decision**: Snackbar/toast messages display for 4 seconds (6 seconds if undo action available).

**Rationale**:
- Long enough to read without blocking
- M3 standard timing
- Undo actions need more time for user decision

**Trade-offs**:
- May be too fast for slow readers
- Mitigation: Critical errors use persistent dialogs, not toasts

---

## Open questions

### Resolved During Design

| Question | Resolution |
|----------|------------|
| Video trimming in-app? | No - out of scope for MVP; users trim before upload |
| Email verification required? | No - OAuth provides verified email; reduce friction |
| Maximum video duration? | 3 minutes - balances processing cost and user need |
| Maximum file size? | 500MB - supports HD video for 3 minutes |

### Deferred to Implementation

| Question | Impact | Decision Deadline |
|----------|--------|-------------------|
| Exact frame extraction interval for thumbnails | Affects subject selection quality | Before US-003 implementation |
| Specific LLM prompt structure | Affects analysis quality | Before US-007 implementation |
| Retry count and backoff timing for LLM failures | Affects user wait experience | Before US-007 implementation |
| Soft delete retention period for reports | Affects storage costs | Before US-010 implementation |

### Requires Domain Expert Input

| Question | Why It Matters | Owner |
|----------|---------------|-------|
| Boxing terminology localization accuracy | Korean boxing terms must be correct | Product + Korean Boxing Expert |
| Metric threshold definitions (what is "good" reach ratio?) | Analysis credibility | Product + Boxing Coach |
| Typical amateur boxer video conditions | Affects pose estimation guidance | Engineering + User Research |

### Post-Launch Evaluation

| Question | Success Metric | Timeline |
|----------|---------------|----------|
| Is 5-minute processing acceptable to users? | Drop-off rate during processing < 10% | 30 days post-launch |
| Do users understand subject selection? | Selection success rate > 95% | 30 days post-launch |
| Is Korean copy natural to native speakers? | User feedback, NPS by language | 60 days post-launch |
| Are error messages actionable enough? | Support ticket rate for upload errors | 30 days post-launch |
