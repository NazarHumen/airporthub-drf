from django.db import IntegrityError, transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from airports.models import Flight
from tickets.models import RESERVATION_TTL, Ticket
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

    def save_reservation(self, serializer, **extra):
        flight = serializer.validated_data.get("flight") or (
            serializer.instance.flight
        )
        seat = serializer.validated_data.get("seat_number") or (
            serializer.instance.seat_number
        )
        stale = Ticket.objects.filter(
            flight=flight,
            seat_number=seat,
            status=Ticket.Status.PENDING,
            reserved_until__lt=timezone.now(),
        )
        if serializer.instance is not None:
            stale = stale.exclude(pk=serializer.instance.pk)
        try:
            with transaction.atomic():
                stale.update(status=Ticket.Status.CANCELLED)
                serializer.save(**extra)
        except IntegrityError:
            raise ValidationError(
                {"seat_number": "This seat is already taken."}
            )

    def perform_create(self, serializer):
        self.save_reservation(
            serializer,
            user=self.request.user,
            reserved_until=timezone.now() + RESERVATION_TTL,
        )

    def perform_update(self, serializer):
        self.save_reservation(serializer)

    @extend_schema(request=None, responses=TicketSerializer)
    @action(detail=True, methods=["post"])
    def purchase(self, request, pk=None):
        """Pay for a pending reservation: pending - paid."""
        ticket = self.get_object()
        if ticket.status != Ticket.Status.PENDING:
            raise ValidationError(
                f"Ticket cannot be purchased from status '{ticket.status}'."
            )
        if ticket.reserved_until and ticket.reserved_until < timezone.now():
            ticket.status = Ticket.Status.CANCELLED
            ticket.reserved_until = None
            ticket.save(update_fields=["status", "reserved_until"])
            raise ValidationError(
                "Reservation has expired, please book again."
            )
        if ticket.flight.status != Flight.Status.SCHEDULED:
            raise ValidationError("Flight is no longer open for purchase.")
        ticket.status = Ticket.Status.PAID
        ticket.reserved_until = None
        ticket.save(update_fields=["status", "reserved_until"])
        return Response(self.get_serializer(ticket).data)

    @extend_schema(request=None, responses=TicketSerializer)
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Release a seat: pending/paid - cancelled."""
        ticket = self.get_object()
        if ticket.status not in (
            Ticket.Status.PENDING,
            Ticket.Status.PAID,
        ):
            raise ValidationError(
                f"Ticket in status '{ticket.status}' cannot be cancelled."
            )
        ticket.status = Ticket.Status.CANCELLED
        ticket.reserved_until = None
        ticket.save(update_fields=["status", "reserved_until"])
        return Response(self.get_serializer(ticket).data)
