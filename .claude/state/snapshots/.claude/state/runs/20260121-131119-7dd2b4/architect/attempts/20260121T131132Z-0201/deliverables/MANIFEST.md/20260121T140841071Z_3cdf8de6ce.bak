# Deliverables Manifest

- stage: **arch**
- agent: **architect**
- contract_version: **1.6.8**
- write_once: **False**

## Golden rules
- Write all artifacts into this attempt's `deliverables/` directory.
- You **may** revise deliverables in-place within this attempt (preferred for small fixes).
- Do **not** edit `MANIFEST.md` / `MANIFEST.json` (the contract for this attempt).
- Do **not** edit canonical docs directly (`docs/**`, `specs/**`, `features.json`, `plan.md`, `plan.json`).

## Inputs to read (non-negotiable)
- source: **stage_inputs_by_agent**
- docs/product/REQUIREMENTS_BASELINE.md
- docs/product/MARKET_BENCHMARK.md
- docs/ux/UX_CONTRACT.md
- docs/ux/DESIGN_SYSTEM.md
- features.json
- specs/bdd/TRACEABILITY.json
- specs/bdd/BDD_INDEX.json

**Output requirement:** Each deliverable you write MUST include an `## Inputs` section listing the canonical docs (by path) that you used.

## Deliverables
- **ARCHITECTURE.md** *or* **ARCHITECTURE.patch.json** (REQUIRED) → promotes to `docs/engineering/ARCHITECTURE.md`
  - patch format: JSON `DOC_PATCH` (see .claude/docs/PUBLISHING.md#doc-patches)
  - must include tokens/headings: Inputs, Overview, Components, Trade-offs, Observability, Security
- **API.md** *or* **API.patch.json** (REQUIRED) → promotes to `docs/engineering/API.md`
  - patch format: JSON `DOC_PATCH` (see .claude/docs/PUBLISHING.md#doc-patches)
  - must include tokens/headings: Inputs, Authentication, Endpoints, Errors, Examples
- **DATA_MODEL.md** *or* **DATA_MODEL.patch.json** (REQUIRED) → promotes to `docs/engineering/DATA_MODEL.md`
  - patch format: JSON `DOC_PATCH` (see .claude/docs/PUBLISHING.md#doc-patches)
  - must include tokens/headings: Inputs, Entities, Relations, Migrations
- **RISK_REGISTER.md** *or* **RISK_REGISTER.patch.json** (REQUIRED) → promotes to `docs/engineering/RISK_REGISTER.md`
  - patch format: JSON `DOC_PATCH` (see .claude/docs/PUBLISHING.md#doc-patches)
  - must include tokens/headings: Inputs, Risk, Likelihood, Impact, Mitigation
- **ADR-*.md** (optional) → promotes into `docs/adr/`
  - placement: Put matching files under deliverables/ (recommended). publish may also detect deliverables/bdd/ and deliverables/specs/bdd/ for .feature files.
- **THREAT_MODEL.md** *or* **THREAT_MODEL.patch.json** (optional) → promotes to `docs/engineering/THREAT_MODEL.md`
  - patch format: JSON `DOC_PATCH` (see .claude/docs/PUBLISHING.md#doc-patches)
  - must include tokens/headings: Inputs, Assets, Trust boundaries, Entry points, Threats, Mitigations, Verification
- **SECURITY_REVIEW.md** *or* **SECURITY_REVIEW.patch.json** (optional) → promotes to `docs/engineering/SECURITY_REVIEW.md`
  - patch format: JSON `DOC_PATCH` (see .claude/docs/PUBLISHING.md#doc-patches)
  - must include tokens/headings: Inputs, Auth, Input validation, Secrets, Abuse cases, Recommendations
- **OPERABILITY.md** *or* **OPERABILITY.patch.json** (optional) → promotes to `docs/engineering/OPERABILITY.md`
  - patch format: JSON `DOC_PATCH` (see .claude/docs/PUBLISHING.md#doc-patches)
  - must include tokens/headings: Inputs, SLO, SLI, Alerting, Runbook, Backups, Deployment

## Required `## Inputs` references for ARCHITECTURE.md (validation will fail without these)
- `docs/product/REQUIREMENTS_BASELINE.md`
- `docs/product/MARKET_BENCHMARK.md`
- `docs/product/STORY_MAP.md`
- `features.json`
- `specs/bdd/TRACEABILITY.json`
- `specs/bdd/BDD_INDEX.json`
- `docs/ux/UX_CONTRACT.md`
- `docs/ux/DESIGN_SYSTEM.md`

## Feature tagging requirement
- Tag architecture sections with `@F###` markers for each feature.
- This enables feature-scoped extraction by downstream agents.
