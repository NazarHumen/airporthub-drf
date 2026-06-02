from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from tickets.models import Ticket
from tickets.serializers import TicketSerializer


@extend_schema(tags=["Tickets"])
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related("flight", "user")
    serializer_class = TicketSerializer
    filterset_fields = ["flight", "user", "status"]
