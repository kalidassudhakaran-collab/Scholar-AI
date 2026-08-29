from django.urls import path

from .views import ParaphraseView, ParaphraserStylesView

urlpatterns = [
    path("run/", ParaphraseView.as_view(), name="paraphraser-run"),
    path("styles/", ParaphraserStylesView.as_view(), name="paraphraser-styles"),
]
