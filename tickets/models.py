from datetime import timedelta

from django.db import models

from airports.models import Flight
from config import settings

RESERVATION_TTL = timedelta(minutes=15)


class Ticket(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"
        USED = "used", "Used"

    flight = models.ForeignKey(
        Flight,
        on_delete=models.PROTECT,
        related_name="tickets",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="tickets",
    )
    seat_number = models.CharField(max_length=4)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    reserved_until = models.DateTimeField(null=True, blank=True)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-purchased_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["flight", "seat_number"],
                condition=~models.Q(status="cancelled"),
                name="uniq_active_seat_per_flight",
            ),
        ]

    def __str__(self):
        return (
            f"Ticket #{self.id}: "
            f"{self.user.email} - "
            f"{self.flight.flight_number}"
        )
