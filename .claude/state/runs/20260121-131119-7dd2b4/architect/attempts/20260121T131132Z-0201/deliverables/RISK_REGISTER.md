# PunchAnalytics - Risk Register

## Inputs

- `docs/product/REQUIREMENTS_BASELINE.md`
- `docs/product/PRD.md`
- `docs/product/MARKET_BENCHMARK.md`
- `features.json`

---

## Overview

This register documents identified risks for PunchAnalytics, their likelihood, impact, and mitigation strategies. Risks are prioritized using a standard risk matrix.

### Risk Scoring

**Likelihood:**
- Low (L): < 10% probability
- Medium (M): 10-50% probability
- High (H): > 50% probability

**Impact:**
- Low (L): Minor inconvenience, workaround available
- Medium (M): Feature degradation, user friction
- High (H): Data loss, security breach, complete feature failure
- Critical (C): System-wide outage, regulatory violation

**Priority = Likelihood x Impact:**
| | Low Impact | Medium Impact | High Impact | Critical Impact |
|---|---|---|---|---|
| **High Likelihood** | P3 | P2 | P1 | P0 |
| **Medium Likelihood** | P4 | P3 | P2 | P1 |
| **Low Likelihood** | P5 | P4 | P3 | P2 |

---

## Risk Summary

| ID | Risk | Likelihood | Impact | Priority | Status |
|----|------|------------|--------|----------|--------|
| R001 | Video processing fails on low-quality input | High | High | P1 | Open |
| R002 | LLM generates incorrect/harmful coaching advice | Medium | High | P2 | Open |
| R003 | LLM API unavailable or rate limited | Medium | High | P2 | Open |
| R004 | Processing latency exceeds 5-minute target | Medium | Medium | P3 | Open |
| R005 | Video upload fails on mobile networks | Medium | Medium | P3 | Open |
| R006 | OAuth provider outage blocks authentication | Low | High | P3 | Open |
| R007 | Shared reports expose unintended private data | Low | Critical | P2 | Open |
| R008 | Storage costs exceed budget at scale | Medium | Medium | P3 | Open |
| R009 | MediaPipe accuracy insufficient for boxing | Medium | High | P2 | Open |
| R010 | Korean boxing terminology lost in LLM translation | Medium | Medium | P3 | Open |
| R011 | Concurrent processing overloads workers | Medium | Medium | P3 | Open |
| R012 | User uploads malicious video files | Low | High | P3 | Open |
| R013 | Database connection exhaustion under load | Low | High | P3 | Open |
| R014 | Refresh token theft enables account takeover | Low | Critical | P2 | Open |
| R015 | GDPR/PIPA compliance violations | Low | Critical | P2 | Open |

---

## Risk Details

### R001: Video Processing Fails on Low-Quality Input @F005

**Description:** Users upload videos with poor lighting, unstable camera, low resolution, or obscured subjects. MediaPipe pose estimation fails or produces unreliable results for >20% of frames.

**Likelihood:** High
- Market benchmark shows Fight AI users report frequent upload failures
- User-generated smartphone video has highly variable quality
- Boxing gym lighting often poor

**Impact:** High
- User receives no analysis after waiting (frustration)
- Wasted compute resources
- Negative perception of product reliability

**Mitigation:**
| Action | Owner | Status |
|--------|-------|--------|
| Implement pre-upload video quality check (resolution, brightness, stability) | Engineering | Planned |
| Provide clear upload guidelines with example good/bad videos | Product | Planned |
| Show quality warning before processing starts | UX | Planned |
| Implement partial analysis with confidence scores for marginal videos | Engineering | Planned |
| Display specific error messages with actionable guidance (AC-028) | Engineering | Required |

**Contingency:** If quality check is too restrictive, allow processing with prominent warnings about reduced accuracy.

**Monitoring:**
- Metric: `pose_estimation_failure_rate`
- Alert: > 15% failure rate over 1 hour

---

### R002: LLM Generates Incorrect or Harmful Coaching Advice @F007

