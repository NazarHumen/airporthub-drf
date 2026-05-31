from rest_framework import serializers

from airports.models import Airline, Airplane, Airport, Country, Flight


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name", "code"]


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ["id", "name", "code", "city", "country"]


class AirlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airline
        fields = ["id", "name", "code", "country", "airports"]


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ["id", "model", "registration_number", "capacity", "airline"]


class FlightSerializer(serializers.ModelSerializer):
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
            "status",
            "base_price",
        ]

    def validate(self, attrs):
        departure = attrs.get("departure_time")
        arrival = attrs.get("arrival_time")
        if departure and arrival and arrival <= departure:
            raise serializers.ValidationError(
                "arrival_time must be later than departure_time."
            )
        return attrs
