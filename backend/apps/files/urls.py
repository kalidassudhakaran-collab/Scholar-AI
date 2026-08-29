from django.urls import path

from .views import FileDetailView, FileListView, FileUploadView

urlpatterns = [
    path("upload/", FileUploadView.as_view(), name="file-upload"),
    path("", FileListView.as_view(), name="file-list"),
    path("<uuid:pk>/", FileDetailView.as_view(), name="file-detail"),
]
