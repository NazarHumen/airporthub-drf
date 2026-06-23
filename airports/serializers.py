import re

from rest_framework import serializers

from airports.models import Airline, Airplane, Airport, Country, Flight

CODE_RE = re.compile(r"^[A-Z]+$")


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name", "code"]

    def validate_code(self, value):
        if not CODE_RE.fullmatch(value):
            raise serializers.ValidationError(
                "Country code must contain only uppercase letters (e.g. UA)."
            )
        return value


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ["id", "name", "code", "city", "country"]

    def validate_code(self, value):
        if not CODE_RE.fullmatch(value):
            raise serializers.ValidationError(
                "Airport code must contain only uppercase letters (e.g. KBP)."
            )
        return value


class AirlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airline
        fields = ["id", "name", "code", "country", "airports"]

    def validate_code(self, value):
        if not CODE_RE.fullmatch(value):
            raise serializers.ValidationError(
                "Airline code must contain only uppercase letters (e.g. PS)."
            )
        return value


class AirplaneSerializer(serializers.ModelSerializer):
    capacity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Airplane
        fields = [
            "id",
            "model",
            "registration_number",
            "rows",
            "seats_per_row",
            "capacity",
            "airline",
        ]

    def validate_rows(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Rows must be greater than zero."
            )
        return value

    def validate_seats_per_row(self, value):
        if not 2 <= value <= 6:
            raise serializers.ValidationError(
                "Seats per row must be between 2 and 6."
            )
        return value


class FlightSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = [
            "id",
            "flight_number",
            "airplane",
            "departure_airport",
            "arrival_airport",
            "departure_time",
            "arrival_time",
            "duration",
            "status",
            "base_price",
        ]

    def get_duration(self, flight) -> str:
        # flight duration as "H:MM"
        total_minutes = int(
            (flight.arrival_time - flight.departure_time).total_seconds() // 60
        )
        hours, minutes = divmod(total_minutes, 60)
        return f"{hours}:{minutes:02d}"

    def validate_base_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "base_price must be greater than zero."
            )
        return value

    def validate_status(self, value):
        if self.instance is None and value != Flight.Status.SCHEDULED:
            raise serializers.ValidationError(
                "New flight must have status 'scheduled'."
            )
        return value

    def validate(self, attrs):
        instance = self.instance
        departure = attrs.get(
            "departure_time", getattr(instance, "departure_time", None)
        )
        arrival = attrs.get(
            "arrival_time", getattr(instance, "arrival_time", None)
        )
        if departure and arrival and arrival <= departure:
            raise serializers.ValidationError(
                "arrival_time must be later than departure_time."
            )

        departure_airport = attrs.get(
            "departure_airport",
            getattr(instance, "departure_airport", None),
        )
        arrival_airport = attrs.get(
            "arrival_airport",
            getattr(instance, "arrival_airport", None),
        )
        if (
            departure_airport
            and arrival_airport
            and departure_airport == arrival_airport
        ):
            raise serializers.ValidationError(
                "departure_airport and arrival_airport must be different."
            )
        return attrs


class FlightTakenSeatsSerializer(serializers.Serializer):
    flight = serializers.IntegerField(read_only=True)
    rows = serializers.IntegerField(read_only=True)
    seats_per_row = serializers.IntegerField(read_only=True)
    seat_letters = serializers.CharField(read_only=True)
    taken_seats = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
    )


class FlightListSerializer(serializers.ModelSerializer):
    airplane = serializers.StringRelatedField()
    departure_airport = serializers.SlugRelatedField(
        slug_field="code", read_only=True
    )
    arrival_airport = serializers.SlugRelatedField(
        slug_field="code", read_only=True
    )
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = [
            "id",
            "flight_number",
            "airplane",
            "departure_airport",
            "arrival_airport",
            "departure_time",
            "duration",
            "status",
        ]

    def get_duration(self, flight) -> str:
        # flight duration as "H:MM"
        total_minutes = int(
            (flight.arrival_time - flight.departure_time).total_seconds() // 60
        )
        hours, minutes = divmod(total_minutes, 60)
        return f"{hours}:{minutes:02d}"
