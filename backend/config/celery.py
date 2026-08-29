import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("scholar_ai")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.task_routes = {
    "apps.ai_tasks.tasks.*": {"queue": "ai"},
    "apps.files.*": {"queue": "files"},
}
