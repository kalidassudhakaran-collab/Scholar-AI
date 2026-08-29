from django.urls import path

from .views import SummarizeView, SummarizerOptionsView

urlpatterns = [
    path("run/", SummarizeView.as_view(), name="summarizer-run"),
    path("options/", SummarizerOptionsView.as_view(), name="summarizer-options"),
]
