from drf_spectacular.utils import extend_schema
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orders.models import Order
from orders.serializers import OrderSerializer
from orders.services import cancel_order, pay_order
from tickets.permissions import IsOwnerOrAdmin


@extend_schema(tags=["Orders"])
class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Order.objects.select_related("user").prefetch_related(
        "tickets__flight"
    )
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filterset_fields = ["status"]

    def get_queryset(self):
        qs = super().get_queryset()
        if getattr(self, "swagger_fake_view", False):
            return qs.none()
        if self.request.user.is_admin:
            return qs
        return qs.filter(user=self.request.user)

    @extend_schema(request=None, responses=OrderSerializer)
    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):
        """Pay for a pending order: pending - paid."""
        order = pay_order(self.get_object())
        return Response(self.get_serializer(order).data)

    @extend_schema(request=None, responses=OrderSerializer)
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel an order and release its seats: pending/paid - cancelled."""
        order = cancel_order(self.get_object())
        return Response(self.get_serializer(order).data)
