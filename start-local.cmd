@echo off
cd /d "%~dp0"

if not exist "backend\.venv\Scripts\python.exe" (
  echo Run setup-local.cmd first.
  pause
  exit /b 1
)

if not exist ".env" copy /Y .env.example .env >nul

echo Starting Scholar AI - no Docker...
echo   Frontend: http://localhost:3000
echo   API:      http://localhost:8000/api/
echo.
echo Close the two windows to stop.
echo.

start "Scholar AI - Backend" cmd /k "%~dp0backend\run-local.cmd"

timeout /t 3 /nobreak >nul

start "Scholar AI - Frontend" cmd /k "%~dp0frontend\run-local.cmd"

echo Started backend and frontend in separate windows.
pause