**Description:** The LLM produces analysis that is factually wrong, contradicts boxing fundamentals, or suggests training that could cause injury.

**Likelihood:** Medium
- GPT-4 class models have limited domain expertise in boxing
- Hallucination risk when interpreting numerical pose data
- Training corpus may contain conflicting or outdated techniques

**Impact:** High
- User follows bad advice and performs worse
- User gets injured following dangerous recommendations
- Reputational damage and potential liability

**Mitigation:**
| Action | Owner | Status |
|--------|-------|--------|
| Develop boxing-specific prompt with domain expert review | Product + ML | Planned |
| Include mandatory disclaimer on every report (AC-040) | Product | Required |
| Set low temperature (0.3) for consistent outputs | Engineering | Planned |
| Implement output validation for obviously wrong claims | Engineering | Planned |
| Conduct domain expert review of 50+ sample outputs before launch | Product | Planned |
| Add user feedback mechanism ("Was this advice helpful?") | Product | P1 |

**Contingency:** If quality cannot be assured, add stronger disclaimers and reduce specificity of recommendations.

**Monitoring:**
- Manual review of random sample (5% of reports weekly)
- User feedback tracking

---

### R003: LLM API Unavailable or Rate Limited @F007

**Description:** OpenAI API experiences outage, rate limits, or degraded performance, preventing analysis completion.

**Likelihood:** Medium
- OpenAI has had notable outages in 2024-2025
- Rate limits can be hit during traffic spikes
- API latency can spike during high-demand periods

**Impact:** High
- Users wait for processing that never completes
- Analysis pipeline backs up
- Cannot generate reports

**Mitigation:**
| Action | Owner | Status |
|--------|-------|--------|
| Implement retry with exponential backoff (3 retries) (AC-039) | Engineering | Required |
| Notify user on final failure with manual retry option | Engineering | Required |
| Queue failed analyses for automatic retry when API recovers | Engineering | Planned |
| Evaluate fallback LLM provider (Anthropic Claude, local model) | Engineering | P1 |
| Monitor OpenAI status page and alert on degradation | SRE | Planned |
| Pre-provision higher rate limits with OpenAI | Operations | Planned |

**Contingency:** If outage extends > 1 hour, display banner on upload page warning of delays.

**Monitoring:**
- Metric: `llm_api_error_rate`, `llm_api_latency_p95`
- Alert: > 5% error rate or p95 > 30 seconds

---

### R004: Processing Latency Exceeds 5-Minute Target @F005

**Description:** Video analysis takes longer than the 5-minute p95 target, causing user abandonment.

**Likelihood:** Medium
- 3-minute video at 30fps = 5,400 frames to process
- MediaPipe inference is CPU-intensive
- LLM API latency varies significantly

**Impact:** Medium
- Poor user experience
- Users may close browser before completion
- Competitive disadvantage vs. faster alternatives

**Mitigation:**
| Action | Owner | Status |
|--------|-------|--------|
| Process every 2nd frame (15fps effective) for longer videos | Engineering | Planned |
| Parallelize pose estimation across workers | Engineering | Planned |
| Show real-time progress with estimated completion time | UX | Required |
| Implement WebSocket status updates (AC-029) | Engineering | Required |
| Benchmark and optimize slowest pipeline stages | Engineering | Planned |
| Consider GPU workers for pose estimation | Engineering | P1 |

**Contingency:** If 5-minute target unachievable, set user expectation to 10 minutes and optimize over time.

**Monitoring:**
- Metric: `processing_duration_p50`, `processing_duration_p95`
- Alert: p95 > 6 minutes

---

### R005: Video Upload Fails on Mobile Networks @F002

**Description:** Users experience upload failures due to network instability, timeouts, or mobile data limitations.

**Likelihood:** Medium
- 500MB upload on 3G/4G can take 10+ minutes
- Mobile connections drop frequently
- Users may switch networks mid-upload

**Impact:** Medium
- User frustration (wasted time and data)
- Incomplete uploads consume storage
- Users may abandon product

