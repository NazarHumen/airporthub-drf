import django_filters

from airports.models import Flight


class FlightFilter(django_filters.FilterSet):
    origin = django_filters.CharFilter(
        field_name="departure_airport__code", lookup_expr="iexact"
    )
    destination = django_filters.CharFilter(
        field_name="arrival_airport__code", lookup_expr="iexact"
    )
    date = django_filters.DateFilter(
        field_name="departure_time", lookup_expr="date"
    )
    departure_after = django_filters.DateTimeFilter(
        field_name="departure_time", lookup_expr="gte"
    )
    departure_before = django_filters.DateTimeFilter(
        field_name="departure_time", lookup_expr="lte"
    )
    min_price = django_filters.NumberFilter(
        field_name="base_price", lookup_expr="gte"
    )
    max_price = django_filters.NumberFilter(
        field_name="base_price", lookup_expr="lte"
    )

    class Meta:
        model = Flight
        fields = ["status"]
