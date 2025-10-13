"""
RBAC Models for the DjVue Orchestra
Ham Dog & TC's Flexible Role-Based Access Control System

Following the Ten Commandments:
- Commandment #1: UUIDs for external references (but keeping bigint for performance)
- Commandment #7: DRY principles with our blessed abstract models
"""
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models import SimpleBaseModel


User = get_user_model()


class Permission(SimpleBaseModel):
    """
    Custom permission model for flexible RBAC.
    
    Unlike Django's built-in permissions, these can be dynamically created
    by users and don't need to be tied to specific models.
    """
    code_name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_("Unique permission identifier (e.g., 'view_reports')")
    )
    name = models.CharField(
        max_length=255,
        help_text=_("Human-readable permission name")
    )
    description = models.TextField(
        blank=True,
        help_text=_("Detailed description of what this permission allows")
    )
    category = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Permission category for organization (e.g., 'reporting', 'admin')")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this permission is currently active")
    )

    class Meta:
        ordering = ['category', 'name']
        verbose_name = _("Permission")
        verbose_name_plural = _("Permissions")

    def __str__(self):
        return f"{self.name} ({self.code_name})"


class Role(SimpleBaseModel):
    """
    Role model that groups permissions together.
    
    Roles provide a way to assign multiple permissions to users
    in meaningful groups (e.g., 'Manager', 'Editor', 'Viewer').
    """
    code_name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_("Unique role identifier (e.g., 'content_manager')")
    )
    name = models.CharField(
        max_length=255,
        help_text=_("Human-readable role name")
    )
    description = models.TextField(
        blank=True,
        help_text=_("Description of the role and its responsibilities")
    )
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='roles',
        help_text=_("Permissions granted by this role")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this role is currently active")
    )
    is_system_role = models.BooleanField(
        default=False,
        help_text=_("System roles cannot be deleted by users")
    )

    class Meta:
        ordering = ['name']
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")

    def __str__(self):
        return f"{self.name} ({self.code_name})"

    def get_permission_codes(self):
        """Get list of permission code names for this role."""
        return list(self.permissions.filter(is_active=True).values_list('code_name', flat=True))

    def has_permission(self, permission_code):
        """Check if this role has a specific permission."""
        return self.permissions.filter(code_name=permission_code, is_active=True).exists()


class UserRole(SimpleBaseModel):
    """
    Through model for user-role assignments with additional context.
    
    This allows for more flexible role assignments with metadata
    like expiration dates, assignment context, etc.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_assignments'
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='role_assignments_made',
        help_text=_("User who assigned this role")
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When this role assignment expires (optional)")
    )
    context = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Additional context for this role assignment")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this role assignment is currently active")
    )

    class Meta:
        unique_together = ['user', 'role']
        ordering = ['-created_at']
        verbose_name = _("User Role Assignment")
        verbose_name_plural = _("User Role Assignments")

    def __str__(self):
        return f"{self.user} -> {self.role.name}"

    def is_expired(self):
        """Check if this role assignment has expired."""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def is_valid(self):
        """Check if this role assignment is currently valid."""
        return self.is_active and not self.is_expired() and self.role.is_active


class Resource(SimpleBaseModel):
    """
    Optional: Specific resources that permissions can be applied to.
    
    This allows for more granular permissions like "can edit article #123"
    rather than just "can edit articles".
    """
    resource_type = models.CharField(
        max_length=100,
        help_text=_("Type of resource (e.g., 'article', 'project', 'document')")
    )
    resource_id = models.CharField(
        max_length=255,
        help_text=_("Identifier for the specific resource")
    )
    name = models.CharField(
        max_length=255,
        help_text=_("Human-readable resource name")
    )
    description = models.TextField(
        blank=True,
        help_text=_("Description of this resource")
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Additional metadata about this resource")
    )

    class Meta:
        unique_together = ['resource_type', 'resource_id']
        ordering = ['resource_type', 'name']
        verbose_name = _("Resource")
        verbose_name_plural = _("Resources")

    def __str__(self):
        return f"{self.resource_type}:{self.resource_id} ({self.name})"


class UserPermission(SimpleBaseModel):
    """
    Direct user-permission assignments (bypass roles).
    
    Sometimes you need to grant specific permissions to specific users
    without creating a whole role for it.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='direct_permissions'
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='direct_assignments'
    )
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text=_("Specific resource this permission applies to (optional)")
    )
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='permissions_granted',
        help_text=_("User who granted this permission")
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When this permission expires (optional)")
    )
    context = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Additional context for this permission assignment")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this permission is currently active")
    )

    class Meta:
        unique_together = ['user', 'permission', 'resource']
        ordering = ['-created_at']
        verbose_name = _("User Permission")
        verbose_name_plural = _("User Permissions")

    def __str__(self):
        resource_str = f" on {self.resource}" if self.resource else ""
        return f"{self.user} -> {self.permission.code_name}{resource_str}"

    def is_expired(self):
        """Check if this permission has expired."""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def is_valid(self):
        """Check if this permission is currently valid."""
        return self.is_active and not self.is_expired() and self.permission.is_active