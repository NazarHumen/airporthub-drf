from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from tickets.models import Ticket
from tickets.permissions import IsOwnerOrAdmin
from tickets.serializers import TicketSerializer


@extend_schema(tags=["Tickets"])
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related("flight", "user")
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filterset_fields = ["flight", "user", "status"]

    def get_queryset(self):
        qs = super().get_queryset()
        if getattr(self, "swagger_fake_view", False):
            return qs.none()
        if self.request.user.is_admin:
            return qs
        return qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
