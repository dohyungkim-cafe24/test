# PunchAnalytics UX Contract

## Inputs
- docs/product/PRD.md
- docs/product/REQUIREMENTS_BASELINE.md
- docs/product/MARKET_BENCHMARK.md
- docs/product/STORY_MAP.md

---

## Scope

### In Scope (Launch P0)
| User Story | Description | Primary Flow |
|------------|-------------|--------------|
| US-001 | OAuth Authentication | Login via Kakao/Google |
| US-002 | Video Upload | File selection, progress, validation |
| US-003 | Subject Selection | Thumbnail grid, tap-to-select |
| US-004 | Body Spec Input | Height/weight/experience/stance form |
| US-005 | Pose Processing | Background job status polling |
| US-006 | Stamp Generation | Key moment detection display |
| US-007 | LLM Analysis | Strategic feedback generation |
| US-008 | Report Generation | Metrics visualization, recommendations |
| US-009 | Report Sharing | Unique URL generation, copy link |
| US-010 | Report History | Dashboard list, navigation |

### Out of Scope
- Real-time video analysis
- Multi-person automatic tracking
- Opponent analysis features
- In-app video editing/trimming
- Payment/subscription flows
- Community/social features beyond sharing
- Coach annotation features
- Push notifications

---

## Competitive bar

Based on Market Benchmark analysis, PunchAnalytics must exceed these competitor standards:

| Dimension | Competitor Baseline | PunchAnalytics Target |
|-----------|--------------------|-----------------------|
| Processing Time | Fight AI: 10+ hours | Under 5 minutes |
| Upload Success | Fight AI: frequent failures | 99%+ with resumable uploads |
| Mobile UX | Varied quality | Material Design 3, touch-optimized |
| Error Guidance | Generic errors | Specific, actionable messages |
| Sharing | Basic URL sharing | Social preview cards (OG tags) |
| Korean Support | None | Native Korean UI, Kakao OAuth |

### Differentiation Requirements
1. LLM-generated strategic feedback (not just form analysis)
2. Sparring-specific subject selection workflow
3. Boxing-specific metrics visualization (reach ratio, guard speed, tilt)
4. Automated stamp generation (no manual tagging)
5. Korean market optimization (Kakao primary, hangul typography)

---

## Non-negotiables

### User Experience
1. **Mobile-first responsive**: All flows functional on 375px+ viewports
2. **Progress visibility**: Upload and processing always show status
3. **Error recovery**: Every error state provides actionable next steps
4. **Korean localization**: Complete Korean UI copy for all user-facing text
5. **WCAG 2.1 AA**: Core flows accessible (focus management, color contrast, labels)

### Privacy and Trust
6. **Private by default**: Videos and reports are private until user explicitly shares
7. **AI disclaimer**: Every report displays disclaimer about AI limitations
8. **Transparent processing**: Clear indication of what AI is analyzing

### Performance
9. **Page load under 2 seconds**: Initial load and navigation
10. **Report load under 1.5 seconds**: Analysis report rendering
11. **Touch targets minimum 48x48px**: All interactive elements

---

## Quality bar

### Visual Quality
| Criterion | Requirement | Verification |
|-----------|-------------|--------------|
| Design system compliance | 100% Material Design 3 | Token usage audit |
| Color contrast | WCAG AA (4.5:1 text, 3:1 UI) | Automated contrast check |
| Typography scale | M3 type scale only | Design token validation |
| Spacing consistency | Only use defined spacing tokens | Code review |
| Icon consistency | Material Symbols set only | Asset audit |

### Interaction Quality
| Criterion | Requirement | Verification |
|-----------|-------------|--------------|
| Touch targets | Minimum 48x48px | Automated measurement |
| Tap feedback | Visual state change under 100ms | Manual testing |
| Loading indicators | All async operations show progress | Flow testing |
| Error messaging | Specific, actionable text | Copy review |
| Form validation | Inline, real-time feedback | Interaction testing |

### Accessibility Quality
| Criterion | Requirement | Verification |
|-----------|-------------|--------------|
| Keyboard navigation | All interactive elements reachable | Manual keyboard test |
| Screen reader labels | All inputs and buttons labeled | aXe audit |
| Focus indicators | Visible focus ring on all elements | Visual inspection |
| Motion sensitivity | Respect prefers-reduced-motion | Media query validation |
| Language declaration | Korean lang attribute | HTML validation |

---

## Performance

