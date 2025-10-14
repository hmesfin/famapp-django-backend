"""
Authentication API Views
FamApp JWT Authentication - Simple & Clean

Following the Ten Commandments:
- JWT tokens for stateless authentication
- Email/Phone + password authentication
- Clean error handling
"""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import UserCreateSerializer

User = get_user_model()


def get_user_data_with_role(user):
    """
    Get user data including their family role.

    Since we enforce one-user-one-family, we can include the role directly.
    Returns None for role if user has no family membership.
    """
    from apps.shared.models import FamilyMember

    # Get user's family membership (should be only one)
    membership = FamilyMember.objects.filter(user=user).select_related("family").first()

    user_data = {
        "id": user.pk,
        "public_id": str(user.public_id),
        "email": user.email,
        "phone_number": user.phone_number if hasattr(user, "phone_number") else None,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "email_verified": user.email_verified
        if hasattr(user, "email_verified")
        else True,
        "date_joined": user.date_joined,
        "last_login": user.last_login,
    }

    # Add role and family info if user has membership
    if membership:
        user_data["role"] = membership.role
        user_data["family"] = {
            "public_id": str(membership.family.public_id),
            "name": membership.family.name,
        }
    else:
        user_data["role"] = None
        user_data["family"] = None

    return user_data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that uses email instead of username.

    Includes basic user info in the response.
    """

    username_field = "email"

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Keep it simple - standard JWT claims only
        return token

    def validate(self, attrs):
        # First, perform standard validation
        data = super().validate(attrs)

        # Check if user has verified their email via OTP
        user = self.user
        if not user.email_verified:
            # Block login - OTP verification required
            # Auto-send OTP with rate limiting (civilized UX!)
            from django.core.cache import cache
            from rest_framework import serializers

            from apps.users.api.auth_utils import send_otp_email

            email_sent = False
            rate_limit_key = f"otp_last_sent:{user.email}"

            # Check rate limit (60 seconds)
            if not cache.get(rate_limit_key):
                # Send OTP
                result = send_otp_email(user)
                if result["success"]:
                    cache.set(rate_limit_key, True, timeout=60)
                    email_sent = True

            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "Email verification required. "
                        + (
                            "We've sent you a new verification code."
                            if email_sent
                            else "Please check your email for your verification code, or request a new one."
                        ),
                    ],
                    "requires_email_verification": True,
                    "email": user.email,
                    "email_sent": email_sent,
                },
            )

        # Add user data with role to response
        data["user"] = get_user_data_with_role(user)

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view that includes user data.

    Accepts email OR phone number + password.
    """

    serializer_class = CustomTokenObtainPairSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user with email or phone number.

    Phase E: Registration Flow Integration with OTP
    Phase G: Support invitation_token for signup with invitation flow

    Expected payload:
    {
        "email": "user@example.com",  # Required OR phone_number
        "phone_number": "+1234567890",  # Required OR email
        "password": "secure_password",
        "first_name": "John",
        "last_name": "User",
        "invitation_token": "uuid"  # Optional (Phase G)
    }

    Flow:
    1. Create user with email_verified=False
    2. Send OTP verification email (if email provided)
    3. Store invitation_token in OTP cache (if provided)
    4. Return user info (tokens on login only after OTP verification)

    Success Response (201):
    {
        "user": {
            "id": 1,
            "public_id": "uuid",
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "User",
            "email_verified": false
        },
        "message": "Registration successful! Please check your email for your verification code.",
        "email_sent": true,
        "requires_email_verification": true
    }
    """
    serializer = UserCreateSerializer(data=request.data)

    if serializer.is_valid():
        # Create user with email verification required
        user = serializer.save()
        user.email_verified = False
        user.save()

        # Get invitation_token if provided (Phase G)
        invitation_token = serializer.validated_data.get("invitation_token")

        # Send OTP email if email provided (Phase E Integration)
        # Store invitation_token with OTP (Phase G)
        email_sent = False
        if user.email:
            from apps.users.otp import generate_otp
            from apps.users.otp import store_otp

            # Generate OTP
            otp = generate_otp()

            # Store OTP with invitation_token
            store_otp(
                user.email,
                otp,
                invitation_token=str(invitation_token) if invitation_token else None,
            )

            # Send OTP email
            import logging

            from django.conf import settings
            from django.core.mail import send_mail
            from django.template.loader import render_to_string

            logger = logging.getLogger(__name__)

            try:
                context = {
                    "user": user,
                    "otp": otp,
                    "expiration_minutes": 10,
                    "app_name": "FamApp",
                }

                subject = "FamApp - Your Verification Code"
                html_message = render_to_string(
                    "emails/otp_verification_email.html", context
                )
                plain_message = render_to_string(
                    "emails/otp_verification_email.txt", context
                )

                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=False,
                )

                logger.info(f"OTP email sent successfully to {user.email}")
                email_sent = True
            except Exception as e:
                logger.error(f"Failed to send OTP email to {user.email}: {e}")
                email_sent = False

        # Prepare user data (no tokens until login)
        user_data = {
            "id": user.pk,
            "public_id": str(user.public_id),
            "email": user.email,
            "phone_number": user.phone_number
            if hasattr(user, "phone_number")
            else None,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "date_joined": user.date_joined,
        }

        return Response(
            {
                "user": user_data,
                "message": "Registration successful! "
                + (
                    "Please check your email for your verification code."
                    if email_sent
                    else "You can now log in."
                ),
                "email_sent": email_sent,
                "requires_email_verification": bool(user.email),
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def logout(request):
    """
    Logout user by blacklisting the refresh token.

    Expected payload:
    {
        "refresh": "refresh_token_string"
    }
    """
    try:
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        return Response(
            {"error": "Refresh token required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def user_profile(request):
    """
    Get current user's profile including family role.

    Requires authentication.
    """
    return Response(
        {"user": get_user_data_with_role(request.user)}, status=status.HTTP_200_OK
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def auth_check(request):
    """
    Check if the current request is authenticated.

    This is useful for frontend to check token validity.
    """
    if request.user.is_authenticated:
        return Response(
            {
                "authenticated": True,
                "user_id": request.user.pk,
                "email": request.user.email,
            },
            status=status.HTTP_200_OK,
        )
    return Response(
        {
            "authenticated": False,
        },
        status=status.HTTP_200_OK,
    )
