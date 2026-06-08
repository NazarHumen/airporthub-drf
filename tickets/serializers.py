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
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    status = serializers.CharField(read_only=True)
    reserved_until = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "flight",
            "user",
            "seat_number",
            "price",
            "status",
            "reserved_until",
            "purchased_at",
        ]

    def validate_seat_number(self, value):
        if not SEAT_NUMBER_RE.fullmatch(value):
            raise serializers.ValidationError(
                "Seat number must be 1-3 digits followed by 1 letter "
                "(e.g. 12A)."
            )
        return value.upper()

    def validate(self, attrs):
        instance = self.instance
        if instance is not None and instance.status != Ticket.Status.PENDING:
            locked = [
                field
                for field in ("flight", "seat_number")
                if field in attrs and attrs[field] != getattr(instance, field)
            ]
            if locked:
                raise serializers.ValidationError(
                    f"A '{instance.status}' ticket can no longer be modified."
                )
        flight = attrs.get("flight") or getattr(self.instance, "flight", None)
        seat_number = attrs.get("seat_number") or getattr(
            self.instance, "seat_number", None
        )
        if (
            flight
            and seat_number
            and not flight.airplane.is_valid_seat(seat_number)
        ):
            airplane = flight.airplane
            raise serializers.ValidationError(
                {
                    "seat_number": (
                        f"Seat {seat_number} does not exist on this "
                        f"airplane (rows 1-{airplane.rows}, "
                        f"seats {airplane.seat_letters})."
                    )
                }
            )
        return attrs

    def create(self, validated_data):
        validated_data["price"] = validated_data["flight"].base_price
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Keep price in sync with the flight: changing the flight must
        # re-derive the fare instead of carrying over the old one.
        if "flight" in validated_data:
            validated_data["price"] = validated_data["flight"].base_price
        return super().update(instance, validated_data)
