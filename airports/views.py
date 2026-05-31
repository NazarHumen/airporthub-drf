from rest_framework import viewsets
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)

from airports.filters import FlightFilter
from airports.models import Airline, Airplane, Airport, Country, Flight
from airports.serializers import (
    AirlineSerializer,
    AirplaneSerializer,
    AirportSerializer,
    CountrySerializer,
    FlightSerializer,
)


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.select_related("country")
    serializer_class = AirportSerializer


class AirlineViewSet(viewsets.ModelViewSet):
    queryset = Airline.objects.select_related("country").prefetch_related(
        "airports"
    )
    serializer_class = AirlineSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airline")
    serializer_class = AirplaneSerializer


class FlightListCreateView(ListCreateAPIView):
    queryset = Flight.objects.select_related(
        "airplane", "departure_airport", "arrival_airport"
    )
    serializer_class = FlightSerializer
    filterset_class = FlightFilter


class FlightDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Flight.objects.select_related(
        "airplane", "departure_airport", "arrival_airport"
    )
    serializer_class = FlightSerializer
