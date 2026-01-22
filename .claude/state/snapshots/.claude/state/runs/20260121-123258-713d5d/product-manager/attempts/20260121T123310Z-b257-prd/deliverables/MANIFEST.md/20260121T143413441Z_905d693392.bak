# Deliverables Manifest

- stage: **discover**
- agent: **product-manager**
- contract_version: **1.6.8**
- write_once: **False**

## Golden rules
- Write all artifacts into this attempt's `deliverables/` directory.
- You **may** revise deliverables in-place within this attempt (preferred for small fixes).
- Do **not** edit `MANIFEST.md` / `MANIFEST.json` (the contract for this attempt).
- Do **not** edit canonical docs directly (`docs/**`, `specs/**`, `features.json`, `plan.md`, `plan.json`).

## Inputs to read (non-negotiable)
- source: **stage_inputs**
- docs/DOC_CONTRACT.md
- (user prompt: captured in run context)

**Output requirement:** Each deliverable you write MUST include an `## Inputs` section listing the canonical docs (by path) that you used.

## Deliverables
- **PRD.md** *or* **PRD.patch.json** (REQUIRED) → promotes to `docs/product/PRD.md`
  - patch format: JSON `DOC_PATCH` (see .claude/docs/PUBLISHING.md#doc-patches)
  - must include tokens/headings: Inputs, Problem, Goals, Non-goals, Success, Success metrics, Scope, Risks, Open questions
- **STORY_MAP.md** *or* **STORY_MAP.patch.json** (REQUIRED) → promotes to `docs/product/STORY_MAP.md`
  - patch format: JSON `DOC_PATCH` (see .claude/docs/PUBLISHING.md#doc-patches)
  - must include tokens/headings: Inputs, Vision, Backbone, Launch, US-, P0, P1, P2
- **REQUIREMENTS_BASELINE.md** *or* **REQUIREMENTS_BASELINE.patch.json** (REQUIRED) → promotes to `docs/product/REQUIREMENTS_BASELINE.md`
  - patch format: JSON `DOC_PATCH` (see .claude/docs/PUBLISHING.md#doc-patches)
  - must include tokens/headings: Inputs, Raw input, Interpretation, In scope, Out of scope, Non-negotiables, Quality bar, Assumptions
- **MARKET_BENCHMARK.md** *or* **MARKET_BENCHMARK.patch.json** (REQUIRED) → promotes to `docs/product/MARKET_BENCHMARK.md`
  - patch format: JSON `DOC_PATCH` (see .claude/docs/PUBLISHING.md#doc-patches)
  - must include tokens/headings: Inputs, Comparable products, Feature parity and gaps, Quality bar, Sources

## REQUIREMENTS_BASELINE.md — Quality bar requirements (non-negotiable)
The `## Quality bar` section MUST explicitly address ALL of these topics:
- **Testing**: test requirements, coverage expectations
- **Security**: authentication, authorization, data protection
- **Performance**: latency, throughput, resource constraints
- **UX**: usability standards, design compliance

Example:
```markdown
## Quality bar
- **Testing**: Unit test coverage ≥80%, E2E tests for all critical paths
- **Security**: OAuth 2.0 authentication, input validation, XSS prevention
- **Performance**: Page load <2s, API response <200ms p95
- **UX**: Consistent with Material Design 3, responsive design
```

## MARKET_BENCHMARK.md — Required sections (non-negotiable)
- `## Sources`: at least 3 URLs to comparable products/services
- `## Feature parity and gaps`: at least 3 list items (bullets or numbered)
- `## Quality bar`: at least 5 list items (bullets or numbered) covering market expectations
