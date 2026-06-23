import re

from rest_framework import serializers

from tickets.models import Ticket

SEAT_NUMBER_RE = re.compile(r"^[0-9]{1,3}[A-Za-z]$")


class TicketSerializer(serializers.ModelSerializer):
    purchased_at = serializers.DateTimeField(
        format="%d.%m.%Y %H:%M:%S",
        read_only=True,
    )
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Ticket
        fields = [
            "id",
            "order",
            "flight",
            "user",
            "seat_number",
            "price",
            "status",
            "purchased_at",
        ]
        read_only_fields = fields
