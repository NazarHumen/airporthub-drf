from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from airports.filters import FlightFilter
from airports.models import Airline, Airplane, Airport, Country, Flight
from airports.permissions import IsAdminRoleOrReadOnly
from airports.serializers import (
    AirlineSerializer,
    AirplaneSerializer,
    AirportSerializer,
    CountrySerializer,
    FlightListSerializer,
    FlightSerializer,
    FlightTakenSeatsSerializer,
)
from tickets.models import Ticket
from tools.pagination import CustomPageNumberPagination


@extend_schema(tags=["Geography"])
class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAdminRoleOrReadOnly]


@extend_schema(tags=["Airports"])
class AirportListCreateView(APIView):
    permission_classes = [IsAdminRoleOrReadOnly]
    pagination_class = CustomPageNumberPagination

    @extend_schema(responses=AirportSerializer(many=True))
    def get(self, request):
        airports = Airport.objects.select_related("country")
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(airports, request, view=self)
        serializer = AirportSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(request=AirportSerializer, responses=AirportSerializer)
    def post(self, request):
        serializer = AirportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Airports"])
class AirportDetailView(APIView):
    permission_classes = [IsAdminRoleOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(
            Airport.objects.select_related("country"), pk=pk
        )

    @extend_schema(responses=AirportSerializer)
    def get(self, request, pk):
        serializer = AirportSerializer(self.get_object(pk))
        return Response(serializer.data)

    @extend_schema(request=AirportSerializer, responses=AirportSerializer)
    def put(self, request, pk):
        serializer = AirportSerializer(self.get_object(pk), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(request=AirportSerializer, responses=AirportSerializer)
    def patch(self, request, pk):
        serializer = AirportSerializer(
            self.get_object(pk), data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(responses=None)
    def delete(self, request, pk):
        self.get_object(pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["Airlines"])
class AirlineViewSet(viewsets.ModelViewSet):
    queryset = Airline.objects.select_related("country").prefetch_related(
        "airports"
    )
    serializer_class = AirlineSerializer
    permission_classes = [IsAdminRoleOrReadOnly]


@extend_schema(tags=["Airplanes"])
class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airline")
    serializer_class = AirplaneSerializer
    permission_classes = [IsAdminRoleOrReadOnly]


@extend_schema(tags=["Flights"])
class FlightListCreateView(ListCreateAPIView):
    queryset = Flight.objects.select_related(
        "airplane", "departure_airport", "arrival_airport"
    )
    serializer_class = FlightSerializer
    filterset_class = FlightFilter
    permission_classes = [IsAdminRoleOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return FlightListSerializer
        return FlightSerializer


@extend_schema(tags=["Flights"])
class FlightDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Flight.objects.select_related(
        "airplane", "departure_airport", "arrival_airport"
    )
    serializer_class = FlightSerializer
    permission_classes = [IsAdminRoleOrReadOnly]


@extend_schema(tags=["Flights"])
class FlightTakenSeatsView(APIView):
    """Seats already taken on a flight (active, non-cancelled tickets)."""

    permission_classes = [IsAdminRoleOrReadOnly]

    @extend_schema(responses=FlightTakenSeatsSerializer)
    def get(self, request, pk):
        flight = get_object_or_404(Flight, pk=pk)
        rows = flight.airplane.rows
        seats_per_row = flight.airplane.seats_per_row
        seat_letters = flight.airplane.seat_letters
        taken_seats = list(
            Ticket.objects.filter(flight=flight)
            .exclude(status=Ticket.Status.CANCELLED)
            .order_by("seat_number")
            .values_list("seat_number", flat=True)
        )
        serializer = FlightTakenSeatsSerializer(
            {
                "flight": flight.pk,
                "rows": rows,
                "seats_per_row": seats_per_row,
                "seat_letters": seat_letters,
                "taken_seats": taken_seats,
            }
        )
        return Response(serializer.data)
