from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db.models import BooleanField
from django.db.models import CharField
from django.db.models import EmailField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

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
        return reverse("users:detail", kwargs={"pk": self.public_id})

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
