# PunchAnalytics - Market Benchmark

## Inputs
- docs/DOC_CONTRACT.md
- docs/product/PRD.md
- docs/product/REQUIREMENTS_BASELINE.md
- Web research (January 2026)

---

## Comparable products

### 1. Jabbr.ai / DeepStrike
**Category:** AI-powered combat sports analysis (professional/broadcast focus)

**Overview:** Jabbr offers "The World's First AI Camera for Combat Sports" with DeepStrike computer-vision technology. They raised a $5M seed round in October 2025 led by Buckley Ventures with participation from SevenSevenSix (Alexis Ohanian), Shrug, John Zimmer, Andre Ward, and PSV Tech.

**Key capabilities:**
- Real-time punch tracking during live fights
- Computer vision analysis for landed punch statistics
- Integration with broadcast networks (TNT Sports since May 2024)
- Dedicated camera hardware unit for gyms
- Multi-use cases: training, fighting, watching, analyzing, coaching

**Target users:** Professional fighters, broadcast networks, gyms, coaches

**Pricing:** Not publicly disclosed; waitlist-based access

**Relevance to PunchAnalytics:** Jabbr targets professional/enterprise market with hardware + software bundle. PunchAnalytics differentiates by targeting amateur/recreational boxers with smartphone-based video upload and LLM-generated strategic feedback.

---

### 2. Fight AI (iOS App)
**Category:** AI MMA coaching mobile app

**Overview:** Fight AI is a mobile app providing AI-powered form analysis and personalized training for MMA fighters, covering boxing, kickboxing, wrestling, and BJJ.

**Key capabilities:**
- AI Form Analyzer: Upload clips for technical breakdowns
- Personalized training plans based on fighting style
- Fighter profile with progress tracking
- AI Coach delivering customized drills and advice

**Target users:** Amateur MMA fighters, recreational martial artists

**Pricing:**
- Free download with in-app purchases
- Monthly Pro: $9.99
- Yearly Pro: $39.99
- Lifetime Pro: $79.99

**User reviews:** 4.5/5 stars (47 ratings). Users report form improvement but note video processing delays (10+ hours reported) and upload failures.

**Relevance to PunchAnalytics:** Direct competitor in the consumer AI coaching space. Fight AI focuses on solo training forms; PunchAnalytics differentiates with sparring-specific analysis and LLM-generated strategic (not just technical) feedback.

---

### 3. Dartfish
**Category:** Professional sports video analysis platform

**Overview:** Dartfish provides video analysis, coaching tools, and performance tracking for combat sports including boxing, judo, and taekwondo. Used by Olympic and professional programs globally.

**Key capabilities:**
- Frame-by-frame video examination
- Action tagging and annotation system
- Performance tracking over time
- Multi-sport support with specialized tools

**Target users:** Professional coaches, national teams, sports federations, universities

**Pricing:** Enterprise pricing (not publicly disclosed); typically $500-2000/year for institutional licenses

**Relevance to PunchAnalytics:** Dartfish is the institutional gold standard but inaccessible to individual amateurs. PunchAnalytics targets the underserved amateur segment with automated AI analysis instead of manual coaching annotation.

---

### 4. iSportsAnalysis
**Category:** Online sports video analysis platform

**Overview:** iSportsAnalysis describes itself as "the world's most powerful online sports analysis solution" with support for boxing match analysis.

**Key capabilities:**
- Video upload and tagging system
- Automated interactive report generation
- Telestration tools for drawing on video
- Playlist creation for teachable moments
- 24-hour professional coding service available
- Compatible with any camera or AI filming systems (VEO, Pixellot)

**Target users:** Boxing coaches, sports universities, athletic clubs

**Pricing:** Free trial available; subscription pricing not publicly disclosed

**Relevance to PunchAnalytics:** iSportsAnalysis requires manual tagging by coaches or their professional service. PunchAnalytics differentiates with fully automated AI analysis accessible to individuals.

---

### 5. VueMotion
**Category:** AI-powered athletic movement analysis

**Overview:** VueMotion uses computer vision to analyze athletic movements from smartphone video, supporting 11 sports with biomechanical analysis.

**Key capabilities:**
- Video analysis from smartphones without sensors
- Biomechanical modeling with 3D movement profiles
- Speed metrics, step analysis, ground contact time
- Kinograms (movement visualization overlays)
- Frame-by-frame annotation and comparison
- Video sharing among team members

**Target users:** Professional sports teams (35+ elite organizations), coaches, athletic trainers

**Pricing:** Annual subscription with per-video AI credit system (1 credit = 1 analyzed video)

**Relevance to PunchAnalytics:** VueMotion demonstrates the credit-based analysis model. However, VueMotion focuses on linear athletic movements (running, jumping); PunchAnalytics specializes in combat sports strategic analysis.

---

## Feature parity and gaps

1. **Video upload from smartphone (Table stakes)**: All competitors support standard video formats. PunchAnalytics will support MP4, MOV, WebM with 500MB limit.

2. **Pose/movement tracking (Table stakes)**: Competitors use MediaPipe or proprietary CV models. PunchAnalytics will use MediaPipe 33-joint extraction.

