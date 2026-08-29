from django.urls import path

from .views import YoutubeRunView

urlpatterns = [
    path("run/", YoutubeRunView.as_view(), name="youtube-run"),
]
