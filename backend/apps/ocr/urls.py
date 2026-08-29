from django.urls import path

from .views import OcrRunView

urlpatterns = [
    path("run/", OcrRunView.as_view(), name="ocr-run"),
]
