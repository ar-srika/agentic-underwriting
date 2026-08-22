#!/usr/bin/env bash
set -e

echo "=================================================="
echo "UnderwriteAI Enterprise Intelligence Platform"
echo "=================================================="

python scripts/verify_environment.py

echo ""
echo "Starting FastAPI Backend on http://localhost:8000 ..."
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &

echo ""
echo "Starting React Enterprise Frontend on http://localhost:5173 ..."
cd frontend-react && npm run dev
