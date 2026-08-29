from django.urls import path

from .views import HumanizeView

urlpatterns = [
    path("run/", HumanizeView.as_view(), name="humanizer-run"),
]
