from tokenize import TokenError

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from auth_app.api.serializers import (
    PasswordResetConfirmSerializer,
    RegistrationSerializer,
    ResetPasswordSerializer,
)

User = get_user_model()


from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


class RegistrationView(APIView):
    """User registration endpoint, sends activation email on success"""

    permission_classes = [AllowAny]

    def post(self, request):
        """Handle user registration, send activation email."""
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        user.is_active = False
        user.save()

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        user_email = user.email
        activation_link = f"http://127.0.0.1:5500/pages/auth/activate.html?uid={uidb64}&token={token}"
        html_content = render_to_string(
            "emails/activation.html",
            {"activation_link": activation_link, "user_email": user_email},
        )
        plain_text = f"""
        Hi {user_email}!,

        Click here to activate your Videoflix account:
        {activation_link}

        Thanks,
        Videoflix Team
        """
        send_mail(
            subject="Activate your Videoflix account",
            html_message=html_content,
            message=plain_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return Response(
            {"message": "Check your email to activate your account"},
            status=201,
        )


class LoginView(APIView):
    """User login endpoint that sets JWT tokens in cookies on success."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Handle user login, set JWT tokens in cookies if credentials are valid."""
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "email and password required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, email=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)

            response = Response(
                {
                    "detail": "Login successful",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                    },
                }
            )

            response.set_cookie(
                key="access_token",
                value=str(refresh.access_token),
                httponly=True,
                secure=False,
                samesite="Lax",
                max_age=30 * 60,  # 30 min
            )

            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                secure=False,
                samesite="Lax",
                max_age=7 * 24 * 60 * 60,  # 7 days
            )

            return response

        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class RefreshTokenView(APIView):
    """Endpoint to refresh JWT access token using the refresh token in cookies."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Handle token refresh, issue new access token if refresh token is valid."""
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"error": "No refresh token provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = RefreshToken(refresh_token)
            new_access = str(refresh.access_token)

            response = Response({"detail": "Token refreshed"})
            response.set_cookie(
                key="access_token",
                value=new_access,
                httponly=True,
                secure=False,
                samesite="Lax",
                max_age=30 * 60,
            )

            return response

        except Exception:
            return Response(
                {"error": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class LogoutView(APIView):
    """User logout endpoint that blacklists the refresh token and clears cookies."""

    def post(self, request):
        """Handle user logout, blacklist refresh token and clear cookies."""
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass

        response = Response(
            {
                "detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."
            }
        )
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


class ActivateTokenView(APIView):
    """Endpoint to activate user account using the token from the activation email."""

    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        """Handle account activation, activate user if link, token are valid and user is not active - activate user and set JWT tokens in cookies."""

        try:
            uid_bytes = urlsafe_base64_decode(uidb64)
            uid = int(uid_bytes.decode())
            user = User.objects.get(pk=uid)
        except (ValueError, TypeError, ObjectDoesNotExist):
            return Response({"error": "Invalid activation link"}, status=400)

        if user.is_active:
            return Response(
                {"message": "Account already activated"}, status=200
            )
        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=400)
        user.is_active = True
        user.save()

        refresh = RefreshToken.for_user(user)

        response = Response(
            {
                "message": "Account successfully activated.",
                "user": {"id": user.id, "email": user.email},
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key="access_token",
            value=str(refresh.access_token),
            httponly=True,
            secure=False,  # TODO change to True on https
            samesite="Lax",
            max_age=30 * 60,
        )

        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=7 * 24 * 60 * 60,
        )

        return response


class ResetPasswordView(APIView):
    """Endpoint to initiate password reset process"""

    permission_classes = [AllowAny]

    def post(self, request):
        """Handle password reset request, send reset email if user with provided email exists."""
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()

        if not user:
            return Response(
                {"detail": "An email has been sent to reset your password."},
                status=200,
            )

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        user_email = user.email
        reset_password_link = f"http://127.0.0.1:5500/pages/auth/confirm_password.html?uid={uidb64}&token={token}"
        html_content = render_to_string(
            "emails/reset_password.html",
            {
                "reset_password_link": reset_password_link,
                "user_email": user_email,
            },
        )
        plain_text = f"""
            Hi {user_email}!,

            Click below to reset your password::
            {reset_password_link}

            Videoflix Team
            """
        send_mail(
            subject="Reset password for your Videoflix account",
            html_message=html_content,
            message=plain_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response(
            {
                "detail": "If an account with that email exists, you will receive a password reset link shortly."
            },
            status=200,
        )


class PasswordResetConfirmView(APIView):
    """Endpoint to confirm password reset and set new password"""

    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        """Handle password reset confirmation, set new password if token is valid."""
        serializer = PasswordResetConfirmSerializer(
            data=request.data, context={"uidb64": uidb64, "token": token}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Your Password has been successfully reset."},
            status=status.HTTP_200_OK,
        )
