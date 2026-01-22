# Browser Runtime Preflight

- UTC: 2026-01-21T12:32:18Z
- Project: projects/punch-analytics
- Requires browser runtime: 1 / 1 features

## Platform
| Item | Value |
|---|---|
| OS | Darwin dhkim15-macbook-7.local 24.6.0 Darwin Kernel Version 24.6.0: Mon Jul 14 11:30:29 PDT 2025; root:xnu-11417.140.69~1/RELEASE_ARM64_T6000 arm64 |
| WSL | False |

## Claude Code (CLI)
| Item | Value |
|---|---|
| Found | True |
| Version | 2.1.14 |
| Raw | 2.1.14 (Claude Code) |

## Chrome integration
- Official check: run `/chrome` in Claude Code to verify connection status.

## Playwright (Python)
| Item | Value |
|---|---|
| Installed | False |
| CLI version |  |
| Browsers installed | False |
| Browsers path |  |

## Playwright (Node)
| Item | Value |
|---|---|
| node | True |
| npm | True |
| npx | True |
| playwright dep in package.json | False |
| npx --no-install playwright --version | npm warn Unknown user config "// fe-mcp". This will stop working in the next major version of npm.
npm warn Unknown user config "always-auth". This will stop working in the next major version of npm.
npm error npx canceled due to missing packages and no YES option: ["playwright@1.57.0"]
npm error A complete log of this run can be found in: /Users/briankim/.npm/_logs/2026-01-21T12_32_18_178Z-debug-0.log |

## Recommendations
- Run this preflight early (right after /agi-project switch) to avoid late-stage browser evidence blockers.
- For Chrome-based evidence: start Claude Code with `claude --chrome` (or run `/chrome` in-session) and confirm the extension is connected.
- Avoid enabling Chrome integration by default unless needed; it increases context usage because browser tools stay loaded.
- Playwright (Python) is not installed. Install: `python3 -m pip install playwright` then `python3 -m playwright install chromium`.

## Notes
- If you want deterministic Node/CI usage, add `@playwright/test` (or `playwright`) to devDependencies instead of relying on ad-hoc `npx` downloads.
- Chrome extension connection status must be checked via `/chrome` inside Claude Code (official workflow).

## References
- Claude Code with Chrome (beta): https://code.claude.com/docs/en/chrome
