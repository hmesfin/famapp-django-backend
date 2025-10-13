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
        return self.get_full_name()

    # RBAC Methods
    def get_active_roles(self):
        """Get all active roles for this user."""
        return [
            ur.role for ur in self.user_roles.filter(is_active=True) if ur.is_valid()
        ]

    def get_all_permissions(self):
        """Get all permissions for this user (via roles + direct permissions)."""
        from apps.permissions.models import Permission

        # Permissions from roles
        role_permissions = Permission.objects.filter(
            roles__user_assignments__user=self,
            roles__user_assignments__is_active=True,
            roles__is_active=True,
            is_active=True,
        ).distinct()

        # Direct permissions
        direct_permissions = Permission.objects.filter(
            direct_assignments__user=self,
            direct_assignments__is_active=True,
            is_active=True,
        ).distinct()

        # Combine and return unique permissions
        return (role_permissions | direct_permissions).distinct()

    def has_permission(self, permission_code, resource=None):
        """
        Check if user has a specific permission.

        Args:
            permission_code (str): The permission code to check
            resource: Optional resource object to check permission against

        Returns:
            bool: True if user has the permission
        """
        # Check role-based permissions (only from valid, non-expired roles)
        for user_role in self.user_roles.filter(is_active=True, role__is_active=True):
            if user_role.is_valid() and user_role.role.has_permission(permission_code):
                return True

        # Check direct permissions (only valid, non-expired ones)
        direct_perms = self.direct_permissions.filter(
            is_active=True,
            permission__code_name=permission_code,
            permission__is_active=True,
        )

        if resource:
            # Check resource-specific permissions
            direct_perms = direct_perms.filter(resource=resource)
        else:
            # Check general permissions (no resource specified)
            direct_perms = direct_perms.filter(resource__isnull=True)

        # Check if any of the direct permissions are valid (not expired)
        for user_perm in direct_perms:
            if user_perm.is_valid():
                return True

        return False

    def has_role(self, role_code):
        """
        Check if user has a specific role.

        Args:
            role_code (str): The role code to check

        Returns:
            bool: True if user has the role
        """
        for user_role in self.user_roles.filter(
            is_active=True,
            role__code_name=role_code,
            role__is_active=True,
        ):
            if user_role.is_valid():
                return True
        return False

    def assign_role(self, role, assigned_by=None, expires_at=None, context=None):
        """
        Assign a role to this user.

        Args:
            role: Role object to assign
            assigned_by: User who is assigning the role (optional)
            expires_at: When the role assignment expires (optional)
            context: Additional context dict (optional)

        Returns:
            UserRole: The created user role assignment
        """
        from apps.permissions.models import UserRole

        user_role, created = UserRole.objects.get_or_create(
            user=self,
            role=role,
            defaults={
                "assigned_by": assigned_by,
                "expires_at": expires_at,
                "context": context or {},
            },
        )

        if not created and not user_role.is_active:
            # Reactivate existing inactive assignment
            user_role.is_active = True
            user_role.assigned_by = assigned_by
            user_role.expires_at = expires_at
            user_role.context = context or {}
            user_role.save()

        return user_role

    def remove_role(self, role):
        """
        Remove a role from this user.

        Args:
            role: Role object to remove

        Returns:
            bool: True if role was removed, False if user didn't have the role
        """
        try:
            user_role = self.user_roles.get(role=role, is_active=True)
            user_role.is_active = False
            user_role.save()
            return True
        except self.user_roles.model.DoesNotExist:
            return False

    def grant_permission(
        self, permission, resource=None, granted_by=None, expires_at=None, context=None
    ):
        """
        Grant a direct permission to this user.

        Args:
            permission: Permission object to grant
            resource: Optional resource the permission applies to
            granted_by: User who is granting the permission (optional)
            expires_at: When the permission expires (optional)
            context: Additional context dict (optional)

        Returns:
            UserPermission: The created user permission
        """
        from apps.permissions.models import UserPermission

        user_permission, created = UserPermission.objects.get_or_create(
            user=self,
            permission=permission,
            resource=resource,
            defaults={
                "granted_by": granted_by,
                "expires_at": expires_at,
                "context": context or {},
            },
        )

        if not created and not user_permission.is_active:
            # Reactivate existing inactive permission
            user_permission.is_active = True
            user_permission.granted_by = granted_by
            user_permission.expires_at = expires_at
            user_permission.context = context or {}
            user_permission.save()

        return user_permission

    def revoke_permission(self, permission, resource=None):
        """
        Revoke a direct permission from this user.

        Args:
            permission: Permission object to revoke
            resource: Optional resource the permission applies to

        Returns:
            bool: True if permission was revoked, False if user didn't have it
        """
        try:
            user_permission = self.direct_permissions.get(
                permission=permission,
                resource=resource,
                is_active=True,
            )
            user_permission.is_active = False
            user_permission.save()
            return True
        except self.direct_permissions.model.DoesNotExist:
            return False
