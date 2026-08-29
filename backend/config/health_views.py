from django.http import JsonResponse
from django.views import View


class HealthView(View):
    """Lightweight ping — no auth required."""

    def get(self, request):
        return JsonResponse({"status": "ok"})