**Mitigation:**
| Action | Owner | Status |
|--------|-------|--------|
| Implement chunked resumable upload (AC-011) | Engineering | Required |
| Auto-resume after network recovery | Engineering | Required |
| Client-side video compression option | Engineering | P1 |
| Show upload speed and estimated time remaining | UX | Planned |
| Validate file locally before upload starts | Engineering | Required |
| Set reasonable chunk timeout (30 seconds) | Engineering | Planned |

**Contingency:** If resumable upload too complex for launch, implement at minimum a clear retry mechanism.

**Monitoring:**
- Metric: `upload_success_rate`, `upload_failure_by_reason`
- Alert: Success rate < 95%

---

### R006: OAuth Provider Outage Blocks Authentication @F001

**Description:** Kakao or Google OAuth services experience outage, preventing users from logging in.

**Likelihood:** Low
- Major providers have 99.9%+ uptime
- Outages are rare but do occur

**Impact:** High
- No new users can sign up
- Existing users cannot access their data
- Complete feature blockage

**Mitigation:**
| Action | Owner | Status |
|--------|-------|--------|
| Support both Kakao and Google OAuth | Engineering | Required |
| If one provider down, encourage users to try other | UX | Planned |
| Display provider status on login page during outages | Engineering | Planned |
| Implement session persistence to reduce re-auth frequency | Engineering | Planned |
| Cache user data to allow limited read-only access during outage | Engineering | P2 |

**Contingency:** During outage, display maintenance message with estimated resolution.

**Monitoring:**
- External monitoring of OAuth endpoints
- Alert: > 5% auth failure rate

---

### R007: Shared Reports Expose Unintended Private Data @F009

**Description:** Sharing mechanism inadvertently exposes data user did not intend to share, or share links are accessed by unauthorized parties.

**Likelihood:** Low
- Sharing is explicit opt-in (AC-049)
- Share links use random hashes

**Impact:** Critical
- Privacy violation
- Regulatory risk (GDPR, PIPA)
- Reputational damage

**Mitigation:**
| Action | Owner | Status |
|--------|-------|--------|
| Require explicit enable action to share (not default) | Engineering | Required |
| Generate cryptographically secure share hashes | Engineering | Required |
| Allow users to revoke sharing at any time (AC-054) | Engineering | Required |
| Do not index shared reports (X-Robots-Tag: noindex) | Engineering | Planned |
| Shared reports show only analysis, not user profile | Engineering | Planned |
| Implement share link audit log | Engineering | P1 |
| Consider optional password protection for shares | Product | P2 |

**Contingency:** If breach occurs, immediate link invalidation and user notification.

**Monitoring:**
- Metric: `share_link_access_by_ip` (unusual patterns)
- Alert: Anomalous access patterns

---

### R008: Storage Costs Exceed Budget at Scale @F002

**Description:** Video storage costs grow faster than revenue as user base scales.

**Likelihood:** Medium
- 500MB videos from many users adds up quickly
- Users may not delete old videos

**Impact:** Medium
- Margin compression
- May need to implement limits or pricing

**Mitigation:**
| Action | Owner | Status |
|--------|-------|--------|
| Implement S3 lifecycle rules (move to IA after 30 days) | SRE | Planned |
| Track storage cost per user | Engineering | Planned |
| Set per-user storage quota (e.g., 10 videos) | Product | P1 |
| Offer video deletion with report preservation | Product | Planned |
| Client-side compression before upload | Engineering | P1 |
| Delete videos but keep processed data and reports | Engineering | P2 |

**Contingency:** Implement paid tier with higher storage limits.

**Monitoring:**
- Metric: `storage_bytes_total`, `storage_cost_per_user`
- Alert: Storage growth > 20% month-over-month

---

### R009: MediaPipe Accuracy Insufficient for Boxing @F005, @F006

**Description:** MediaPipe pose estimation trained on general activities may not accurately track fast boxing movements (punches, head movement).

