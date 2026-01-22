# Deliverables Manifest

- stage: **ux**
- agent: **ux-designer**
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
- docs/product/PRD.md
- (optional) docs/product/PERSONAS.md
- (optional) docs/product/USER_STORIES.md
- (optional) docs/ux/INSIGHTS.md
- (optional) docs/ux/RISKS_AND_ASSUMPTIONS.md

**Output requirement:** Each deliverable you write MUST include an `## Inputs` section listing the canonical docs (by path) that you used.

## Deliverables
- **DESIGN_SYSTEM.md** *or* **DESIGN_SYSTEM.patch.json** (REQUIRED) → promotes to `docs/ux/DESIGN_SYSTEM.md`
  - patch format: JSON `DOC_PATCH` (see .claude/docs/PUBLISHING.md#doc-patches)
  - must include tokens/headings: Inputs, Material, Design tokens, Theme, Color roles, Typography, Components
- **design_tokens.json** (REQUIRED) → promotes to `docs/ux/design_tokens.json`
- **UX_CONTRACT.md** *or* **UX_CONTRACT.patch.json** (REQUIRED) → promotes to `docs/ux/UX_CONTRACT.md`
  - patch format: JSON `DOC_PATCH` (see .claude/docs/PUBLISHING.md#doc-patches)
  - must include tokens/headings: Inputs, Scope, Competitive bar, Non-negotiables, Quality bar, Performance, Heuristic acceptance criteria, Evidence, Change control
- **UI_STATES.md** *or* **UI_STATES.patch.json** (REQUIRED) → promotes to `docs/ux/UI_STATES.md`
  - patch format: JSON `DOC_PATCH` (see .claude/docs/PUBLISHING.md#doc-patches)
  - must include tokens/headings: Inputs, Loading, Empty, Error, Validation, Success
- **UX_SPEC.md** *or* **UX_SPEC.patch.json** (REQUIRED) → promotes to `docs/ux/UX_SPEC.md`
  - patch format: JSON `DOC_PATCH` (see .claude/docs/PUBLISHING.md#doc-patches)
  - must include tokens/headings: Inputs, Scope, Entry points, Primary flows, Edge cases, Screens & routes, Components, UI states, Instrumentation, Validation plan, Open questions
- **IA_MAP.md** *or* **IA_MAP.patch.json** (REQUIRED) → promotes to `docs/ux/IA_MAP.md`
  - patch format: JSON `DOC_PATCH` (see .claude/docs/PUBLISHING.md#doc-patches)
  - must include tokens/headings: Inputs, Sitemap, Routes, Key flows, Notes
- **COPY.md** *or* **COPY.patch.json** (REQUIRED) → promotes to `docs/ux/COPY.md`
  - patch format: JSON `DOC_PATCH` (see .claude/docs/PUBLISHING.md#doc-patches)
  - must include tokens/headings: Inputs, Tone & voice, UI copy, Error messages, Glossary
- **UX_REPORT.md** *or* **UX_REPORT.patch.json** (REQUIRED) → promotes to `docs/ux/UX_REPORT.md`
  - patch format: JSON `DOC_PATCH` (see .claude/docs/PUBLISHING.md#doc-patches)
  - must include tokens/headings: Inputs, Summary, Decisions, Open questions

## UI/UX style constraint
- This project uses a **Material Design 3** design system. Ensure `DESIGN_SYSTEM.md` explicitly documents Material tokens/components and theming rules.

## Placeholder ban (non-negotiable)
- **DO NOT** leave `TODO`, `TBD`, `PLACEHOLDER`, `FIXME`, or `{{...}}` anywhere in deliverables.
- IMPORTANT: the scan is literal. Do not include these strings even in meta-statements (e.g., avoid writing "no TBD" or "remove TODOs"). Rephrase instead.
- This includes `UI_STATES.md` — every state must be fully specified.
- If uncertain, propose a concrete default instead of a placeholder.

## Required `## Inputs` references (validation will fail without these)
- `UX_SPEC.md` must reference: `docs/product/PRD.md`, `docs/product/REQUIREMENTS_BASELINE.md`, `docs/product/MARKET_BENCHMARK.md`, `docs/product/STORY_MAP.md`, `docs/ux/UX_CONTRACT.md`, `docs/ux/DESIGN_SYSTEM.md`
- `UX_REPORT.md` must reference (at minimum): `docs/product/REQUIREMENTS_BASELINE.md`, `docs/product/MARKET_BENCHMARK.md`, `docs/product/STORY_MAP.md`, `docs/ux/UX_CONTRACT.md`, `docs/ux/DESIGN_SYSTEM.md`, `docs/ux/UX_SPEC.md`, `docs/ux/UI_STATES.md`, `docs/ux/IA_MAP.md`, `docs/ux/COPY.md`
