@echo off
echo ==================================================
echo UnderwriteAI Enterprise Intelligence Platform
echo ==================================================

python scripts\verify_environment.py
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%

echo.
echo Starting FastAPI Backend on http://localhost:8000 ...
start /B python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo Starting React Enterprise Frontend on http://localhost:5173 ...
cd frontend-react
npm run dev
