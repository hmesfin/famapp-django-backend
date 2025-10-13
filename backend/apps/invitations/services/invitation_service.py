"""
Core invitation service
Extracted from InvitationViewSet to separate business logic from HTTP concerns

Ham Dog's Django Commandments:
- Keep services stateless
- Pass all dependencies explicitly
- Return structured data, not HTTP responses
"""

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken

from apps.invitations.models import Invitation
from .invitation_token_service import InvitationTokenService
from .invitation_status_service import InvitationStatusService

User = get_user_model()


class InvitationService:
    """
    Core invitation operations service

    Handles:
    - Email existence checking
    - Invitation verification
    - User account creation from invitations
    - Orchestrates token and status services
    """

    def __init__(self):
        self.token_service = InvitationTokenService()
        self.status_service = InvitationStatusService()

    def check_email_exists(self, email: str) -> bool:
        """
        Check if an email already has a pending invitation
        Optimized to use database index on (email, status)

        Args:
            email: Email address to check

        Returns:
            bool: True if pending invitation exists
        """
        # Use exists() for boolean check - more efficient than count()
        return (
            Invitation.objects.active().filter(email=email, status="pending").exists()
        )

    def verify_invitation_token(self, token: str) -> dict:
        """
        Verify an invitation token and return invitation data
        Optimized to avoid accessing foreign key fields without select_related

        Args:
            token: Invitation token to verify

        Returns:
            dict: Invitation data or error information
        """
        # Use token service for validation with optimized query
        validation = self.token_service.validate_token(token)

        if not validation["is_valid"]:
            return validation

        invitation = validation["invitation"]

        # Access invited_by safely - it should be prefetched by token service
        invited_by_email = None
        if hasattr(invitation, "invited_by") and invitation.invited_by:
            invited_by_email = invitation.invited_by.email

        # Return expanded invitation data
        return {
            **validation,
            "email": invitation.email,
            "organization_name": invitation.organization_name,
            "role": invitation.role,
            "message": invitation.message,
            "invited_by": invited_by_email,
        }

    def resend_invitation(
        self, invitation: Invitation, custom_message: str = None
    ) -> dict:
        """
        Resend an invitation with a new token

        Args:
            invitation: Invitation instance to resend
            custom_message: Optional custom message to include

        Returns:
            dict: Success/error information
        """
        # Check if invitation can be resent
        can_resend = self.status_service.can_resend(invitation)
        if not can_resend["can_resend"]:
            return {"success": False, **can_resend}

        # Update message if provided
        if custom_message:
            invitation.message = custom_message

        # Generate new token and update expiry
        token_result = self.token_service.regenerate_token(invitation)
        if not token_result["success"]:
            return {"success": False, **token_result}

        # Send email for resent invitation
        self._send_invitation_email(invitation)

        return {
            "success": True,
            "message": "Invitation resent successfully",
            "invitation": invitation,
            "new_token": token_result["new_token"],
        }

    def accept_invitation(self, token: str, user_data: dict) -> dict:
        """
        Accept an invitation and create user account

        Args:
            token: Invitation token
            user_data: User account data (email, password, first_name, last_name)

        Returns:
            dict: User account info and JWT tokens

        Raises:
            Various exceptions for validation errors
        """
        invitation = get_object_or_404(Invitation, token=token)

        # Check if invitation can be accepted
        can_accept = self.status_service.can_accept(invitation)
        if not can_accept["can_accept"]:
            raise ValueError(can_accept["message"])

        # Create user account
        user = User.objects.create_user(
            email=invitation.email,
            password=user_data["password"],
            first_name=user_data.get("first_name", ""),
            last_name=user_data.get("last_name", ""),
        )

        # Accept the invitation using status service
        accept_result = self.status_service.accept_invitation(invitation, user)
        if not accept_result["success"]:
            # Rollback user creation if acceptance failed
            user.delete()
            raise ValueError(accept_result["message"])

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return {
            "user": user,
            "invitation": invitation,
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
        }

    def cancel_invitation(self, invitation: Invitation) -> dict:
        """
        Cancel a pending invitation

        Args:
            invitation: Invitation instance to cancel

        Returns:
            dict: Success/error information
        """
        return self.status_service.cancel_invitation(invitation)

    def get_my_invitations(self, user: User) -> "QuerySet":
        """
        Get invitations sent by a specific user
        Optimized with select_related to avoid N+1 queries

        Args:
            user: User who sent the invitations

        Returns:
            QuerySet: Invitations sent by the user
        """
        return (
            Invitation.objects.active()
            .select_related("invited_by", "accepted_by")
            .filter(invited_by=user)
            .order_by("-created_at")
        )

    def _send_invitation_email(self, invitation: Invitation):
        """
        Queue the invitation email to be sent via Celery
        Internal method to handle email sending
        """
        from apps.invitations.tasks import send_invitation_email

        # Queue the task asynchronously
        send_invitation_email.delay(invitation.id)

        return True
