from django.urls import path

from .views import PlagiarismRunView

urlpatterns = [
    path("run/", PlagiarismRunView.as_view(), name="plagiarism-run"),
]
