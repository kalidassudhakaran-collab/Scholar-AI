from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.conf.urls.static import static

from apps.accounts.forms import ScholarAdminAuthenticationForm
from .health_views import HealthView
from .web_views import serve_css, serve_js, serve_page

admin.site.login_form = ScholarAdminAuthenticationForm

urlpatterns = [
    path("", serve_page, {"page": "index.html"}, name="web-home"),
    path("login.html", serve_page, {"page": "login.html"}),
    path("register.html", serve_page, {"page": "register.html"}),
    path("app.html", serve_page, {"page": "app.html"}),
    path("dashboard.html", serve_page, {"page": "dashboard.html"}),
    re_path(r"^css/(?P<filepath>.*)$", serve_css),
    re_path(r"^js/(?P<filepath>.*)$", serve_js),
    path("admin/", admin.site.urls),
    path("api/health/", HealthView.as_view(), name="health"),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/files/", include("apps.files.urls")),
    path("api/history/", include("apps.history.urls")),
    path("api/feedback/", include("apps.feedback.urls")),
    path("api/summarizer/", include("apps.summarizer.urls")),
    path("api/translator/", include("apps.translator.urls")),
    path("api/paraphraser/", include("apps.paraphraser.urls")),
    path("api/humanizer/", include("apps.humanizer.urls")),
    path("api/plagiarism/", include("apps.plagiarism.urls")),
    path("api/ai-detection/", include("apps.ai_detection.urls")),
    path("api/ocr/", include("apps.ocr.urls")),
    path("api/voice/", include("apps.voice.urls")),
    path("api/youtube/", include("apps.youtube.urls")),
    path("api/tasks/", include("apps.ai_tasks.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
