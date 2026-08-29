from django.urls import path

from .views import VoiceRunView

urlpatterns = [
    path("run/", VoiceRunView.as_view(), name="voice-run"),
]