**Likelihood:** Medium
- MediaPipe designed for general pose, not combat sports
- Fast punches may blur between frames
- Gloves may confuse hand tracking

**Impact:** High
- Stamps detect wrong actions
- Metrics calculated incorrectly
- Analysis loses credibility

**Mitigation:**
| Action | Owner | Status |
|--------|-------|--------|
| Benchmark MediaPipe on boxing-specific test set | ML Engineer | Planned |
| Tune confidence thresholds for boxing movements | ML Engineer | Planned |
| Process at higher frame rate for fast movements | Engineering | Planned |
| Add post-processing to smooth tracking outliers | Engineering | Planned |
| Display confidence scores on stamps (AC-032) | Engineering | Required |
| Evaluate boxing-specific models (BoxingVI dataset) | ML Engineer | P1 |

**Contingency:** If accuracy unacceptable, pivot to simpler metrics or partner with specialized CV provider.

**Monitoring:**
- Metric: `pose_detection_confidence_avg`
- Manual accuracy review on sample videos

---

### R010: Korean Boxing Terminology Lost in LLM Translation @F007

**Description:** LLM generates analysis in English that poorly maps to Korean boxing terminology, or Korean prompts produce lower quality output.

**Likelihood:** Medium
- GPT-4 training data skews English
- Boxing terminology differs between Korean and English traditions
- Korean boxing community uses specific terms

**Impact:** Medium
- Analysis feels foreign to Korean users
- Technical terms may be wrong or awkward
- Reduces perceived expertise

**Mitigation:**
| Action | Owner | Status |
|--------|-------|--------|
| Build Korean boxing terminology glossary | Product | Planned |
| Validate prompts and outputs with Korean boxing coaches | Product | Planned |
| Generate analysis in Korean directly (not translated) | Engineering | Planned |
| Include terminology guide in analysis output | Product | P1 |
| A/B test Korean vs. English analysis quality | Product | P1 |

**Contingency:** Launch English-first, add Korean analysis post-launch after validation.

**Monitoring:**
- User feedback on terminology accuracy
- Review by Korean boxing domain experts

---

### R011: Concurrent Processing Overloads Workers @F005

**Description:** Traffic spike causes more video uploads than workers can process, creating long queues.

**Likelihood:** Medium
- Viral sharing could cause sudden traffic
- Processing is resource-intensive (5+ minutes per video)

**Impact:** Medium
- Long wait times for analysis
- User abandonment
- Potential worker crashes

**Mitigation:**
| Action | Owner | Status |
|--------|-------|--------|
| Auto-scale workers based on queue depth | SRE | Planned |
| Implement queue depth monitoring and alerting | SRE | Planned |
| Set maximum concurrent analyses per user (2) | Engineering | Planned |
| Show queue position to users | UX | Planned |
| Implement priority queue (paying users first, P2) | Engineering | P2 |

**Contingency:** Temporarily pause new uploads during extreme load.

**Monitoring:**
- Metric: `processing_queue_depth`, `processing_wait_time`
- Alert: Queue depth > 50 or wait > 10 minutes

---

### R012: User Uploads Malicious Video Files @F002

**Description:** Attacker uploads file disguised as video that exploits server-side vulnerabilities (buffer overflow, code execution).

**Likelihood:** Low
- Requires targeted attack
- Video processing libraries are well-tested

**Impact:** High
- Server compromise
- Data breach
- Service disruption

**Mitigation:**
| Action | Owner | Status |
|--------|-------|--------|
| Validate file type via magic bytes, not extension | Engineering | Planned |
| Process videos in isolated container/sandbox | SRE | Planned |
| Set strict resource limits on processing containers | SRE | Planned |
| Use up-to-date MediaPipe and FFmpeg versions | Engineering | Planned |
| Scan uploaded files with ClamAV | SRE | P1 |
| Implement upload rate limiting | Engineering | Required |

**Contingency:** Quarantine suspicious files, alert security team, suspend processing.

**Monitoring:**
- Metric: `file_validation_failure_rate`
- Alert: Unusual file validation patterns

