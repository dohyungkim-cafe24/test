# UI baselines (visual regression)

This directory is optional.

If you maintain stable baseline screenshots, this workspace can run deterministic visual regression checks by comparing:
- **baseline images** in `docs/ux/baselines/images/`
vs
- **candidate screenshots** captured during a tester attempt

The comparison is executed by:

```bash
python3 .claude/scripts/visual_regression.py \
  --baselines-dir "projects/<p>/docs/ux/baselines/images" \
  --screenshots-dir "<attempt_dir>/evidence/browser/screenshots" \
  --out-json "<attempt_dir>/deliverables/VISUAL_REGRESSION.json" \
  --out-md "<attempt_dir>/deliverables/VISUAL_REGRESSION.md"
```

## Naming convention (recommended)

Use stable filenames that correspond to user-visible screens:

- `home_desktop.png`
- `settings_desktop.png`
- `checkout_step1_desktop.png`
- `checkout_step1_mobile.png`

During testing, save candidate screenshots using the **same filenames**.
`visual_regression.py` matches candidate images by relative path/name.

## When to update baselines

Update baselines only when:
- the UI change is intentional and approved, and
- UX_JUDGE has signed off on the visual change

Otherwise, treat any diff as a regression to be fixed.

## Scope control

If you do not want visual regression enforced for a UI feature, set:

```json
{ "requires_visual_regression": false }
```

If you want to disable browser runtime gating for a UI feature (not recommended), set:

```json
{ "requires_browser_runtime": false }
```
