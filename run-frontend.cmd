@echo off
cd /d "%~dp0frontend"

set "NODE=C:\Program Files\nodejs\node.exe"
set "NPM=C:\Program Files\nodejs\npm.cmd"

if not exist "%NPM%" (
  echo Node.js not found. Install from https://nodejs.org/
  pause
  exit /b 1
)

if not exist "node_modules" (
  echo Installing frontend dependencies...
  call "%NPM%" install
)

echo.
echo  Frontend: http://localhost:3000
echo  ^(Backend must run separately — install Docker and use run.cmd^)
echo.

set NEXT_PUBLIC_API_URL=http://localhost:8000
set NEXT_PUBLIC_WS_URL=ws://localhost:8001
call "%NPM%" run dev

pause
