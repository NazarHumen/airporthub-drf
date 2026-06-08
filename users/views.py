import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView

from users.serializers import (
    LoginSerializer,
    LogoutSerializer,
    RegisterSerializer,
    UserSerializer,
)

logger = logging.getLogger("airporthub")


@extend_schema(
    tags=["Auth"],
    request=RegisterSerializer,
    responses=RegisterSerializer,
)
class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "auth"

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["Auth"], request=LoginSerializer, responses=LoginSerializer
)
class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "auth"

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except (ValidationError, AuthenticationFailed):
            logger.warning(
                "Failed login for %s from %s",
                request.data.get("email"),
                request.META.get("REMOTE_ADDR"),
            )
            raise
        logger.info(
            "User %s logged in from %s",
            serializer.validated_data["user"]["id"],
            request.META.get("REMOTE_ADDR"),
        )
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Auth"],
    request=LogoutSerializer,
    responses={204: None},
)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["Auth"])
class TokenRefreshAuthView(TokenRefreshView):
    throttle_scope = "auth"


@extend_schema(tags=["Auth"], responses=UserSerializer)
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
