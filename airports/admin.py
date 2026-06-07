from django.contrib import admin
from django.db.models import Count, Q

from tickets.models import Ticket

from .models import Airline, Airplane, Airport, Country, Flight

admin.site.register(Country)
admin.site.register(Airport)
admin.site.register(Airline)


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = [
        "model",
        "registration_number",
        "airline",
        "rows",
        "seats_per_row",
        "seat_letters",
        "capacity",
    ]
    list_filter = ["airline", "model"]
    search_fields = ["model", "registration_number"]
    readonly_fields = ["seat_letters", "capacity_display"]

    @admin.display(description="Capacity")
    def capacity_display(self, obj):
        if obj.rows is None or obj.seats_per_row is None:
            return "—"
        return obj.capacity


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = [
        "flight_number",
        "route",
        "departure_time",
        "arrival_time",
        "status",
        "base_price",
        "airplane",
        "occupancy",
    ]
    list_filter = ["status", "departure_airport", "arrival_airport"]
    search_fields = ["flight_number"]
    list_select_related = [
        "airplane",
        "departure_airport",
        "arrival_airport",
    ]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(
                sold_tickets=Count(
                    "tickets",
                    filter=~Q(tickets__status=Ticket.Status.CANCELLED),
                )
            )
        )

    @admin.display(description="Route")
    def route(self, obj):
        return f"{obj.departure_airport.code} → {obj.arrival_airport.code}"

    @admin.display(description="Seats (sold / total)")
    def occupancy(self, obj):
        return f"{obj.sold_tickets} / {obj.airplane.capacity}"
