@echo off
REM Run Supabase health check test (Windows)

cd /d "%~dp0"

echo Running Supabase health check...
echo.

REM Try uv first, fallback to python
where uv >nul 2>&1
if %ERRORLEVEL% == 0 (
    uv run test_supabase.py
) else (
    python test_supabase.py
)

pause
