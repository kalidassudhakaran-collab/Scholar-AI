@echo off
cd /d "%~dp0..\backend"
if not exist ".venv\Scripts\pip.exe" (
  echo Run setup-local.cmd from the project root first.
  pause
  exit /b 1
)
echo Installing Whisper + bundled ffmpeg...
call .venv\Scripts\pip install openai-whisper imageio-ffmpeg
echo.
echo Done. Close and reopen run.cmd, then upload samples\voice-test.mp3
pause
