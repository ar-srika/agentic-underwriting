@echo off
echo ==================================================
echo UnderwriteAI Enterprise Intelligence Platform
echo ==================================================

:: Clean up any leftover processes listening on port 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1

python scripts\verify_environment.py
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%

echo.
echo Starting FastAPI Backend on http://localhost:8000 ...
start /B python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

echo.
echo Starting React Enterprise Frontend on http://localhost:5173 ...
cd frontend-react
npm run dev


