from rest_framework import viewsets

from tickets.models import Ticket
from tickets.serializers import TicketSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related("flight", "user")
    serializer_class = TicketSerializer
    filterset_fields = ["flight", "user", "status"]
