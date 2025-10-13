"""
Invitation expiry management service
Extracted from InvitationViewSet extend_expiry action

Ham Dog's Expiry Management:
- Handle invitation expiry extensions
- Validate expiry permissions
- Manage expiry business rules
"""

from datetime import timedelta
from typing import Dict, Any
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.invitations.models import Invitation

User = get_user_model()


class InvitationExpiryService:
    """
    Handles invitation expiry management

    Provides:
    - Expiry date extension
    - Expiry permission validation
    - Bulk expiry operations
    - Expiry business rule enforcement
    """

    def __init__(self, permission_service=None):
        """Initialize expiry service with optional permission service injection"""
        if permission_service is None:
            from apps.invitations.services.permission_service import PermissionService

            permission_service = PermissionService()
        self.permission_service = permission_service

    def extend_expiry(
        self, invitation: Invitation, days: int, user: User
    ) -> Dict[str, Any]:
        """
        Extend the expiry date of an invitation

        Args:
            invitation: Invitation to extend
            days: Number of days to extend (1-30)
            user: User requesting the extension

        Returns:
            dict: Success/error information with updated invitation
        """
        # Check admin permission
        if not self.permission_service.can_extend_expiry(user):
            return {
                "success": False,
                "error": "Only administrators can extend invitation expiry",
            }

        # Validate invitation status
        if invitation.status != "pending":
            return {
                "success": False,
                "error": "Can only extend expiry for pending invitations",
            }

        # Validate days parameter
        validation_result = self._validate_extension_days(days)
        if not validation_result["is_valid"]:
            return {"success": False, "error": validation_result["error"]}

        # Extend the expiry
        invitation.expires_at = timezone.now() + timedelta(days=days)
        invitation.save(update_fields=["expires_at", "updated_at"])

        return {
            "success": True,
            "invitation": invitation,
            "extended_days": days,
            "new_expiry": invitation.expires_at,
        }

    def check_and_update_expired(self, batch_size: int = 100) -> Dict[str, Any]:
        """
        Check for expired invitations and update their status

        Args:
            batch_size: Number of invitations to process in each batch

        Returns:
            dict: Summary of expired invitations processed
        """
        now = timezone.now()

        # Find expired pending invitations
        expired_invitations = Invitation.objects.filter(
            status="pending", expires_at__lt=now
        )[:batch_size]

        updated_count = 0
        for invitation in expired_invitations:
            invitation.status = "expired"
            invitation.save(update_fields=["status", "updated_at"])
            updated_count += 1

        return {
            "processed_count": updated_count,
            "has_more": expired_invitations.count() == batch_size,
            "processed_at": now,
        }

    def get_expiring_soon(self, days_ahead: int = 7, user: User = None) -> "QuerySet":
        """
        Get invitations expiring within specified days

        Args:
            days_ahead: Number of days to look ahead
            user: Optional user to filter by (for non-admins)

        Returns:
            QuerySet: Invitations expiring soon
        """
        cutoff_date = timezone.now() + timedelta(days=days_ahead)

        queryset = Invitation.objects.filter(
            status="pending",
            expires_at__lte=cutoff_date,
            expires_at__gte=timezone.now(),
        ).order_by("expires_at")

        # Filter by user if not admin
        if user and not self.permission_service.can_extend_expiry(user):
            queryset = queryset.filter(invited_by=user)

        return queryset

    def bulk_extend_expiry(
        self, invitation_ids: list, days: int, user: User
    ) -> Dict[str, Any]:
        """
        Extend expiry for multiple invitations

        Args:
            invitation_ids: List of invitation IDs to extend
            days: Number of days to extend
            user: User requesting the extension

        Returns:
            dict: Results of bulk extension operation
        """
        # Check permission
        if not self.permission_service.can_extend_expiry(user):
            return {
                "success": False,
                "error": "Only administrators can extend invitation expiry",
            }

        # Validate days
        validation_result = self._validate_extension_days(days)
        if not validation_result["is_valid"]:
            return {"success": False, "error": validation_result["error"]}

        # Process invitations
        successful = []
        failed = []

        for invitation_id in invitation_ids:
            try:
                invitation = Invitation.objects.get(
                    public_id=invitation_id, status="pending"
                )

                invitation.expires_at = timezone.now() + timedelta(days=days)
                invitation.save(update_fields=["expires_at", "updated_at"])

                successful.append(
                    {
                        "invitation_id": str(invitation.public_id),
                        "email": invitation.email,
                        "new_expiry": invitation.expires_at,
                    }
                )

            except Invitation.DoesNotExist:
                failed.append(
                    {
                        "invitation_id": invitation_id,
                        "error": "Invitation not found or not pending",
                    }
                )
            except Exception as e:
                failed.append({"invitation_id": invitation_id, "error": str(e)})

        return {
            "success": len(failed) == 0,
            "successful": successful,
            "failed": failed,
            "total_processed": len(successful) + len(failed),
        }

    def get_expiry_summary(self, user: User = None) -> Dict[str, Any]:
        """
        Get summary of invitation expiry status

        Args:
            user: Optional user to filter by

        Returns:
            dict: Expiry summary statistics
        """
        now = timezone.now()
        base_queryset = Invitation.objects.filter(status="pending")

        # Filter by user if not admin
        if user and not self.permission_service.can_extend_expiry(user):
            base_queryset = base_queryset.filter(invited_by=user)

        # Calculate different expiry categories
        expired = base_queryset.filter(expires_at__lt=now).count()
        expiring_today = base_queryset.filter(expires_at__date=now.date()).count()
        expiring_week = base_queryset.filter(
            expires_at__gte=now, expires_at__lte=now + timedelta(days=7)
        ).count()
        expiring_month = base_queryset.filter(
            expires_at__gte=now + timedelta(days=7),
            expires_at__lte=now + timedelta(days=30),
        ).count()

        return {
            "expired": expired,
            "expiring_today": expiring_today,
            "expiring_this_week": expiring_week,
            "expiring_this_month": expiring_month,
            "total_pending": base_queryset.count(),
        }

    def _has_extend_permission(self, user: User) -> bool:
        """
        Check if user has permission to extend invitation expiry

        Args:
            user: User to check permissions for

        Returns:
            bool: True if user can extend expiry
        """
        return self.permission_service.can_extend_expiry(user)

    def _validate_extension_days(self, days: Any) -> Dict[str, Any]:
        """
        Validate the extension days parameter

        Args:
            days: Days value to validate

        Returns:
            dict: Validation result
        """
        try:
            days = int(days)
            if days <= 0 or days > 30:
                return {
                    "is_valid": False,
                    "error": "Days must be a positive integer between 1 and 30",
                }
            return {"is_valid": True, "validated_days": days}
        except (ValueError, TypeError):
            return {
                "is_valid": False,
                "error": "Days must be a positive integer between 1 and 30",
            }
