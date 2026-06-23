from django.db import IntegrityError, models, transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from airports.models import Flight
from orders.models import PAYMENT_TTL, Order
from tickets.models import Ticket


def _cancel_order(order):
    """Cancel an order and release its seats."""
    order.tickets.exclude(status=Ticket.Status.CANCELLED).update(
        status=Ticket.Status.CANCELLED
    )
    order.status = Order.Status.CANCELLED
    order.reserved_until = None
    order.save(update_fields=["status", "reserved_until"])


def _taken_seats(items):
    """Active (non-cancelled) tickets among the requested flight/seat pairs."""
    seat_filter = models.Q()
    for item in items:
        seat_filter |= models.Q(
            flight=item["flight"],
            seat_number=item["seat_number"],
        )
    if not seat_filter:
        return []
    return [
        {"flight": flight_id, "seat_number": seat_number}
        for flight_id, seat_number in Ticket.objects.filter(seat_filter)
        .exclude(status=Ticket.Status.CANCELLED)
        .order_by("flight_id", "seat_number")
        .values_list("flight_id", "seat_number")
    ]


def _release_expired(items):
    """Lazy expiry: cancel expired pending orders
    holding the requested seats."""
    now = timezone.now()
    seat_filter = models.Q()
    for item in items:
        seat_filter |= models.Q(
            tickets__flight=item["flight"],
            tickets__seat_number=item["seat_number"],
        )
    expired_ids = list(
        Order.objects.filter(
            seat_filter,
            status=Order.Status.PENDING,
            reserved_until__lt=now,
        )
        .values_list("id", flat=True)
        .distinct()
    )
    for order in Order.objects.filter(id__in=expired_ids).select_for_update():
        _cancel_order(order)


def reserve_order(user, items):
    """Reserve all requested seats as a single pending order."""
    with transaction.atomic():
        _release_expired(items)
        taken = _taken_seats(items)
        if taken:
            raise ValidationError({"taken_seats": taken})
        order = Order.objects.create(
            user=user,
            status=Order.Status.PENDING,
            total_price=sum(item["flight"].base_price for item in items),
            reserved_until=timezone.now() + PAYMENT_TTL,
        )
        tickets = [
            Ticket(
                order=order,
                flight=item["flight"],
                user=user,
                seat_number=item["seat_number"],
                price=item["flight"].base_price,
                status=Ticket.Status.PENDING,
            )
            for item in items
        ]
        try:
            Ticket.objects.bulk_create(tickets)
        except IntegrityError:
            taken = _taken_seats(items)
            raise ValidationError({"taken_seats": taken})
        return order


def pay_order(order):
    """Pay for a pending order: pending - paid (cascades to tickets)."""
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)
        if order.status != Order.Status.PENDING:
            raise ValidationError(
                f"Order cannot be paid from status '{order.status}'."
            )
        if order.reserved_until and order.reserved_until < timezone.now():
            _cancel_order(order)
            raise ValidationError(
                "Reservation has expired, please book again."
            )
        flights = {
            ticket.flight for ticket in order.tickets.select_related("flight")
        }
        if any(flight.status != Flight.Status.SCHEDULED for flight in flights):
            raise ValidationError("A flight is no longer open for purchase.")
        order.tickets.exclude(status=Ticket.Status.CANCELLED).update(
            status=Ticket.Status.PAID
        )
        order.status = Order.Status.PAID
        order.paid_at = timezone.now()
        order.reserved_until = None
        order.save(update_fields=["status", "paid_at", "reserved_until"])
        return order


def cancel_order(order):
    """Cancel an order and release its seats: pending/paid - cancelled."""
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)
        if order.status not in (
            Order.Status.PENDING,
            Order.Status.PAID,
        ):
            raise ValidationError(
                f"Order in status '{order.status}' cannot be cancelled."
            )
        _cancel_order(order)
        return order


def release_expired_orders():
    """Backup to lazy expiry: cancel every pending order past its deadline."""
    now = timezone.now()
    expired_ids = list(
        Order.objects.filter(
            status=Order.Status.PENDING,
            reserved_until__lt=now,
        ).values_list("id", flat=True)
    )
    released = 0
    for order_id in expired_ids:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(pk=order_id)
            if order.status != Order.Status.PENDING:
                continue
            _cancel_order(order)
            released += 1
    return released
