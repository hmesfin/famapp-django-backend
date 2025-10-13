"""
Invitation Status Service
Handles status transitions and validation logic for invitations

Ham Dog's Django Commandments:
- Keep services stateless
- Pass all dependencies explicitly
- Return structured data, not domain objects
- Enforce business rules consistently
"""

from typing import Dict, Optional, List
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.invitations.models import Invitation

User = get_user_model()


class InvitationStatusService:
    """
    Service for managing invitation status transitions

    Handles:
    - Status validation and transitions
    - Business rules enforcement
    - Acceptance logic
    - Cancellation logic
    - Status history tracking
    """

    # Valid status transitions
    VALID_TRANSITIONS = {
        "pending": ["accepted", "expired", "cancelled"],
        "accepted": [],  # Terminal state
        "expired": ["pending"],  # Can be resent
        "cancelled": ["pending"],  # Can be resent
    }

    TERMINAL_STATUSES = ["accepted"]
    RESENDABLE_STATUSES = [
        "pending"
    ]  # Only pending invitations can be resent (original behavior)

    def validate_status_transition(self, from_status: str, to_status: str) -> Dict:
        """
        Validate if a status transition is allowed

        Args:
            from_status: Current status
            to_status: Desired status

        Returns:
            dict: Validation result
        """
        if from_status not in self.VALID_TRANSITIONS:
            return {
                "is_valid": False,
                "error": "invalid_current_status",
                "message": f"Invalid current status: {from_status}",
            }

        allowed_transitions = self.VALID_TRANSITIONS[from_status]

        if to_status not in allowed_transitions:
            return {
                "is_valid": False,
                "error": "invalid_transition",
                "message": f"Cannot transition from {from_status} to {to_status}. Allowed: {allowed_transitions}",
            }

        return {"is_valid": True, "from_status": from_status, "to_status": to_status}

    def can_accept(self, invitation: Invitation) -> Dict:
        """
        Check if an invitation can be accepted

        Args:
            invitation: Invitation to check

        Returns:
            dict: Validation result with details
        """
        # Check if invitation is soft-deleted
        if invitation.is_deleted:
            return {
                "can_accept": False,
                "error": "deleted_invitation",
                "message": "Cannot accept deleted invitation",
            }

        # Check status
        if invitation.status != "pending":
            return {
                "can_accept": False,
                "error": "invalid_status",
                "message": f"Cannot accept invitation with status: {invitation.status}",
            }

        # Check expiry
        if invitation.expires_at and timezone.now() > invitation.expires_at:
            return {
                "can_accept": False,
                "error": "expired",
                "message": "Invitation has expired",
            }

        # Check if user already exists
        if User.objects.filter(email=invitation.email).exists():
            return {
                "can_accept": False,
                "error": "user_exists",
                "message": "User with this email already exists",
            }

        return {"can_accept": True, "invitation": invitation}

    def can_cancel(self, invitation: Invitation) -> Dict:
        """
        Check if an invitation can be cancelled

        Args:
            invitation: Invitation to check

        Returns:
            dict: Validation result with details
        """
        # Check if invitation is soft-deleted
        if invitation.is_deleted:
            return {
                "can_cancel": False,
                "error": "deleted_invitation",
                "message": "Cannot cancel deleted invitation",
            }

        # Can only cancel pending invitations
        if invitation.status != "pending":
            return {
                "can_cancel": False,
                "error": "invalid_status",
                "message": f"Cannot cancel invitation with status: {invitation.status}",
            }

        return {"can_cancel": True, "invitation": invitation}

    def can_resend(self, invitation: Invitation) -> Dict:
        """
        Check if an invitation can be resent

        Args:
            invitation: Invitation to check

        Returns:
            dict: Validation result with details
        """
        # Check if invitation is soft-deleted
        if invitation.is_deleted:
            return {
                "can_resend": False,
                "error": "deleted_invitation",
                "message": "Cannot resend deleted invitation",
            }

        # Can resend if status allows it
        if invitation.status not in self.RESENDABLE_STATUSES:
            return {
                "can_resend": False,
                "error": "invalid_status",
                "message": f"Can only resend pending invitations, not {invitation.status}",
            }

        # Check if user already exists
        if User.objects.filter(email=invitation.email).exists():
            return {
                "can_resend": False,
                "error": "user_exists",
                "message": "User with this email already exists",
            }

        return {"can_resend": True, "invitation": invitation}

    @transaction.atomic
    def accept_invitation(self, invitation: Invitation, user: User) -> Dict:
        """
        Accept an invitation and update status

        Args:
            invitation: Invitation to accept
            user: User accepting the invitation

        Returns:
            dict: Result of acceptance
        """
        # Validate acceptance
        validation = self.can_accept(invitation)
        if not validation["can_accept"]:
            return {"success": False, **validation}

        # Perform acceptance
        old_status = invitation.status
        invitation.status = "accepted"
        invitation.accepted_by = user
        invitation.accepted_at = timezone.now()
        invitation.save()

        return {
            "success": True,
            "old_status": old_status,
            "new_status": "accepted",
            "accepted_at": invitation.accepted_at,
            "invitation": invitation,
        }

    @transaction.atomic
    def cancel_invitation(self, invitation: Invitation) -> Dict:
        """
        Cancel an invitation

        Args:
            invitation: Invitation to cancel

        Returns:
            dict: Result of cancellation
        """
        # Validate cancellation
        validation = self.can_cancel(invitation)
        if not validation["can_cancel"]:
            return {"success": False, **validation}

        # Perform cancellation
        old_status = invitation.status
        invitation.status = "cancelled"
        invitation.save()

        return {
            "success": True,
            "old_status": old_status,
            "new_status": "cancelled",
            "cancelled_at": timezone.now(),
            "invitation": invitation,
        }

    @transaction.atomic
    def expire_invitation(self, invitation: Invitation) -> Dict:
        """
        Mark an invitation as expired

        Args:
            invitation: Invitation to expire

        Returns:
            dict: Result of expiration
        """
        # Can expire pending invitations
        if invitation.status != "pending":
            return {
                "success": False,
                "error": "invalid_status",
                "message": f"Cannot expire invitation with status: {invitation.status}",
            }

        # Perform expiration
        old_status = invitation.status
        invitation.status = "expired"
        invitation.save()

        return {
            "success": True,
            "old_status": old_status,
            "new_status": "expired",
            "expired_at": timezone.now(),
            "invitation": invitation,
        }

    def get_status_summary(self, invitation: Invitation) -> Dict:
        """
        Get comprehensive status information for an invitation

        Args:
            invitation: Invitation to analyze

        Returns:
            dict: Status summary with available actions
        """
        summary = {
            "current_status": invitation.status,
            "is_terminal": invitation.status in self.TERMINAL_STATUSES,
            "is_pending": invitation.status == "pending",
            "is_accepted": invitation.status == "accepted",
            "is_expired": invitation.status == "expired",
            "is_cancelled": invitation.status == "cancelled",
            "available_actions": [],
        }

        # Determine available actions
        if self.can_accept(invitation)["can_accept"]:
            summary["available_actions"].append("accept")

        if self.can_cancel(invitation)["can_cancel"]:
            summary["available_actions"].append("cancel")

        if self.can_resend(invitation)["can_resend"]:
            summary["available_actions"].append("resend")

        # Add timing information
        if invitation.accepted_at:
            summary["accepted_at"] = invitation.accepted_at
            summary["accepted_by"] = (
                invitation.accepted_by.email if invitation.accepted_by else None
            )

        if invitation.expires_at:
            summary["expires_at"] = invitation.expires_at
            summary["is_time_expired"] = timezone.now() > invitation.expires_at
            if not summary["is_time_expired"]:
                summary["time_remaining"] = invitation.expires_at - timezone.now()

        return summary

    def bulk_expire_invitations(self, queryset) -> Dict:
        """
        Bulk expire multiple invitations

        Args:
            queryset: QuerySet of invitations to expire

        Returns:
            dict: Summary of bulk operation
        """
        # Filter to only pending invitations
        pending_invitations = queryset.filter(status="pending")
        count = pending_invitations.count()

        if count == 0:
            return {
                "success": True,
                "expired_count": 0,
                "message": "No pending invitations to expire",
            }

        # Bulk update
        updated_count = pending_invitations.update(status="expired")

        return {
            "success": True,
            "expired_count": updated_count,
            "message": f"Expired {updated_count} invitations",
        }
