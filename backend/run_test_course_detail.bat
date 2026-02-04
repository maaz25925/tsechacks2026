@echo off
REM Test GET /discovery/listings/{listing_id}
cd /d "%~dp0"

echo Testing Course Detail endpoint...
echo.

REM Option 1: Test against in-process app (no server)
uv run python test_course_detail.py

REM Option 2: Test against running server (uncomment and start server first)
REM set BASE_URL=http://localhost:8000
REM uv run python test_course_detail.py

pause
