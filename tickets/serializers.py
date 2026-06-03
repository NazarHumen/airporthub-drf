import re

from rest_framework import serializers

from tickets.models import Ticket

SEAT_NUMBER_RE = re.compile(r"^[0-9]{1,3}[A-Za-z]$")


class TicketSerializer(serializers.ModelSerializer):
    purchased_at = serializers.DateTimeField(
        format="%d.%m.%Y %H:%M:%S",
        read_only=True,
    )

    class Meta:
        model = Ticket
        fields = [
            "id",
            "flight",
            "user",
            "seat_number",
            "price",
            "status",
            "purchased_at",
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than zero."
            )
        return value

    def validate_seat_number(self, value):
        if not SEAT_NUMBER_RE.fullmatch(value):
            raise serializers.ValidationError(
                "Seat number must be 1-3 digits followed by 1 letter "
                "(e.g. 12A)."
            )
        return value.upper()

    def validate_status(self, value):
        if self.instance is None and value != Ticket.Status.PENDING:
            raise serializers.ValidationError(
                "New ticket must have status 'pending'."
            )
        return value
