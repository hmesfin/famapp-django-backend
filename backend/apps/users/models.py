import uuid
from datetime import timedelta
from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import BooleanField
from django.db.models import CharField
from django.db.models import EmailField
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.shared.models import BaseModel
from apps.shared.models import TimestampedMixin
from apps.shared.models import UUIDMixin

from .managers import UserManager


class User(UUIDMixin, TimestampedMixin, AbstractUser):
    """
    Ham Dog & TC's custom user model for the DjVue Orchestra.

    Features:
    - UUID primary key (Commandment #1: No bigint shame!)
    - Timestamp tracking (created_at, updated_at)
    - Email-based authentication
    - First name + Last name structure (civilized naming!)

    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # Use proper first_name and last_name instead of generic 'name'
    first_name = CharField(_("First name"), blank=True, max_length=150)
    last_name = CharField(_("Last name"), blank=True, max_length=150)
    email = EmailField(_("email address"), unique=True)
    email_verified = BooleanField(
        _("email verified"),
        default=False,
        help_text=_("Designates whether this user has verified their email address."),
    )
    username = None  # type: ignore[assignment]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    class Meta:
        # Inherit from TimestampedMixin ordering but override for users
        ordering = ["-created_at", "email"]
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail using public_id (Stripe/Instagram pattern).

        """
        return reverse("api:user-detail", kwargs={"public_id": self.public_id})

    def get_full_name(self) -> str:
        """
        Get the user's full name.

        Returns:
            str: Full name combining first and last name.
        """
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email

    def get_short_name(self) -> str:
        """
        Get the user's short name.

        Returns:
            str: First name or email if first name is empty.
        """
        return self.first_name or self.email

    def __str__(self) -> str:
        """
        String representation of the user.

        Returns:
            str: Full name or email.
        """
        return self.get_full_name() or self.email


class Invitation(BaseModel):
    """
    Family Invitation model for FamApp (Enhancement 3).

    Allows ORGANIZERS to invite new members to their family by email.
    Invitations have a 7-day expiration and can only assign PARENT or CHILD roles
    (ORGANIZER role is excluded for security).

    Features:
    - UUID token for invitation links
    - Email-based invitations
    - Role assignment (PARENT/CHILD only)
    - 7-day expiration
    - Status tracking (PENDING, ACCEPTED, DECLINED, EXPIRED, CANCELLED)
    - Audit trail via BaseModel (who invited, when, etc.)
    """

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        ACCEPTED = "accepted", _("Accepted")
        DECLINED = "declined", _("Declined")
        EXPIRED = "expired", _("Expired")
        CANCELLED = "cancelled", _("Cancelled")

    class Role(models.TextChoices):
        """
        Roles that can be assigned via invitation.
        Note: ORGANIZER is intentionally excluded for security.
        """
        PARENT = "parent", _("Parent")
        CHILD = "child", _("Child")

    # Invitation details
    inviter = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="sent_invitations",
        help_text="User who sent this invitation",
    )
    invitee_email = models.EmailField(
        help_text="Email address of the person being invited",
    )
    family = models.ForeignKey(
        "shared.Family",
        on_delete=models.CASCADE,
        related_name="invitations",
        help_text="Family the invitee is being invited to join",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        help_text="Role to be assigned upon acceptance (PARENT or CHILD only)",
    )

    # Invitation token and status
    token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        help_text="Unique token for invitation acceptance link",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        help_text="Current status of the invitation",
    )
    expires_at = models.DateTimeField(
        help_text="When this invitation expires (7 days from creation)",
    )

    class Meta:
        verbose_name = "Invitation"
        verbose_name_plural = "Invitations"
        ordering = ["-created_at"]
        # Prevent duplicate pending invitations for same email to same family
        constraints = [
            models.UniqueConstraint(
                fields=["family", "invitee_email"],
                condition=Q(status="pending"),
                name="unique_pending_invitation_per_family_email",
            ),
        ]
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["status", "expires_at"]),
            models.Index(fields=["family", "status"]),
        ]

    def save(self, *args, **kwargs):
        """
        Override save to auto-set expires_at to 7 days from now if not set.
        """
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    def clean(self):
        """
        Custom validation for Invitation model.

        Validates:
        - Email format (handled by EmailField)
        - Role is not ORGANIZER (security check)
        - Invitee is not already a family member
        """
        super().clean()

        # Prevent ORGANIZER role assignment via invitation
        if self.role == "organizer":
            raise ValidationError(
                {"role": "ORGANIZER role cannot be assigned via invitation for security reasons."}
            )

        # Prevent inviting existing family members
        if self.family_id and self.invitee_email:
            from apps.shared.models import FamilyMember

            # Check if a user with this email is already in the family
            existing_member = FamilyMember.objects.filter(
                family=self.family,
                user__email=self.invitee_email,
            ).exists()

            if existing_member:
                raise ValidationError(
                    {"invitee_email": f"{self.invitee_email} is already a member of {self.family.name}."}
                )

    @property
    def is_expired(self) -> bool:
        """
        Check if invitation has expired.

        Returns:
            bool: True if current time is past expires_at, False otherwise.
        """
        return timezone.now() > self.expires_at

    def __str__(self) -> str:
        """
        String representation of invitation.

        Returns:
            str: Human-readable invitation description.
        """
        return f"Invitation to {self.invitee_email} for {self.family.name} ({self.get_status_display()})"
