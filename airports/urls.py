from django.urls import path

from airports import views

urlpatterns = [
    path("flights/", views.FlightListCreateView.as_view(), name="flight-list"),
    path(
        "flights/<int:pk>/",
        views.FlightDetailView.as_view(),
        name="flight-detail",
    ),
]
