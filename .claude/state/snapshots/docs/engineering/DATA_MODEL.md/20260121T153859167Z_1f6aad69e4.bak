# PunchAnalytics - Data Model

## Inputs

- `docs/product/REQUIREMENTS_BASELINE.md`
- `docs/product/STORY_MAP.md`
- `features.json`
- `specs/bdd/TRACEABILITY.json`

---

## Overview

PunchAnalytics uses PostgreSQL as the primary relational database for structured data, with S3-compatible object storage for binary files (videos, thumbnails, pose data).

### Storage Responsibilities

| Storage | Data Types | Access Pattern |
|---------|------------|----------------|
| PostgreSQL | Users, videos (metadata), analyses, reports, stamps, share_links | Transactional, relational queries |
| S3 | Video files, thumbnails, pose JSON, OG images | Large object storage, CDN delivery |
| Redis | Sessions, rate limits, job queue, pub/sub | Ephemeral, high-frequency access |

---

## Entities

### User @F001

Stores user account information from OAuth providers.

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    name            VARCHAR(255),
    avatar_url      TEXT,
    provider        VARCHAR(20) NOT NULL,  -- 'kakao' | 'google'
    provider_id     VARCHAR(255) NOT NULL,

    -- Body specs (persisted for returning users) @F004
    height_cm       SMALLINT CHECK (height_cm BETWEEN 100 AND 250),
    weight_kg       SMALLINT CHECK (weight_kg BETWEEN 30 AND 200),
    experience_level VARCHAR(20) CHECK (experience_level IN ('beginner', 'intermediate', 'advanced', 'competitive')),
    stance          VARCHAR(10) CHECK (stance IN ('orthodox', 'southpaw')),

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_at   TIMESTAMPTZ,
    deleted_at      TIMESTAMPTZ,  -- Soft delete

    UNIQUE (provider, provider_id)
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_provider ON users(provider, provider_id);
```

**Field notes:**
- `provider_id`: Unique identifier from OAuth provider
- `body_specs` fields: Persisted for pre-fill on subsequent uploads (AC-024)
- `deleted_at`: Soft delete for account recovery

---

### RefreshToken @F001

Stores refresh tokens for session management.

```sql
CREATE TABLE refresh_tokens (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash      VARCHAR(64) NOT NULL UNIQUE,  -- SHA-256 of token
    expires_at      TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at      TIMESTAMPTZ,

    -- Device/session tracking
    user_agent      TEXT,
    ip_address      INET
);

CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at) WHERE revoked_at IS NULL;
```

---

### Video @F002

Stores video file metadata (binary stored in S3).

```sql
CREATE TABLE videos (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- File metadata
    filename        VARCHAR(255) NOT NULL,
    content_type    VARCHAR(50) NOT NULL,
    file_size       BIGINT NOT NULL,
    duration_seconds SMALLINT NOT NULL CHECK (duration_seconds BETWEEN 60 AND 180),

    -- Storage paths (S3 keys)
    storage_key     VARCHAR(512) NOT NULL UNIQUE,
    thumbnail_key   VARCHAR(512),  -- First thumbnail for list display

    -- Upload tracking
    upload_status   VARCHAR(20) NOT NULL DEFAULT 'uploading',
    upload_started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    upload_completed_at TIMESTAMPTZ,

    -- Video properties (extracted after upload)
    width           SMALLINT,
    height          SMALLINT,
    fps             REAL,
    total_frames    INTEGER,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ,

    CONSTRAINT chk_upload_status CHECK (upload_status IN ('uploading', 'processing', 'ready', 'failed'))
);

CREATE INDEX idx_videos_user ON videos(user_id, created_at DESC);
CREATE INDEX idx_videos_status ON videos(upload_status) WHERE deleted_at IS NULL;
```

**Field notes:**
- `storage_key`: S3 path to video file (e.g., `videos/{user_id}/{video_id}.mp4`)
- `upload_status`: Tracks upload lifecycle
- `duration_seconds`: Validated at upload time (1-3 minutes)

---

### UploadSession @F002

Tracks chunked upload progress.

```sql
CREATE TABLE upload_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Upload configuration
    filename        VARCHAR(255) NOT NULL,
    file_size       BIGINT NOT NULL,
    content_type    VARCHAR(50) NOT NULL,
    duration_seconds SMALLINT NOT NULL,
    chunk_size      INTEGER NOT NULL DEFAULT 5242880,  -- 5MB
    total_chunks    SMALLINT NOT NULL,

    -- Progress tracking
    chunks_received SMALLINT NOT NULL DEFAULT 0,
    bytes_received  BIGINT NOT NULL DEFAULT 0,

    -- Status
    status          VARCHAR(20) NOT NULL DEFAULT 'active',
    expires_at      TIMESTAMPTZ NOT NULL,
    video_id        UUID REFERENCES videos(id),  -- Set on completion

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,

    CONSTRAINT chk_session_status CHECK (status IN ('active', 'completed', 'cancelled', 'expired'))
);

