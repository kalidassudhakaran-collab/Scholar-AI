from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AIHistoryViewSet

router = DefaultRouter()
router.register("", AIHistoryViewSet, basename="history")

urlpatterns = [
    path("", include(router.urls)),
]
