from django.urls import path

from .views import TranslateView, TranslatorLanguagesView

urlpatterns = [
    path("run/", TranslateView.as_view(), name="translator-run"),
    path("languages/", TranslatorLanguagesView.as_view(), name="translator-languages"),
]