CREATE INDEX idx_upload_sessions_user ON upload_sessions(user_id, created_at DESC);
CREATE INDEX idx_upload_sessions_expires ON upload_sessions(expires_at) WHERE status = 'active';
```

**Field notes:**
- Sessions expire after 1 hour of inactivity
- `chunks_received` enables resumable uploads

---

### UploadChunk @F002

Tracks individual chunk uploads for resumability.

```sql
CREATE TABLE upload_chunks (
    session_id      UUID NOT NULL REFERENCES upload_sessions(id) ON DELETE CASCADE,
    chunk_number    SMALLINT NOT NULL,

    size_bytes      INTEGER NOT NULL,
    md5_hash        VARCHAR(32),
    storage_key     VARCHAR(512) NOT NULL,

    uploaded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (session_id, chunk_number)
);
```

---

### Thumbnail @F003

Stores extracted video thumbnails for subject selection.

```sql
CREATE TABLE thumbnails (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id        UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,

    frame_number    INTEGER NOT NULL,
    timestamp_seconds REAL NOT NULL,
    storage_key     VARCHAR(512) NOT NULL,

    -- Person detection results
    detected_persons JSONB,  -- Array of {person_id, bounding_box, confidence}

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (video_id, frame_number)
);

CREATE INDEX idx_thumbnails_video ON thumbnails(video_id, timestamp_seconds);
```

**`detected_persons` structure:**
```json
[
  {
    "person_id": "p1",
    "bounding_box": {"x": 120, "y": 80, "width": 200, "height": 400},
    "confidence": 0.95
  }
]
```

---

### BodySpecs @F004

Stores body specifications per analysis (allows different specs per video).

```sql
CREATE TABLE body_specs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    video_id        UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,

    height_cm       SMALLINT NOT NULL CHECK (height_cm BETWEEN 100 AND 250),
    weight_kg       SMALLINT NOT NULL CHECK (weight_kg BETWEEN 30 AND 200),
    experience_level VARCHAR(20) NOT NULL,
    stance          VARCHAR(10) NOT NULL,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_experience CHECK (experience_level IN ('beginner', 'intermediate', 'advanced', 'competitive')),
    CONSTRAINT chk_stance CHECK (stance IN ('orthodox', 'southpaw'))
);

CREATE INDEX idx_body_specs_video ON body_specs(video_id);
```

---

### Subject @F003

Stores selected analysis subject (the user in the video).

```sql
CREATE TABLE subjects (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id        UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,

    -- Selection from thumbnail
    thumbnail_id    UUID NOT NULL REFERENCES thumbnails(id),
    person_id       VARCHAR(20) NOT NULL,  -- References detected_persons array

    -- Initial bounding box for tracking
    initial_bbox    JSONB NOT NULL,  -- {x, y, width, height}

    -- Tracking quality (updated after pose estimation)
    tracking_confidence REAL,
    frames_tracked  INTEGER,
    frames_lost     INTEGER,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (video_id)  -- One subject per video
);

CREATE INDEX idx_subjects_video ON subjects(video_id);
```

---

### Analysis @F005, @F006, @F007

Tracks analysis pipeline execution.

```sql
CREATE TABLE analyses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id        UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject_id      UUID NOT NULL REFERENCES subjects(id),
    body_specs_id   UUID NOT NULL REFERENCES body_specs(id),

    -- Pipeline status
    status          VARCHAR(20) NOT NULL DEFAULT 'queued',
    current_stage   VARCHAR(30),
    progress_percent SMALLINT DEFAULT 0,

    -- Stage timestamps
    queued_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at      TIMESTAMPTZ,
    pose_started_at TIMESTAMPTZ,
    pose_completed_at TIMESTAMPTZ,
    stamps_started_at TIMESTAMPTZ,
    stamps_completed_at TIMESTAMPTZ,
    llm_started_at  TIMESTAMPTZ,
    llm_completed_at TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    failed_at       TIMESTAMPTZ,

    -- Error tracking
    error_code      VARCHAR(50),
    error_message   TEXT,
    retry_count     SMALLINT DEFAULT 0,

    -- Result references
    report_id       UUID,  -- Set on completion
    pose_data_key   VARCHAR(512),  -- S3 key for pose JSON

    -- Worker tracking
    worker_id       VARCHAR(100),

    CONSTRAINT chk_analysis_status CHECK (status IN (
        'queued', 'processing', 'pose_estimation', 'stamp_generation',
        'llm_analysis', 'report_generation', 'completed', 'failed'
    ))
);

