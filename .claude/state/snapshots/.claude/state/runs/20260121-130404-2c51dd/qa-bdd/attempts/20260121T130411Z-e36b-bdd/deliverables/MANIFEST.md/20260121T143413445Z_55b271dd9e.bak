# Deliverables Manifest

- stage: **bdd**
- agent: **qa-bdd**
- contract_version: **1.6.8**
- write_once: **False**

## Golden rules
- Write all artifacts into this attempt's `deliverables/` directory.
- You **may** revise deliverables in-place within this attempt (preferred for small fixes).
- Do **not** edit `MANIFEST.md` / `MANIFEST.json` (the contract for this attempt).
- Do **not** edit canonical docs directly (`docs/**`, `specs/**`, `features.json`, `plan.md`, `plan.json`).

## Inputs to read (non-negotiable)
- source: **stage_inputs**
- docs/product/REQUIREMENTS_BASELINE.md
- docs/product/MARKET_BENCHMARK.md
- docs/product/STORY_MAP.md
- (optional) docs/product/USER_STORIES.md
- docs/ux/UX_CONTRACT.md
- docs/ux/DESIGN_SYSTEM.md
- docs/ux/UX_SPEC.md
- docs/ux/IA_MAP.md
- docs/ux/UI_STATES.md
- docs/ux/COPY.md

**Output requirement:** Each deliverable you write MUST include an `## Inputs` section listing the canonical docs (by path) that you used.

## Deliverables
- **features.json** (REQUIRED) → promotes to `features.json`
- **TRACEABILITY.json** (REQUIRED) → promotes to `specs/bdd/TRACEABILITY.json`
- **TRACEABILITY.md** *or* **TRACEABILITY.patch.json** (optional) → promotes to `specs/bdd/TRACEABILITY.md`
  - patch format: JSON `DOC_PATCH` (see .claude/docs/PUBLISHING.md#doc-patches)
  - must include tokens/headings: Inputs, Traceability, US-, @F
- ***.feature** (REQUIRED) → promotes into `specs/bdd/`
  - placement: Put matching files under deliverables/ (recommended). publish may also detect deliverables/bdd/ and deliverables/specs/bdd/ for .feature files.

## BDD & Traceability gate (non-negotiable)
- Every `Scenario` / `Scenario Outline` MUST be tagged with its feature id, e.g. `@F001`.
- Preferred: `TRACEABILITY.json` (deterministic, parseable). `TRACEABILITY.md` may include a fenced ```yaml``` block (JSON-as-YAML accepted) with mapping objects using keys: `feature`, `gherkin_file`, `scenarios` (optional: `user_story`).

**CRITICAL: Feature ID format**
- Use exactly `F` + 3 digits: `F001`, `F002`, `F003`, etc.
- **DO NOT use sub-IDs** like `F001-A`, `F001.1`, `F001a` — these will fail validation.
- If a feature is complex, split it into separate features: `F001`, `F002`, etc.

Required YAML schema (minimal example):
```yaml
traceability:
  - user_story: US-001
    feature: F001
    gherkin_file: auth-login.feature
    scenarios:
      - "Successful login"
```
- All **Launch-scope** user stories (docs/product/STORY_MAP.md##Launch) must be covered via either (a) TRACEABILITY `user_story` mappings or (b) `@US-###` tags in Gherkin.

Example tag pattern:
```gherkin
@F001 @US-001
Scenario: Successful login
  Given ...
```
```
