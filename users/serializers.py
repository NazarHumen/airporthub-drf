from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "phone", "role"]
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )

    class Meta:
        model = User
        fields = ["id", "email", "username", "phone", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self, **kwargs):
        try:
            RefreshToken(self.validated_data["refresh"]).blacklist()
        except TokenError:
            raise serializers.ValidationError(
                {"refresh": "Invalid or expired token."}
            )


class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["role"] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "role": self.user.role,
        }
        return data
