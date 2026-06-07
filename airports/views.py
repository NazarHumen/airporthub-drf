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
)


@extend_schema(tags=["Geography"])
class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAdminRoleOrReadOnly]


@extend_schema(tags=["Airports"])
class AirportListCreateView(APIView):
    permission_classes = [IsAdminRoleOrReadOnly]

    @extend_schema(responses=AirportSerializer(many=True))
    def get(self, request):
        airports = Airport.objects.select_related("country")
        serializer = AirportSerializer(airports, many=True)
        return Response(serializer.data)

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