CREATE INDEX idx_analyses_video ON analyses(video_id);
CREATE INDEX idx_analyses_user ON analyses(user_id, created_at DESC);
CREATE INDEX idx_analyses_status ON analyses(status) WHERE status NOT IN ('completed', 'failed');
```

**Status state machine:**
```
queued -> processing -> pose_estimation -> stamp_generation -> llm_analysis -> report_generation -> completed
                   \-> failed (from any state)
```

---

### Stamp @F006

Stores detected key moments (strikes, defensive actions).

```sql
CREATE TABLE stamps (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id     UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,

    -- Timing
    timestamp_seconds REAL NOT NULL,
    frame_number    INTEGER NOT NULL,

    -- Action classification
    action_type     VARCHAR(30) NOT NULL,
    side            VARCHAR(10) NOT NULL,  -- 'left', 'right', 'both'
    confidence      REAL NOT NULL CHECK (confidence BETWEEN 0 AND 1),

    -- Detection details (for debugging/improvement)
    velocity_vector JSONB,  -- {x, y, z} at detection
    trajectory_data JSONB,  -- Points leading to detection

    -- Visual
    thumbnail_key   VARCHAR(512),

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_action_type CHECK (action_type IN (
        'jab', 'straight', 'hook', 'uppercut',  -- Strikes
        'guard_up', 'guard_down', 'slip', 'duck', 'bob_weave'  -- Defense
    )),
    CONSTRAINT chk_side CHECK (side IN ('left', 'right', 'both'))
);

CREATE INDEX idx_stamps_analysis ON stamps(analysis_id, timestamp_seconds);
CREATE INDEX idx_stamps_type ON stamps(action_type);
```

---

### Report @F008

Stores generated analysis reports.

```sql
CREATE TABLE reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id     UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE UNIQUE,
    video_id        UUID NOT NULL REFERENCES videos(id),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Summary
    performance_score SMALLINT CHECK (performance_score BETWEEN 0 AND 100),
    overall_assessment TEXT NOT NULL,

    -- Analysis sections (stored as JSONB for flexibility)
    strengths       JSONB NOT NULL,  -- Array of {title, description, metric_reference}
    weaknesses      JSONB NOT NULL,
    recommendations JSONB NOT NULL,  -- Array of {title, description, priority, drill_type}

    -- Calculated metrics
    metrics         JSONB NOT NULL,  -- {metric_name: {value, unit, benchmark_min, benchmark_max, percentile}}

    -- LLM metadata
    llm_model       VARCHAR(50),
    prompt_tokens   INTEGER,
    completion_tokens INTEGER,

    -- Timestamps
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ,

    -- Disclaimer (required by product requirements)
    disclaimer      TEXT NOT NULL DEFAULT 'This AI analysis is for training purposes only and is not a substitute for professional coaching. Always train under proper supervision.'
);

