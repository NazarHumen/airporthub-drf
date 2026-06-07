import re
import string

from django.db import models

SEAT_RE = re.compile(r"^([0-9]{1,3})([A-Z])$")


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=4, unique=True)
    city = models.CharField(max_length=100)
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="airports",
    )

    class Meta:
        ordering = ["country__name", "city"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Airline(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=3, unique=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="airlines",
    )
    airports = models.ManyToManyField(
        Airport,
        related_name="airlines",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Airplane(models.Model):
    model = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=20, unique=True)
    rows = models.PositiveSmallIntegerField()
    seats_per_row = models.PositiveSmallIntegerField(default=6)
    airline = models.ForeignKey(
        Airline,
        on_delete=models.CASCADE,
        related_name="airplanes",
    )

    class Meta:
        ordering = ["airline__name", "model"]

    @property
    def capacity(self):
        return self.rows * self.seats_per_row

    @property
    def seat_letters(self):
        return string.ascii_uppercase[: self.seats_per_row]

    def is_valid_seat(self, seat_number):
        match = SEAT_RE.fullmatch(seat_number.upper())
        if not match:
            return False
        row = int(match.group(1))
        letter = match.group(2)
        return 1 <= row <= self.rows and letter in self.seat_letters

    def __str__(self):
        return f"{self.model} ({self.registration_number})"


class Flight(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        BOARDING = "boarding", "Boarding"
        DEPARTED = "departed", "Departed"
        DELAYED = "delayed", "Delayed"
        CANCELLED = "cancelled", "Cancelled"

    flight_number = models.CharField(max_length=10)
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.PROTECT,
        related_name="flights",
    )
    departure_airport = models.ForeignKey(
        Airport,
        on_delete=models.PROTECT,
        related_name="departures",
    )
    arrival_airport = models.ForeignKey(
        Airport,
        on_delete=models.PROTECT,
        related_name="arrivals",
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["-departure_time"]

    def __str__(self):
        return (
            f"{self.flight_number}: "
            f"{self.departure_airport.code} - "
            f"{self.arrival_airport.code}"
        )
