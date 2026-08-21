@echo off
echo ==================================================
echo UnderwriteAI - Launching Enterprise Suite
echo ==================================================

python scripts\verify_environment.py
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%

echo.
echo Starting Streamlit UI on http://localhost:8501 ...
python -m streamlit run frontend\app.py --server.port 8501 --theme.base light
