@echo off
cd /d "%~dp0"

if not exist ".env" copy /Y .env.example .env >nul

if not exist "backend\.venv\Scripts\python.exe" (
  echo First run - installing dependencies, may take a few minutes...
  call setup-local.cmd nopause
  if not exist "backend\.venv\Scripts\python.exe" (
    echo Setup failed. See messages above.
    pause
    exit /b 1
  )
)

echo.
echo  Scholar AI starting...
echo    Open:  http://localhost:8000
echo    API:   http://localhost:8000/api/
echo.
echo  HTML + CSS frontend - no Node.js needed.
echo  Close this window to stop.
echo.

start "" "http://localhost:8000"
call "%~dp0backend\run-local.cmd"
