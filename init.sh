#!/usr/bin/env bash
set -euo pipefail

echo "=== init.sh (template) ==="
echo "NOTE: add your stack-specific startup command here."
echo "Recommended: start backend + frontend and provide health checks."

# Example placeholders:
# - backend: uvicorn app.main:app --port 8000 --reload &
# - frontend: npm run dev -- --port 3000 &
# - health: curl -f http://localhost:8000/health
