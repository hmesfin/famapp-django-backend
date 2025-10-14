"""
OTP Verification API Views
FamApp OTP-based Email Verification

Handles:
- OTP verification with JWT token generation
- Family auto-creation on first login
- Invitation acceptance during signup
- OTP resend with rate limiting
"""

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_otp(request):
    """
    Verify OTP code and return JWT tokens.

    Phase C: OTP Verification Endpoint
    Phase G: Auto-join invited family after OTP verification

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
        },
        "families": [
            {"public_id": "uuid", "name": "John's Family", "role": "organizer"},
            {"public_id": "uuid2", "name": "Invited Family", "role": "parent"}
        ]
    }

    Error Responses (400):
    - Invalid OTP: {"error": "Invalid OTP code"}
    - Expired OTP: {"error": "No OTP code found for this email"}
    - Missing OTP: {"error": "No OTP code found for this email"}
    """
    import logging

    from apps.shared.models import FamilyMember
    from apps.users.models import Invitation
    from apps.users.otp import delete_otp
    from apps.users.otp import get_invitation_token
    from apps.users.otp import get_otp

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

        # Get invitation_token from Redis (Phase G)
        invitation_token_str = get_invitation_token(email)

        # Delete OTP (one-time use)
        delete_otp(email)

        families_data = []

        # IMPORTANT: Auto-create family for new user FIRST (Enhancement 2)
        # This ensures user always gets their own family with ORGANIZER role
        from apps.shared.services import create_family_for_user

        family, family_member = create_family_for_user(user)

        # Add auto-created family to response
        auto_family_data = {
            "public_id": str(family.public_id),
            "name": family.name,
            "role": family_member.role,
        }
        families_data.append(auto_family_data)

        # Phase G: Check for invitation and auto-join invited family (AFTER auto-create)
        invited_family_data = None
        if invitation_token_str:
            try:
                import uuid

                invitation_token = uuid.UUID(invitation_token_str)

                invitation = Invitation.objects.select_related("family").get(
                    token=invitation_token,
                    status=Invitation.Status.PENDING,
                    invitee_email__iexact=user.email,
                )

                # Check if invitation is still valid (not expired)
                if not invitation.is_expired:
                    # Accept invitation atomically
                    with transaction.atomic():
                        # Create FamilyMember
                        invited_member = FamilyMember.objects.create(
                            user=user,
                            family=invitation.family,
                            role=invitation.role,
                        )

                        # Mark invitation as accepted
                        invitation.status = Invitation.Status.ACCEPTED
                        invitation.updated_by = user
                        invitation.save()

                    # Add invited family to response (at the beginning for priority)
                    invited_family_data = {
                        "public_id": str(invitation.family.public_id),
                        "name": invitation.family.name,
                        "role": invited_member.role,
                    }
                    # Insert at beginning so invited family comes first in list
                    families_data.insert(0, invited_family_data)

                    logger.info(
                        f"User {email} accepted invitation and joined family {invitation.family.name}",
                    )
                else:
                    logger.warning(
                        f"Invitation {invitation_token} expired during signup for {email}",
                    )

            except (Invitation.DoesNotExist, ValueError) as e:
                # Invitation not found or invalid - continue with normal flow
                logger.warning(
                    f"Invitation token {invitation_token_str} not found or invalid for {email}: {e}",
                )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        logger.info(f"OTP verified successfully for {email}")

        response_data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email_verified": user.email_verified,
            },
            "families": families_data,
        }

        # Backward compatibility: include single "family" field for auto-created family
        response_data["family"] = auto_family_data

        # Include invited_family separately if exists
        if invited_family_data:
            response_data["invited_family"] = invited_family_data

        return Response(response_data, status=status.HTTP_200_OK)

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
    return Response(
        {"error": "Failed to send OTP"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
