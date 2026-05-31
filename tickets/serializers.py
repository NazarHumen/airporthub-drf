from rest_framework import serializers

from tickets.models import Ticket


class TicketSerializer(serializers.ModelSerializer):
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
        read_only_fields = ["purchased_at"]
