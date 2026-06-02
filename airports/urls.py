from django.urls import include, path
from rest_framework.routers import DefaultRouter

from airports.views import (
    AirlineViewSet,
    AirplaneViewSet,
    AirportViewSet,
    CountryViewSet,
    FlightDetailView,
    FlightListCreateView,
)

app_name = "airports"

router = DefaultRouter()
router.register("countries", CountryViewSet)
router.register("airports", AirportViewSet)
router.register("airlines", AirlineViewSet)
router.register("airplanes", AirplaneViewSet)

urlpatterns = [
    path("flights/", FlightListCreateView.as_view(), name="flight-list"),
    path(
        "flights/<int:pk>/",
        FlightDetailView.as_view(),
        name="flight-detail",
    ),
    path("", include(router.urls)),
]
