from django.contrib import admin

from .models import Airline, Airplane, Airport, Country, Flight, Ticket

admin.site.register(Country)
admin.site.register(Airport)
admin.site.register(Airline)
admin.site.register(Airplane)
admin.site.register(Flight)
admin.site.register(Ticket)