3. **Analysis report generation (Table stakes)**: Market offers automated or semi-automated reports. PunchAnalytics provides fully automated LLM-generated analysis.

4. **Report sharing (Table stakes)**: Competitors offer URL or in-app sharing. PunchAnalytics provides unique URL with OG tags for social preview.

5. **Mobile-friendly interface (Table stakes)**: Market standard is responsive or native apps. PunchAnalytics is responsive web (mobile-first).

6. **LLM strategic analysis (Differentiator)**: Fight AI offers form feedback only; Dartfish requires manual annotation. PunchAnalytics provides AI-generated national-team-caliber strategic feedback.

7. **Sparring-specific analysis (Differentiator)**: Fight AI focuses on solo training only. PunchAnalytics is designed for sparring footage with subject selection.

8. **Boxing-specific metrics (Differentiator)**: Competitors use generic pose estimation. PunchAnalytics calculates reach-to-distance ratio, guard recovery speed, and upper body tilt.

9. **Stamp generation (Differentiator)**: Competitors require manual tagging. PunchAnalytics provides automated key moment detection (strikes, defensive actions).

10. **Korean market focus (Differentiator)**: No competitors offer Kakao OAuth. PunchAnalytics provides Kakao OAuth primary with Korean localization.

11. **Individual consumer pricing (Differentiator)**: Competitors focus on enterprise (Dartfish, iSportsAnalysis) or require hardware (Jabbr). PunchAnalytics is web-only, no hardware, consumer-accessible.

12. **Processing time (Gap to address)**: Fight AI users report 10+ hour waits; we must target under 5 minutes.

13. **Upload reliability (Gap to address)**: Fight AI users report upload failures; we need resumable chunked uploads.

14. **Analysis accuracy (Gap to address)**: Must validate LLM output quality with domain experts before launch.

15. **Error messaging (Gap to address)**: Clear guidance when videos are unprocessable (Fight AI lacks this).

---

## Quality bar

Based on market research and competitor analysis, PunchAnalytics must meet or exceed:

### Performance expectations
1. **Processing latency**: Under 5 minutes for 3-minute video (Fight AI benchmark: 10+ hours is unacceptable)
2. **Upload success rate**: 99%+ for videos under 500MB (resumable uploads required)
3. **Page load time**: Under 2 seconds initial load; under 1.5 seconds for report pages
4. **API availability**: 99.5% uptime (standard for consumer SaaS)
5. **Concurrent user support**: 100+ active users without degradation

### UX expectations
6. **Mobile-first design**: Touch-optimized interface; minimum 375px viewport support
7. **Progress visibility**: Real-time upload progress bar; processing status updates
8. **Error recovery**: Clear error messages with actionable guidance; no cryptic failures
9. **Frictionless sharing**: One-tap copy link; social preview cards (OG tags)
10. **Korean localization**: Native Korean UI copy; proper hangul typography

### Analysis quality expectations
11. **Pose estimation accuracy**: 95%+ joint detection rate for clear, well-lit videos
12. **Stamp relevance**: Key moments (strikes, guards) detected with 90%+ precision
13. **LLM output quality**: Specific, actionable feedback (not generic advice); domain expert validation
14. **Metric accuracy**: Calculated metrics (reach ratio, tilt angle) within 10% of manual measurement

### Security and trust expectations
15. **Authentication security**: OAuth 2.0 with secure token handling; no credential exposure
16. **Data privacy**: Videos and reports private by default; explicit sharing opt-in
17. **Encryption**: At-rest encryption for stored videos; HTTPS-only transport
18. **Compliance**: GDPR/PIPA-aligned data handling for Korean and international users

---

## Sources

1. **Jabbr.ai** - https://jabbr.ai/
   - AI camera for combat sports; DeepStrike computer vision; $5M seed funding (October 2025)

2. **Fight AI (App Store)** - https://apps.apple.com/us/app/fight-ai-your-ai-mma-coach/id6747051940
   - iOS MMA coaching app; $9.99-79.99 pricing; 4.5/5 rating with processing time complaints

3. **Dartfish Combat Sports** - https://www.dartfish.com/combatsports/
   - Professional video analysis platform; boxing, judo, taekwondo support; enterprise pricing

4. **iSportsAnalysis Boxing** - https://www.isportsanalysis.com/boxing-video-analysis.php
   - Online boxing analysis platform; manual tagging + professional coding service

5. **VueMotion** - https://www.vuemotion.com/
   - AI athletic movement analysis; credit-based pricing; 35+ elite sports organizations

6. **Roboflow Boxing Punch Detection** - https://blog.roboflow.com/boxing-punch-detection-computer-vision/
   - Technical reference for computer vision approaches to punch detection

7. **arXiv: Multi-person Physics-based Pose Estimation for Combat Sports** - https://arxiv.org/html/2504.08175v1
   - Academic research on multi-view pose tracking for combat sports (April 2025)

8. **arXiv: BoxingVI Dataset** - https://arxiv.org/html/2511.16524v1
   - Boxing action recognition benchmark with 6,915 labeled punch clips (November 2025)
