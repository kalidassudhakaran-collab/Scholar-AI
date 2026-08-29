@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
set "DJANGO_SETTINGS_MODULE=config.settings.local"
python manage.py runserver 127.0.0.1:8000
pause
