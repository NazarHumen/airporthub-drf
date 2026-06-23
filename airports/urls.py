from django.urls import include, path
from rest_framework.routers import DefaultRouter

from airports.views import (
    AirlineViewSet,
    AirplaneViewSet,
    AirportDetailView,
    AirportListCreateView,
    CountryViewSet,
    FlightDetailView,
    FlightListCreateView,
    FlightTakenSeatsView,
)

app_name = "airports"

router = DefaultRouter()
router.register("countries", CountryViewSet)
router.register("airlines", AirlineViewSet)
router.register("airplanes", AirplaneViewSet)

urlpatterns = [
    path("airports/", AirportListCreateView.as_view(), name="airport-list"),
    path(
        "airports/<int:pk>/",
        AirportDetailView.as_view(),
        name="airport-detail",
    ),
    path("flights/", FlightListCreateView.as_view(), name="flight-list"),
    path(
        "flights/<int:pk>/",
        FlightDetailView.as_view(),
        name="flight-detail",
    ),
    path(
        "flights/<int:pk>/taken-seats/",
        FlightTakenSeatsView.as_view(),
        name="flight-taken-seats",
    ),
    path("", include(router.urls)),
]