---

### R013: Database Connection Exhaustion Under Load @F001-F010

**Description:** High traffic exhausts PostgreSQL connection pool, causing request failures.

**Likelihood:** Low
- Properly sized connection pool should handle load
- Async queries reduce connection time

**Impact:** High
- API requests fail
- Complete service degradation

**Mitigation:**
| Action | Owner | Status |
|--------|-------|--------|
| Use connection pooler (PgBouncer) | SRE | Planned |
| Set appropriate pool size (25-50 connections) | Engineering | Planned |
| Monitor connection pool utilization | SRE | Planned |
| Implement query timeouts (30 seconds) | Engineering | Planned |
| Review slow queries and add indexes | Engineering | Planned |
| Implement read replica for dashboard queries | SRE | P2 |

**Contingency:** Increase connection limit, scale database vertically.

**Monitoring:**
- Metric: `db_connections_active`, `db_connection_wait_time`
- Alert: Pool utilization > 80%

---

### R014: Refresh Token Theft Enables Account Takeover @F001

**Description:** Attacker steals refresh token and uses it to maintain persistent access to user account.

**Likelihood:** Low
- Requires XSS or device compromise
- HttpOnly cookies reduce theft vectors

**Impact:** Critical
- Account takeover
- Access to private videos and reports
- Potential for data deletion

**Mitigation:**
| Action | Owner | Status |
|--------|-------|--------|
| Store refresh tokens in HttpOnly, Secure, SameSite=Strict cookies | Engineering | Required |
| Bind refresh tokens to user agent/IP (detect anomalies) | Engineering | Planned |
| Implement token rotation on refresh | Engineering | Planned |
| Allow users to view and revoke active sessions | Product | P1 |
| Detect and alert on multiple concurrent sessions | Engineering | P1 |
| Implement short refresh token expiry (7 days) | Engineering | Required |

**Contingency:** Implement emergency "logout all sessions" capability.

**Monitoring:**
- Metric: `concurrent_sessions_per_user`
- Alert: > 5 concurrent sessions

---

### R015: GDPR/PIPA Compliance Violations @F001-F010

**Description:** System handling of personal data (videos, analysis, profile) violates EU GDPR or Korean PIPA requirements.

**Likelihood:** Low
- Modern compliance practices well-documented
- No special categories of data

**Impact:** Critical
- Regulatory fines
- Mandatory breach notification
- Service restrictions in EU/Korea

**Mitigation:**
| Action | Owner | Status |
|--------|-------|--------|
| Implement data export capability (GDPR Article 20) | Engineering | P1 |
| Implement account deletion with data purge (GDPR Article 17) | Engineering | Required |
| Document data processing purposes in privacy policy | Legal | Planned |
| Obtain explicit consent for data processing | Product | Required |
| Implement data retention limits | Engineering | Planned |
| Encrypt PII at rest (AES-256) | Engineering | Required |
| Maintain processing records | Legal | Planned |

**Contingency:** Engage privacy counsel if violation suspected.

**Monitoring:**
- Regular compliance audit (quarterly)
- Data deletion verification

---

## Risk Review Schedule

| Review Type | Frequency | Participants |
|-------------|-----------|--------------|
| Risk register review | Bi-weekly | Eng Lead, Product, SRE |
| New risk identification | Each sprint | Full team |
| Mitigation status update | Weekly | Risk owners |
| Post-incident risk update | After each incident | Incident responders |

---

## Appendix: Risk by Feature

| Feature | Associated Risks |
|---------|-----------------|
| @F001 Auth | R006, R014, R015 |
| @F002 Upload | R005, R008, R012 |
| @F003 Subject Selection | R001 |
| @F004 Body Specs | R015 |
| @F005 Pose Estimation | R001, R004, R009, R011 |
| @F006 Stamp Generation | R009 |
| @F007 LLM Analysis | R002, R003, R010 |
| @F008 Report Display | R002 |
| @F009 Report Sharing | R007 |
| @F010 Dashboard | R013 |
