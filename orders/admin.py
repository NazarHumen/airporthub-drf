from django.contrib import admin

from orders.models import Order
from tickets.models import Ticket


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "status",
        "total_price",
        "reserved_until",
        "created_at",
        "paid_at",
    ]
    list_filter = ["status"]
    search_fields = ["user__email"]
    inlines = [TicketInline]
