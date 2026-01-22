# punch-analytics

This is an **AGI Dev Workspace** project directory.

The workspace is designed to run an end-to-end product pipeline (PM → UX → BDD → Architecture → Plan → Build/Test loop → Release) with deterministic gates and publish-only canonical artifacts.

## Where to start

- If you have raw requirements, run autopilot from the **workspace root**:
  - `/agi-autopilot create punch-analytics`

- If you prefer step-by-step:
  1. `/agi-discover`
  2. `/agi-ux`
  3. `/agi-bdd`
  4. `/agi-arch`
  5. `/agi-plan`
  6. `/agi-loop F001`
  7. `/agi-quality`
  8. `/agi-e2e`
  9. `/agi-release`

## Key files

- `docs/DOC_CONTRACT.md`: canonical contract for stage outputs and promotion rules
- `features.json`: backlog + per-feature PASS ledger
- `plan.md`: execution plan (promoted from plan runs)
- `HANDOFF.md`: release handoff (published)

## Operational status

- `status.md`: current high-level status and notes
- `progress.md`: progress tracking

