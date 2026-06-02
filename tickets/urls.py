from django.urls import include, path
from rest_framework.routers import DefaultRouter

from tickets.views import TicketViewSet

app_name = "tickets"

router = DefaultRouter()
router.register("tickets", TicketViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
