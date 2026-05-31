from rest_framework.routers import DefaultRouter

from airports.views import (
    AirlineViewSet,
    AirplaneViewSet,
    AirportViewSet,
    CountryViewSet,
)
from tickets.views import TicketViewSet

router = DefaultRouter()
router.register("countries", CountryViewSet)
router.register("airports", AirportViewSet)
router.register("airlines", AirlineViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("tickets", TicketViewSet)
