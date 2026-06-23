from django.utils import timezone
from rest_framework import serializers

from airports.models import Flight
from orders.models import Order
from orders.services import reserve_order
from tickets.models import Ticket
from tickets.serializers import SEAT_NUMBER_RE

MAX_SEATS_PER_ORDER = 9


class OrderItemSerializer(serializers.Serializer):
    flight = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.all())
    seat_number = serializers.CharField(max_length=4)

    def validate_seat_number(self, value):
        if not SEAT_NUMBER_RE.fullmatch(value):
            raise serializers.ValidationError(
                "Seat number must be 1-3 digits followed by 1 letter "
                "(e.g. 12A)."
            )
        return value.upper()


class OrderTicketSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Ticket
        fields = ["id", "flight", "seat_number", "price", "status"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)
    tickets = OrderTicketSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    status = serializers.CharField(read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )
    created_at = serializers.DateTimeField(
        format="%d.%m.%Y %H:%M:%S",
        read_only=True,
    )
    paid_at = serializers.DateTimeField(
        format="%d.%m.%Y %H:%M:%S",
        read_only=True,
    )
    reserved_until = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "status",
            "total_price",
            "reserved_until",
            "created_at",
            "paid_at",
            "items",
            "tickets",
        ]

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one seat is required.")
        if len(value) > MAX_SEATS_PER_ORDER:
            raise serializers.ValidationError(
                f"You can book at most {MAX_SEATS_PER_ORDER} seats per order."
            )
        if len({item["flight"].pk for item in value}) > 1:
            raise serializers.ValidationError(
                "All seats in an order must be for the same flight."
            )
        flight = value[0]["flight"]
        if flight.status != Flight.Status.SCHEDULED:
            raise serializers.ValidationError(
                f"Flight {flight.flight_number} is not open for booking "
                f"(status '{flight.status}')."
            )
        if flight.departure_time <= timezone.now():
            raise serializers.ValidationError(
                f"Flight {flight.flight_number} has already departed."
            )
        airplane = flight.airplane
        seen = set()
        for item in value:
            seat_number = item["seat_number"]
            if seat_number in seen:
                raise serializers.ValidationError(
                    f"Seat {seat_number} is listed more than once."
                )
            seen.add(seat_number)
            if not airplane.is_valid_seat(seat_number):
                raise serializers.ValidationError(
                    f"Seat {seat_number} does not exist on this airplane "
                    f"(rows 1-{airplane.rows}, seats {airplane.seat_letters})."
                )
        return value

    def create(self, validated_data):
        return reserve_order(
            self.context["request"].user,
            validated_data["items"],
        )
