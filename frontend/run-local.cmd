@echo off
cd /d "%~dp0"
set "NEXT_PUBLIC_API_URL=http://localhost:8000"
set "NEXT_PUBLIC_WS_URL=ws://localhost:8000"
if exist "C:\Program Files\nodejs\npm.cmd" (
  call "C:\Program Files\nodejs\npm.cmd" run dev
) else (
  npm run dev
)
pause