### Page Load Targets
| Page | LCP Target | FID Target | CLS Target |
|------|------------|------------|------------|
| Landing/Login | 1.5s | 100ms | 0.1 |
| Upload | 1.5s | 100ms | 0.1 |
| Processing Status | 1.0s | 100ms | 0.05 |
| Report View | 1.5s | 100ms | 0.1 |
| Dashboard | 2.0s | 100ms | 0.1 |

### Interaction Targets
| Interaction | Response Target |
|-------------|-----------------|
| Button tap feedback | 100ms |
| Navigation transition | 300ms |
| Form field focus | 100ms |
| Toast appearance | 200ms |
| Dialog open/close | 300ms |

### Upload Performance
| File Size | Upload Target (3G) | Upload Target (4G) |
|-----------|-------------------|-------------------|
| 100MB | 3 minutes | 30 seconds |
| 300MB | 8 minutes | 90 seconds |
| 500MB | 12 minutes | 2.5 minutes |

---

## Heuristic acceptance criteria

### Nielsen's Heuristics Evaluation

| Heuristic | Acceptance Criterion | Evidence Required |
|-----------|---------------------|-------------------|
| Visibility of system status | Upload progress bar updates every 500ms; processing status updates every 5 seconds | Screenshot of progress states |
| Match between system and real world | Korean boxing terminology used correctly; metric units (cm, kg) | Copy audit |
| User control and freedom | Cancel upload available; back navigation from all screens | Flow walkthrough |
| Consistency and standards | M3 components throughout; consistent icons | Design audit |
| Error prevention | File validation before upload; form validation before submit | Edge case testing |
| Recognition rather than recall | Experience levels shown as options, not free text; recent uploads visible | UI review |
| Flexibility and efficiency | Returning users see pre-filled body specs | Returning user flow test |
| Aesthetic and minimalist design | Report sections collapsible; no decorative elements | Design review |
| Help users recognize and recover from errors | Every error shows specific cause and suggested action | Error state screenshots |
| Help and documentation | Upload guidelines visible; metric explanations in tooltips | Content audit |

### Journey Completion Criteria

| Journey | Start Point | End Point | Success Criterion |
|---------|-------------|-----------|-------------------|
| First Upload | Landing page | Report view | Under 8 minutes total (includes 5 min processing) |
| Return Upload | Dashboard | Report view | Under 6 minutes total |
| Share Report | Report view | Link copied | Under 10 seconds |
| View History | Any authenticated page | Past report | Under 5 seconds |

---

## Evidence

### Required Evidence for Launch
| Evidence Type | Description | Acceptance Threshold |
|---------------|-------------|---------------------|
| Journey Screenshots | Screenshots of each screen in primary flows | All 10 user stories covered |
| State Screenshots | Each UI state (loading/empty/error/success) captured | All states per UI_STATES.md |
| Accessibility Audit | aXe automated scan results | Zero critical/serious issues |
| Performance Report | Lighthouse scores for key pages | Performance score 80+ |
| Mobile Screenshots | All screens at 375px viewport | 100% functional |
| Desktop Screenshots | All screens at 1280px viewport | 100% functional |
| Error Flow Evidence | Screenshot of each error type with message | All error types per COPY.md |
| Korean Copy Review | Screenshot showing Korean UI in context | Native speaker approval |

### Evidence Collection Process
1. Engineer implements feature per UX_SPEC.md
2. Tester captures screenshots during verification
3. Screenshots stored in `evidence/ux/` with naming: `{story_id}_{screen}_{state}.png`
4. UX Validator reviews evidence against this contract
5. UX Judge confirms pass/fail per heuristic criteria

---

## Change control

### Change Request Process
1. Submit change request with rationale and impact assessment
2. UX Designer evaluates against competitive bar and non-negotiables
3. Product Manager approves scope changes affecting user stories
4. Update affected documents: UX_SPEC.md, UI_STATES.md, COPY.md
5. Re-verify affected evidence

### Protected Elements (Require Change Request)
- User story flows (US-001 through US-010)
- Error message content
- Navigation structure
- Color roles and tokens
- Typography scale
- Component specifications

### Permitted Refinements (No Change Request)
- Animation timing adjustments (within motion token ranges)
- Minor copy clarifications (not error messages)
- Additional helper text
- Spacing fine-tuning (within token system)
- Icon selection (within Material Symbols set)

### Version History
| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2026-01-21 | Initial UX Contract | UX Designer |
