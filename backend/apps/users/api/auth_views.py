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

from .auth_utils import send_verification_email, send_otp_email
from .serializers import UserCreateSerializer

User = get_user_model()


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

        # Check if user has verified their email (optional for now)
        user = self.user
        if not user.email_verified:
            # Send a new verification email
            email_sent = send_verification_email(user)

            # Warn but allow login (soft verification)
            from rest_framework import serializers

            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "Email verification required. We've sent you a new verification link.",
                    ],
                    "requires_email_verification": True,
                    "email": user.email,
                    "email_sent": email_sent,
                },
            )

        # Add user data to response
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
            "date_joined": user.date_joined,
            "last_login": user.last_login,
        }

        data["user"] = user_data

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

    Expected payload:
    {
        "email": "user@example.com",  # Required OR phone_number
        "phone_number": "+1234567890",  # Required OR email
        "password": "secure_password",
        "first_name": "John",
        "last_name": "User"
    }

    Flow:
    1. Create user with email_verified=False
    2. Send OTP verification email (if email provided)
    3. Return user info (tokens on login only after OTP verification)

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

        # Send OTP email if email provided (Phase E Integration)
        email_sent = False
        if user.email:
            result = send_otp_email(user)
            email_sent = result["success"]

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
            {"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def user_profile(request):
    """
    Get current user's profile.

    Requires authentication.
    """
    user = request.user

    user_data = {
        "id": user.pk,
        "public_id": str(user.public_id),
        "email": user.email,
        "phone_number": user.phone_number if hasattr(user, "phone_number") else None,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "email_verified": user.email_verified,
        "date_joined": user.date_joined,
        "last_login": user.last_login,
    }

    return Response({"user": user_data}, status=status.HTTP_200_OK)


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


@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password(request):
    """
    Initiate password reset by sending email with reset link.

    Expected payload:
    {
        "email": "user@example.com"
    }
    """
    from django.contrib.auth.forms import PasswordResetForm

    email = request.data.get("email")
    if not email:
        return Response(
            {"error": "Email address is required"}, status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if user exists
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # For security, don't reveal if email exists or not
        return Response(
            {
                "message": "If an account with this email exists, you will receive a password reset link.",
            },
            status=status.HTTP_200_OK,
        )

    # Use Django's built-in password reset form
    form = PasswordResetForm({"email": email})
    if form.is_valid():
        # This will send the email
        form.save(
            request=request,
            use_https=request.is_secure(),
            email_template_name="registration/password_reset_email.txt",
            html_email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
        )

    return Response(
        {
            "message": "If an account with this email exists, you will receive a password reset link.",
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_confirm(request):
    """
    Confirm password reset with token and set new password.

    Expected payload:
    {
        "token": "password_reset_token",
        "uid": "encoded_user_id",
        "password": "new_password",
        "password_confirm": "new_password"
    }
    """
    from django.contrib.auth.forms import SetPasswordForm
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_decode

    token = request.data.get("token")
    uid = request.data.get("uid")
    password = request.data.get("password")
    password_confirm = request.data.get("password_confirm")

    if not all([token, uid, password, password_confirm]):
        return Response(
            {"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST,
        )

    if password != password_confirm:
        return Response(
            {"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Decode the user ID
        user_id = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {"error": "Invalid reset link"}, status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if token is valid
    if not default_token_generator.check_token(user, token):
        return Response(
            {"error": "Invalid or expired reset token"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Set the new password
    form = SetPasswordForm(
        user, {"new_password1": password, "new_password2": password_confirm},
    )
    if form.is_valid():
        form.save()
        return Response(
            {
                "message": "Password has been reset successfully. You can now log in with your new password.",
            },
            status=status.HTTP_200_OK,
        )
    return Response({"error": form.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_email(request):
    """
    Verify user's email address using signed token.

    Expected payload:
    {
        "token": "signed_verification_token"
    }
    """
    from django.core.signing import BadSignature
    from django.core.signing import Signer

    token = request.data.get("token")
    if not token:
        return Response(
            {"error": "Verification token is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Verify the signed token
        signer = Signer()
        original_value = signer.unsign(token)

        # Parse the token format: "email_verify_{user_pk}_{email}"
        if not original_value.startswith("email_verify_"):
            raise BadSignature("Invalid token format")

        parts = original_value.split(
            "_", 2,
        )  # Split into ['email', 'verify', '{pk}_{email}']
        if len(parts) != 3:
            raise BadSignature("Invalid token format")

        user_and_email = parts[2].split("_", 1)  # Split '{pk}_{email}' into [pk, email]
        if len(user_and_email) != 2:
            raise BadSignature("Invalid token format")

        user_pk = int(user_and_email[0])
        email = user_and_email[1]

        # Find and verify the user
        user = User.objects.get(pk=user_pk, email=email)

        if user.email_verified:
            return Response(
                {
                    "message": "Email is already verified. You can log in now.",
                    "verified": True,
                    "email": user.email,
                },
                status=status.HTTP_200_OK,
            )

        # Mark email as verified
        user.email_verified = True
        user.save()

        return Response(
            {
                "message": "Email verified successfully! You can now log in.",
                "verified": True,
                "email": user.email,
            },
            status=status.HTTP_200_OK,
        )

    except BadSignature:
        return Response(
            {"error": "Invalid or expired verification token.", "invalid": True},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except User.DoesNotExist:
        return Response(
            {"error": "Invalid verification token.", "invalid": True},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except ValueError:
        return Response(
            {"error": "Invalid verification token format.", "invalid": True},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {
                "error": "An error occurred during verification. Please try again.",
                "details": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def resend_verification_email(request):
    """
    Resend email verification for a user.

    Expected payload:
    {
        "email": "user@example.com"
    }
    """
    email = request.data.get("email")
    if not email:
        return Response(
            {"error": "Email address is required"}, status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = User.objects.get(email=email)

        # Only resend if user email is not yet verified
        if user.email_verified:
            return Response(
                {"message": "This email address is already verified."},
                status=status.HTTP_200_OK,
            )

        # Send new verification email using utility function
        email_sent = send_verification_email(user)

        return Response(
            {
                "message": "Verification email sent. Please check your inbox."
                if email_sent
                else "Failed to send verification email. Please try again later.",
                "email": user.email,
                "email_sent": email_sent,
            },
            status=status.HTTP_200_OK,
        )

    except User.DoesNotExist:
        # For security, don't reveal if email exists or not
        return Response(
            {
                "message": "If an account with this email exists, you will receive a verification email.",
            },
            status=status.HTTP_200_OK,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_otp(request):
    """
    Verify OTP code and return JWT tokens.

    Phase C: OTP Verification Endpoint

    Expected payload:
    {
        "email": "user@example.com",
        "otp": "123456"
    }

    Success Response (200):
    {
        "access": "jwt_access_token",
        "refresh": "jwt_refresh_token",
        "user": {
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "email_verified": true
        }
    }

    Error Responses (400):
    - Invalid OTP: {"error": "Invalid OTP code"}
    - Expired OTP: {"error": "No OTP code found for this email"}
    - Missing OTP: {"error": "No OTP code found for this email"}
    """
    import logging
    from apps.users.otp import get_otp, delete_otp

    logger = logging.getLogger(__name__)

    # Validate input
    email = request.data.get("email")
    otp_code = request.data.get("otp")

    if not email or not otp_code:
        return Response(
            {"error": "Email and OTP are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Get stored OTP from Redis
    stored_otp = get_otp(email)

    # Check if OTP exists (not expired)
    if stored_otp is None:
        return Response(
            {"error": "No OTP code found for this email"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Verify OTP matches
    if stored_otp != otp_code:
        return Response(
            {"error": "Invalid OTP code"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # OTP is valid - find and verify the user
    try:
        user = User.objects.get(email=email)
        user.email_verified = True
        user.save()

        # Delete OTP (one-time use)
        delete_otp(email)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        logger.info(f"OTP verified successfully for {email}")

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email_verified": user.email_verified,
                },
            },
            status=status.HTTP_200_OK,
        )

    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def resend_otp(request):
    """
    Resend OTP verification code.

    Phase D: OTP Resend Endpoint

    Expected payload:
    {
        "email": "user@example.com"
    }

    Success Response (200):
    {
        "message": "OTP sent successfully",
        "email": "user@example.com"
    }

    Error Responses:
    - 400: {"error": "Email is required"}
    - 400: {"error": "Email already verified"}
    - 404: {"error": "User not found"}
    - 429: {"error": "Please wait before requesting another OTP"}
    - 500: {"error": "Failed to send OTP"}
    """
    import logging
    from django.core.cache import cache
    from apps.users.api.auth_utils import send_otp_email

    logger = logging.getLogger(__name__)

    # Validate input
    email = request.data.get("email")

    if not email:
        return Response(
            {"error": "Email is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if user exists
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Check if already verified
    if user.email_verified:
        return Response(
            {"error": "Email already verified"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Rate limiting check (60 seconds)
    rate_limit_key = f"otp_last_sent:{email}"
    if cache.get(rate_limit_key):
        return Response(
            {"error": "Please wait before requesting another OTP"},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    # Send new OTP (this overwrites old one in Redis)
    result = send_otp_email(user)

    if result["success"]:
        # Set rate limit (60 seconds)
        cache.set(rate_limit_key, True, timeout=60)

        logger.info(f"OTP resent to {email}")
        return Response(
            {
                "message": "OTP sent successfully",
                "email": email,
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {"error": "Failed to send OTP"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
