# PunchAnalytics - Product Requirements Document

## Inputs
- docs/DOC_CONTRACT.md
- docs/product/REQUIREMENTS_BASELINE.md
- docs/product/MARKET_BENCHMARK.md
- docs/product/STORY_MAP.md
- User prompt (project context: AI-powered boxing sparring strategy analysis platform)

---

## Problem

Amateur and recreational boxers lack access to professional-grade fight analysis. National team athletes benefit from dedicated coaching staff who manually review footage, identify technical flaws, and prescribe improvements. Meanwhile, the vast majority of boxing practitioners—gym members, amateur competitors, and self-taught fighters—train without objective feedback on their sparring performance.

**Why now:**
1. Pose estimation technology (MediaPipe, OpenPose) has matured to extract 33-joint XYZ coordinates from standard smartphone video at consumer-grade accuracy
2. LLMs can now interpret structured movement data and generate human-readable strategic coaching feedback
3. The Korean fitness and combat sports market is growing, with increasing demand for data-driven training tools
4. Video sharing via unique URLs is now a standard UX pattern that enables community and coach feedback loops

**Current alternatives fail because:**
- Professional analysis services (Dartfish, iSportsAnalysis) target institutional buyers with enterprise pricing
- Consumer apps (Fight AI) focus on solo training forms rather than sparring strategy
- No existing product combines pose estimation, LLM-based strategic analysis, and social sharing for boxing sparring

---

## Goals

1. **Democratize expert-level sparring analysis**: Provide national-team-caliber strategic feedback to any boxer with a smartphone
2. **Enable measurable improvement**: Deliver actionable, specific recommendations that users can apply in their next session
3. **Foster community and coaching relationships**: Allow easy sharing of analysis reports with coaches, training partners, and online communities
4. **Establish a scalable AI coaching platform**: Build a foundation for expanding to other combat sports (MMA, Muay Thai, Taekwondo)

---

## Non-goals

1. **Real-time analysis during sparring**: V1 focuses on post-session video upload; live feedback is out of scope
2. **Opponent identification and tracking**: Analysis focuses on the user-selected subject; automated multi-person tracking is deferred
3. **Wearable sensor integration**: Analysis uses video-only input; no accelerometer or heart rate data
4. **Competition scoring or judging**: The platform provides training feedback, not bout scoring
5. **Monetization in V1**: Pricing, subscriptions, and payment processing are deferred to post-launch
6. **Multi-language support**: V1 supports Korean and English only; additional localization is deferred

---

## Success

PunchAnalytics succeeds when:
1. Users can upload a sparring video, select themselves, and receive a strategic analysis report within 5 minutes
2. Analysis reports contain specific, actionable feedback (not generic coaching advice)
3. Users share reports with coaches or communities and receive follow-up engagement
4. Users return to upload additional videos to track improvement over time

---

## Success metrics

### Leading indicators (adoption)
| Metric | Target (90 days post-launch) | Instrumentation |
|--------|------------------------------|-----------------|
| Registered users | 500 | Auth events |
| Videos uploaded | 1,500 | Upload completion events |
| Reports generated | 1,200 (80% upload-to-report) | Report generation events |
| Reports shared | 400 (33% of reports) | Share link creation events |

### Engagement indicators (value delivery)
| Metric | Target | Instrumentation |
|--------|--------|-----------------|
| Report completion rate | 95% | Report status tracking |
| Repeat upload rate | 30% of users upload 2+ videos | User cohort analysis |
| Time to second upload | Median < 14 days | Event timestamps |
| Report view time | Median > 2 minutes | Page engagement tracking |

### Quality guardrails
| Metric | Threshold | Instrumentation |
|--------|-----------|-----------------|
| Upload-to-report latency | p95 < 5 minutes | Pipeline timing |
| Pose estimation success rate | > 95% | Pipeline error tracking |
| LLM generation failure rate | < 2% | Pipeline error tracking |
| Report page load time | p95 < 2 seconds | Frontend performance |
| API response time | p95 < 500ms | Backend APM |

---

## Scope

### Launch (P0) - Minimum Viable Product

**Core user journey:**
1. User signs up/logs in via Kakao or Google OAuth
2. User uploads a 1-3 minute sparring video
3. User selects the analysis subject from a thumbnail grid
4. User inputs body specs (height, weight, experience level, fighting style)
5. System extracts XYZ coordinates and generates stamps (key striking moments)
6. LLM analyst produces strategic feedback report
7. User views report with strengths, weaknesses, and improvement recommendations
8. User can share report via unique URL

**Technical MVP:**
- MediaPipe pose estimation for 33-joint coordinate extraction
- Stamp generation algorithm (speed change detection, trajectory inflection points)
- JSON text log formatting for LLM consumption
- LLM prompt engineering for boxing-specific strategic analysis
- Report rendering with visualizations
- URL-based report sharing (no authentication required to view shared reports)

### Post-launch (P1)
- Video overlay visualization showing pose skeleton and stamps
- Historical report comparison (progress tracking)
- Coach annotation feature on shared reports
- Push notifications for processing completion

### Future (P2)
- Multi-person tracking with automatic subject identification
- Opponent analysis integration
- Community features (public report feed, leaderboards)
- Subscription tiers with premium analysis depth
- Additional combat sports (MMA, Muay Thai)

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Pose estimation accuracy degrades with low video quality | High | High | Provide upload guidelines; implement quality validation before processing; show confidence scores |
| LLM generates generic or incorrect coaching advice | Medium | High | Extensive prompt engineering with domain experts; include disclaimers; allow user feedback on analysis quality |
| Processing time exceeds user patience threshold | Medium | Medium | Show progress indicators; send notification when complete; optimize pipeline parallelization |
| Korean boxing terminology may not map well to English LLM training | Medium | Medium | Build Korean boxing glossary; test with Korean coaches; consider fine-tuning |
| Video upload failures on mobile networks | Medium | Medium | Implement resumable uploads; compress video client-side; provide offline queue |
| Shared report links could expose private training data | Low | High | Make sharing opt-in; allow link expiration; enable link revocation |

---

## Open questions

| Question | Why it matters | Decision deadline | Owner |
|----------|---------------|-------------------|-------|
| What specific metrics should the LLM analyze beyond the initial list (reach-to-distance ratio, upper body tilt, guard recovery speed)? | Defines the differentiated value proposition | Before BDD spec | Product + Domain Expert |
| Should we support video trimming in-app or require pre-trimmed uploads? | Affects upload UX complexity and processing costs | Before UX design | Product + Engineering |
| What is the maximum video duration and file size? | Affects storage costs and processing time | Before architecture | Engineering + Product |
| How do we handle videos where the selected subject is not clearly visible throughout? | Affects analysis reliability and user trust | Before BDD spec | Engineering + Product |
| Will we require email verification for account creation? | Affects friction vs. spam prevention tradeoff | Before implementation | Product + Security |
