from django.urls import path

from users.views import (
    LoginView,
    LogoutView,
    MeView,
    RegisterView,
    TokenRefreshAuthView,
)

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path(
        "token/refresh/",
        TokenRefreshAuthView.as_view(),
        name="token_refresh",
    ),
]
