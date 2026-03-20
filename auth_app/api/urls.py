from django.urls import path

from .views import (
    ActivateTokenView,
    LoginView,
    LogoutView,
    RefreshTokenView,
    RegistrationView,
)

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", RefreshTokenView.as_view(), name="refresh"),
    path(
        "activate/<uidb64>/<token>/",
        ActivateTokenView.as_view(),
        name="activate_token",
    ),
]
