from django.urls import path

from .views import AiDetectionRunView

urlpatterns = [
    path("run/", AiDetectionRunView.as_view(), name="ai-detection-run"),
]
