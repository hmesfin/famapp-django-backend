"""
Custom permissions for the invitations app
Only admins and managers can send invitations!
"""

from rest_framework import permissions
from apps.permissions.models import UserRole
from apps.permissions.constants import RoleCodeName, PermissionCodeName


class CanSendInvitations(permissions.BasePermission):
    """
    Permission to check if user can send invitations.
    Only admins and managers have this permission.
    """

    message = "You don't have permission to send invitations. Only administrators and managers can send invitations."

    def has_permission(self, request, view):
        """Check if user has permission to send invitations"""
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers always have permission
        if request.user.is_superuser:
            return True

        # Check if user has admin or manager role
        user_roles = UserRole.objects.filter(
            user=request.user,
            is_active=True,
            role__is_active=True,
            role__code_name__in=[RoleCodeName.ADMIN, RoleCodeName.MANAGER],
        )

        # Check if any of the user's roles are valid (not expired)
        for user_role in user_roles:
            if user_role.is_valid():
                return True

        # Alternative: Check if user has specific permission through any role
        user_roles_with_permission = UserRole.objects.filter(
            user=request.user,
            is_active=True,
            role__is_active=True,
            role__permissions__code_name=PermissionCodeName.SEND_INVITATIONS,
            role__permissions__is_active=True,
        )

        for user_role in user_roles_with_permission:
            if user_role.is_valid():
                return True

        return False


class CanManageInvitations(permissions.BasePermission):
    """
    Permission to manage all invitations (resend, cancel, etc).
    Only admins have this permission.
    """

    message = "You don't have permission to manage invitations. Only administrators can manage all invitations."

    def has_permission(self, request, view):
        """Check if user has permission to manage invitations"""
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers always have permission
        if request.user.is_superuser:
            return True

        # Check if user has admin role
        admin_roles = UserRole.objects.filter(
            user=request.user,
            is_active=True,
            role__is_active=True,
            role__code_name=RoleCodeName.ADMIN,
        )

        for user_role in admin_roles:
            if user_role.is_valid():
                return True

        # Alternative: Check for specific permission
        user_roles_with_permission = UserRole.objects.filter(
            user=request.user,
            is_active=True,
            role__is_active=True,
            role__permissions__code_name=PermissionCodeName.MANAGE_INVITATIONS,
            role__permissions__is_active=True,
        )

        for user_role in user_roles_with_permission:
            if user_role.is_valid():
                return True

        return False

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission check.
        Users can manage invitations they sent, admins can manage all.
        """
        # If user has general manage permission, they can manage any invitation
        if self.has_permission(request, view):
            return True

        # Otherwise, users can only manage invitations they sent
        return obj.invited_by == request.user


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission that allows users to view/edit their own sent invitations,
    or admins to view/edit all invitations.
    """

    def has_object_permission(self, request, view, obj):
        """Check object-level permissions"""
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers have full access
        if request.user.is_superuser:
            return True

        # Owner can always access their own invitations
        if obj.invited_by == request.user:
            return True

        # Check if user is admin
        admin_roles = UserRole.objects.filter(
            user=request.user,
            is_active=True,
            role__is_active=True,
            role__code_name=RoleCodeName.ADMIN,
        )

        for user_role in admin_roles:
            if user_role.is_valid():
                return True

        return False


def user_has_role(user, role_code_name):
    """
    Utility function to check if a user has a specific role.

    Args:
        user: The user to check
        role_code_name: The code name of the role to check for

    Returns:
        bool: True if user has the role and it's valid, False otherwise
    """
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    user_roles = UserRole.objects.filter(
        user=user, is_active=True, role__is_active=True, role__code_name=role_code_name
    )

    for user_role in user_roles:
        if user_role.is_valid():
            return True

    return False


def user_has_permission(user, permission_code_name):
    """
    Utility function to check if a user has a specific permission.

    Args:
        user: The user to check
        permission_code_name: The code name of the permission to check for

    Returns:
        bool: True if user has the permission through any valid role, False otherwise
    """
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    user_roles = UserRole.objects.filter(
        user=user,
        is_active=True,
        role__is_active=True,
        role__permissions__code_name=permission_code_name,
        role__permissions__is_active=True,
    )

    for user_role in user_roles:
        if user_role.is_valid():
            return True

    return False
