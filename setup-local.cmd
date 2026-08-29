@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo ========================================
echo  Scholar AI - Local setup - no Docker
echo ========================================
echo.

REM Find Python (PATH or common install folders)
set "PY="
for %%P in (py python python3) do (
  if not defined PY (
    where %%P >nul 2>&1
    if !ERRORLEVEL!==0 set "PY=%%P"
  )
)
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
  set "PY=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
)
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
  set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
)
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
  set "PY=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
)

if not defined PY (
  echo Python 3.10+ was not found.
  echo Install from https://www.python.org/downloads/
  echo Check "Add python.exe to PATH" during install, then run this again.
  pause
  exit /b 1
)

echo Tip: Add Python to PATH permanently:
echo   %LOCALAPPDATA%\Programs\Python\Python313
echo   %LOCALAPPDATA%\Programs\Python\Python313\Scripts
echo.

echo Using: %PY%
%PY% --version
echo.

if not exist ".env" copy /Y .env.example .env >nul

REM Backend venv
cd backend
if not exist ".venv" (
  echo Creating virtual environment...
  %PY% -m venv .venv 2>nul
  if not exist ".venv\Scripts\python.exe" (
    echo venv module missing - using virtualenv...
    %PY% -m pip install virtualenv -q
    %PY% -m virtualenv .venv
  )
)

call .venv\Scripts\activate.bat
echo Installing Python packages - lightweight, no GPU...
python -m pip install --upgrade pip
pip install -r requirements-local.txt

set "DJANGO_SETTINGS_MODULE=config.settings.local"
echo Running database migrations...
python manage.py migrate

cd ..

echo Frontend: plain HTML in /web folder - served by Django, no npm required.

echo.
echo ========================================
echo  Setup complete.
echo ========================================
if /i "%~1"=="nopause" exit /b 0
pause
