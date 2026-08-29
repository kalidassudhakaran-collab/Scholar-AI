"""
Local development without Docker, PostgreSQL, or Redis.

Uses SQLite, in-memory cache/channels, and synchronous Celery (no worker process).
Set: DJANGO_SETTINGS_MODULE=config.settings.local
"""

import os

from .base import *  # noqa: F403

DEBUG = True

# Add API key here in .env as DJANGO_SECRET_KEY when deploying.
# This placeholder is only for local SQLite runs.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or "add-api-key-here"

# Local dev: no API rate limits (avoids "throttled" after testing features)
REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # noqa: F405
    "DEFAULT_THROTTLE_CLASSES": [],
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# SQLite — no PostgreSQL required
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# No Redis — local memory cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# WebSockets in-process (single server; fine for local dev)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

# Run Celery tasks in-process — no separate worker; return HTTP 202 immediately
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_EAGER_ASYNC = True
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"

# Local file uploads
USE_S3 = False
MEDIA_ROOT = BASE_DIR / "media"  # noqa: F405
MEDIA_URL = "/media/"
