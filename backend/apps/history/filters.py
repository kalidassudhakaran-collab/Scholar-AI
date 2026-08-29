import django_filters

from .models import AIHistory


class AIHistoryFilter(django_filters.FilterSet):
    feature = django_filters.CharFilter(field_name="feature")
    status = django_filters.CharFilter(field_name="status")
    is_starred = django_filters.BooleanFilter(field_name="is_starred")
    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = AIHistory
        fields = ["feature", "status", "is_starred"]
