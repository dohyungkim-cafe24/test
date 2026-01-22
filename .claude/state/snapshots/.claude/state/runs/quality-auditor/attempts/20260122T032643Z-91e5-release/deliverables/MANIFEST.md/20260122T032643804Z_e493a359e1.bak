# Deliverables Manifest

- stage: **release**
- agent: **quality-auditor**
- contract_version: **1.6.8**
- write_once: **False**

## Golden rules
- Write all artifacts into this attempt's `deliverables/` directory.
- You **may** revise deliverables in-place within this attempt (preferred for small fixes).
- Do **not** edit `MANIFEST.md` / `MANIFEST.json` (the contract for this attempt).
- Do **not** edit canonical docs directly (`docs/**`, `specs/**`, `features.json`, `plan.md`, `plan.json`).

## Inputs to read (non-negotiable)
- source: **stage_inputs**
- features.json
- docs/ux/UX_CONTRACT.md
- docs/operations/RUNBOOK.md
- docs/operations/RELEASE_NOTES.md
- (evidence) HANDOFF.md (project root)
- (evidence) QUALITY_AUDIT.md (quality-auditor run)

**Output requirement:** Each deliverable you write MUST include an `## Inputs` section listing the canonical docs (by path) that you used.

## Deliverables
- **QUALITY_AUDIT.md** *or* **QUALITY_AUDIT.patch.json** (optional) → promotes to `docs/release/QUALITY_AUDIT.md`
  - patch format: JSON `DOC_PATCH` (see .claude/docs/PUBLISHING.md#doc-patches)
  - must include tokens/headings: Inputs, Summary, Findings, Actions
- **HANDOFF.md** *or* **HANDOFF.patch.json** (REQUIRED) → promotes to `HANDOFF.md`
  - patch format: JSON `DOC_PATCH` (see .claude/docs/PUBLISHING.md#doc-patches)
  - must include tokens/headings: Inputs, Start, URLs, Test
