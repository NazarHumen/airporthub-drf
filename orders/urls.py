from django.urls import include, path
from rest_framework.routers import DefaultRouter

from orders.views import OrderViewSet

app_name = "orders"

router = DefaultRouter()
router.register("orders", OrderViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