CREATE INDEX idx_reports_user ON reports(user_id, created_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_reports_video ON reports(video_id);
```

**`metrics` structure example:**
```json
{
  "punch_frequency": {
    "value": 2.3,
    "unit": "punches_per_10s",
    "benchmark_min": 1.5,
    "benchmark_max": 3.0,
    "percentile": 65
  },
  "guard_recovery_speed": {
    "value": 0.8,
    "unit": "seconds",
    "benchmark_min": 0.3,
    "benchmark_max": 0.5,
    "percentile": 35
  }
}
```

---

### ShareLink @F009

Manages public sharing of reports.

```sql
CREATE TABLE share_links (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id       UUID NOT NULL REFERENCES reports(id) ON DELETE CASCADE,

    -- Public identifier (8-char hash)
    share_hash      VARCHAR(8) NOT NULL UNIQUE,

    -- Status
    is_active       BOOLEAN NOT NULL DEFAULT true,

    -- Analytics
    view_count      INTEGER NOT NULL DEFAULT 0,
    last_viewed_at  TIMESTAMPTZ,

    -- Social preview
    og_image_key    VARCHAR(512),  -- S3 key for generated OG image

    -- Timestamps
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at      TIMESTAMPTZ,

    -- Only one active link per report
    UNIQUE (report_id) WHERE is_active = true  -- Partial unique index
);

CREATE UNIQUE INDEX idx_share_links_active ON share_links(report_id) WHERE is_active = true;
CREATE INDEX idx_share_links_hash ON share_links(share_hash) WHERE is_active = true;
```

**Field notes:**
- `share_hash`: 8-character alphanumeric (base62 encoded UUID fragment)
- Re-enabling sharing generates new hash (old links invalidated)

---

## Relations

### Entity Relationship Diagram

```
                                    ┌─────────────┐
                                    │   users     │
                                    └──────┬──────┘
                                           │
              ┌────────────────────────────┼────────────────────────────┐
              │                            │                            │
              ▼                            ▼                            ▼
    ┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
    │ refresh_tokens  │          │     videos      │          │   body_specs    │
    └─────────────────┘          └────────┬────────┘          └─────────────────┘
                                          │
              ┌───────────────────────────┼───────────────────────────┐
              │                           │                           │
              ▼                           ▼                           ▼
    ┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
    │ upload_sessions │          │   thumbnails    │          │    subjects     │
    └────────┬────────┘          └─────────────────┘          └────────┬────────┘
             │                                                         │
             ▼                                                         │
    ┌─────────────────┐                                               │
    │  upload_chunks  │                                               │
    └─────────────────┘                                               │
                                                                      │
                                          ┌───────────────────────────┘
                                          │
                                          ▼
                                 ┌─────────────────┐
                                 │    analyses     │
                                 └────────┬────────┘
                                          │
              ┌───────────────────────────┴───────────────────────────┐
              │                                                       │
              ▼                                                       ▼
    ┌─────────────────┐                                     ┌─────────────────┐
    │     stamps      │                                     │    reports      │
    └─────────────────┘                                     └────────┬────────┘
                                                                     │
                                                                     ▼
                                                            ┌─────────────────┐
                                                            │  share_links    │
                                                            └─────────────────┘
```

### Cardinality Summary

| Relationship | Cardinality | Description |
|--------------|-------------|-------------|
| User -> Videos | 1:N | User can upload many videos |
| User -> RefreshTokens | 1:N | User can have multiple active sessions |
| Video -> Thumbnails | 1:N | Video has multiple thumbnails (10 frames) |
| Video -> Subject | 1:1 | One subject selected per video |
| Video -> Analysis | 1:1 | One analysis per video (can retry) |
| Analysis -> Stamps | 1:N | Analysis detects multiple stamps |
| Analysis -> Report | 1:1 | One report per successful analysis |
| Report -> ShareLink | 1:1 | One active share link per report |

---

## Migrations

### Migration Strategy

1. **Forward-only migrations**: No rollback scripts in production
2. **Backward compatible**: Old code must work with new schema during deployment
3. **Data migrations**: Separate from schema migrations for large tables
4. **Testing**: All migrations tested against production-like data volume

### Migration Naming Convention

```
YYYYMMDD_HHMMSS_<description>.sql
```

Example:
```
20260121_130000_create_users_table.sql
20260121_130100_create_videos_table.sql
20260121_130200_add_body_specs_to_users.sql
```

### Initial Migration Order

1. `create_users_table` - Base user entity
2. `create_refresh_tokens_table` - Auth tokens
3. `create_videos_table` - Video metadata
4. `create_upload_sessions_table` - Chunked upload tracking
5. `create_upload_chunks_table` - Chunk tracking
6. `create_thumbnails_table` - Frame extraction
7. `create_body_specs_table` - User measurements
8. `create_subjects_table` - Analysis subject
9. `create_analyses_table` - Pipeline tracking
10. `create_stamps_table` - Detected actions
11. `create_reports_table` - Analysis output
12. `create_share_links_table` - Public sharing

### Sample Migration: Add Body Specs to Users

```sql
-- Migration: 20260121_130200_add_body_specs_to_users.sql
-- Description: Add body spec columns to users for pre-fill functionality (AC-024)

BEGIN;

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS height_cm SMALLINT,
    ADD COLUMN IF NOT EXISTS weight_kg SMALLINT,
    ADD COLUMN IF NOT EXISTS experience_level VARCHAR(20),
    ADD COLUMN IF NOT EXISTS stance VARCHAR(10);

ALTER TABLE users
    ADD CONSTRAINT chk_user_height CHECK (height_cm IS NULL OR height_cm BETWEEN 100 AND 250),
    ADD CONSTRAINT chk_user_weight CHECK (weight_kg IS NULL OR weight_kg BETWEEN 30 AND 200),
    ADD CONSTRAINT chk_user_experience CHECK (experience_level IS NULL OR experience_level IN ('beginner', 'intermediate', 'advanced', 'competitive')),
    ADD CONSTRAINT chk_user_stance CHECK (stance IS NULL OR stance IN ('orthodox', 'southpaw'));

COMMENT ON COLUMN users.height_cm IS 'Persisted body spec for pre-fill on upload';
COMMENT ON COLUMN users.weight_kg IS 'Persisted body spec for pre-fill on upload';

COMMIT;
```

### Data Retention Policy

| Entity | Retention | Trigger |
|--------|-----------|---------|
| Videos (file) | Until user deletion | Soft delete -> 30 days -> hard delete |
| Reports | Until user deletion | Soft delete -> 30 days -> hard delete |
| Upload sessions | 24 hours | Automatic cleanup job |
| Refresh tokens | 7 days after expiry | Automatic cleanup job |
| Share links (revoked) | 90 days | Automatic cleanup job |

### Backup Strategy

| Data | Frequency | Retention | Method |
|------|-----------|-----------|--------|
| PostgreSQL | Continuous | 30 days | WAL archiving + daily snapshots |
| S3 (videos) | N/A | Versioning enabled | S3 versioning + cross-region |
| S3 (pose data) | N/A | No versioning | Single copy (regeneratable) |

---

## Indexes

### Query Pattern Analysis

| Query Pattern | Frequency | Index |
|---------------|-----------|-------|
| User by email (login) | High | `idx_users_email` |
| User by OAuth provider | High | `idx_users_provider` |
| Videos by user (dashboard) | High | `idx_videos_user` |
| Reports by user (dashboard) | High | `idx_reports_user` |
| Analysis by status (worker) | High | `idx_analyses_status` |
| Share link by hash (public) | High | `idx_share_links_hash` |
| Thumbnails by video | Medium | `idx_thumbnails_video` |
| Stamps by analysis | Medium | `idx_stamps_analysis` |

### Partial Indexes

Used for frequently filtered conditions:

```sql
-- Only query active sessions
CREATE INDEX idx_upload_sessions_expires ON upload_sessions(expires_at)
    WHERE status = 'active';

-- Only query non-deleted reports
CREATE INDEX idx_reports_user ON reports(user_id, created_at DESC)
    WHERE deleted_at IS NULL;

-- Only query active share links
CREATE INDEX idx_share_links_hash ON share_links(share_hash)
    WHERE is_active = true;

-- Only query pending analyses
CREATE INDEX idx_analyses_status ON analyses(status)
    WHERE status NOT IN ('completed', 'failed');
```

---

## Constraints

### Business Rules Enforced at Database Level

| Rule | Constraint | Table |
|------|------------|-------|
| Video duration 1-3 min | CHECK | videos |
| Height 100-250cm | CHECK | body_specs, users |
| Weight 30-200kg | CHECK | body_specs, users |
| One subject per video | UNIQUE | subjects |
| One active share per report | Partial UNIQUE | share_links |
| Valid status transitions | CHECK | analyses, videos |
| Confidence 0-1 | CHECK | stamps |

### Foreign Key Cascade Rules

| Relationship | On Delete |
|--------------|-----------|
| videos -> users | CASCADE |
| analyses -> videos | CASCADE |
| reports -> analyses | CASCADE |
| share_links -> reports | CASCADE |
| stamps -> analyses | CASCADE |
| refresh_tokens -> users | CASCADE |

---

## S3 Storage Schema

### Bucket Structure

```
punchanalytics-storage/
├── videos/
│   └── {user_id}/
│       └── {video_id}.mp4
├── thumbnails/
│   └── {video_id}/
│       └── frame_{frame_number:03d}.jpg
├── pose_data/
│   └── {analysis_id}/
│       └── pose.json.gz
├── stamps/
│   └── {report_id}/
│       └── {stamp_id}.jpg
└── og_images/
    └── {report_id}.png
```

### Lifecycle Rules

| Path | Rule |
|------|------|
| `videos/*` | Transition to IA after 30 days; delete after user deletion |
| `thumbnails/*` | Delete with video |
| `pose_data/*` | Delete with analysis |
| `og_images/*` | Delete with report |
