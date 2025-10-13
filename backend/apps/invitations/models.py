"""
Invitation model for managing user invitations
Refactored to separate concerns - data definition only, business logic moved to services
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.shared.models import BaseModel
from apps.permissions.constants import ROLE_CHOICES, RoleCodeName

User = get_user_model()


class InvitationQuerySet(models.QuerySet):
    """Custom queryset for Invitation model"""

    def active(self):
        """Return only non-deleted invitations"""
        return self.filter(is_deleted=False)

    def deleted(self):
        """Return only soft-deleted invitations"""
        return self.filter(is_deleted=True)


class InvitationManager(models.Manager):
    """Custom manager for Invitation model"""

    def get_queryset(self):
        """Return the custom queryset"""
        return InvitationQuerySet(self.model, using=self._db)

    def active(self):
        """Return only active (non-deleted) invitations"""
        return self.get_queryset().active()

    def deleted(self):
        """Return only soft-deleted invitations"""
        return self.get_queryset().deleted()


class Invitation(BaseModel):
    """
    Model for managing user invitations to the platform
    Inherits from BaseModel for audit trail and soft delete
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    ]

    # Invitation details
    email = models.EmailField(db_index=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    token = models.CharField(max_length=64, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # Who invited
    invited_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="invitations_sent"
    )

    # Optional fields for context
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=RoleCodeName.MEMBER,
        help_text="Role to assign to the invited user",
    )
    organization_name = models.CharField(max_length=255, blank=True)
    message = models.TextField(blank=True)

    # Acceptance tracking
    accepted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invitation_accepted",
    )
    accepted_at = models.DateTimeField(null=True, blank=True)

    # Expiry
    expires_at = models.DateTimeField()

    # Custom manager
    objects = InvitationManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            # Existing indexes
            models.Index(fields=["email", "status"]),
            models.Index(fields=["token"]),
            # New optimized indexes based on query patterns
            models.Index(
                fields=["status", "is_deleted"]
            ),  # For active() + status filtering
            models.Index(
                fields=["invited_by", "status", "is_deleted"]
            ),  # For user's invitations
            models.Index(fields=["is_deleted", "created_at"]),  # For active() ordering
            models.Index(fields=["status", "expires_at"]),  # For pending expiry checks
            models.Index(
                fields=["email", "status", "is_deleted"]
            ),  # For email existence checks
            models.Index(
                fields=["status", "accepted_at"]
            ),  # For acceptance time calculations
            models.Index(fields=["role", "is_deleted"]),  # For role distribution stats
        ]

    def __str__(self):
        return f"Invitation to {self.email} ({self.status})"

    @property
    def get_full_name(self):
        """Get the full name of the invited person"""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email

    def save(self, *args, **kwargs):
        """
        Override save to ensure required fields are set

        For backward compatibility, generates token and expiry if not set.
        New code should use services to set these before saving.
        """
        # Generate token if not set (backward compatibility)
        if not self.token:
            # Import here to avoid circular imports
            from apps.invitations.services.invitation_token_service import (
                InvitationTokenService,
            )

            token_service = InvitationTokenService()
            self.token = token_service.generate_unique_token()

        # Set expiry if not set (backward compatibility)
        if not self.expires_at:
            from apps.invitations.services.invitation_token_service import (
                InvitationTokenService,
            )

            token_service = InvitationTokenService()
            self.expires_at = token_service.calculate_expiry_date()

        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Check if the invitation has expired"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    # Backward compatibility methods - delegate to services

    def accept(self, user):
        """
        Accept the invitation (backward compatibility)

        Note: New code should use InvitationStatusService.accept_invitation()
        """
        from django.core.exceptions import ValidationError

        # Basic validation (similar to the original logic)
        if self.status == "accepted":
            raise ValidationError("This invitation has already been accepted")

        if self.is_expired:
            raise ValidationError("This invitation has expired")

        # Simple acceptance without complex user existence checks
        # (original model behavior was simpler)
        self.status = "accepted"
        self.accepted_by = user
        self.accepted_at = timezone.now()
        self.save()

    def resend(self):
        """
        Resend the invitation with a new token (backward compatibility)

        Note: New code should use InvitationTokenService.regenerate_token()
        and InvitationService._send_invitation_email()
        """
        from apps.invitations.services.invitation_token_service import (
            InvitationTokenService,
        )

        token_service = InvitationTokenService()

        # Regenerate token
        result = token_service.regenerate_token(self)
        if not result["success"]:
            raise ValueError(result.get("message", "Cannot resend invitation"))

        # Send email
        self.send_invitation_email()

    def cancel(self):
        """
        Cancel the invitation (backward compatibility)

        Note: New code should use InvitationStatusService.cancel_invitation()
        """
        from apps.invitations.services.invitation_status_service import (
            InvitationStatusService,
        )

        status_service = InvitationStatusService()

        result = status_service.cancel_invitation(self)
        if not result["success"]:
            raise ValueError(result.get("message", "Cannot cancel invitation"))

    def send_invitation_email(self):
        """
        Queue the invitation email to be sent via Celery (backward compatibility)

        Note: New code should use InvitationService._send_invitation_email()
        """
        from apps.invitations.tasks import send_invitation_email

        # Queue the task asynchronously
        send_invitation_email.delay(self.id)

        return True

    def delete(self, using=None, keep_parents=False):
        """Override delete to perform soft delete"""
        self.soft_delete()
        return 1, {self._meta.label: 1}
