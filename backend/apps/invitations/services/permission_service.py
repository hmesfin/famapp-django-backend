"""
Centralized permission service for the invitations app
Single source of truth for all invitation-related permission checks

Ham Dog & TC's Permission Philosophy:
- All permission logic centralized in one place
- Clear, testable permission methods
- Consistent role and permission checking
- Separation of concerns from business logic
"""

from typing import TYPE_CHECKING
from django.contrib.auth import get_user_model

# Import permission utilities and constants
from apps.invitations.permissions import user_has_role, user_has_permission
from apps.permissions.constants import RoleCodeName, PermissionCodeName

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

User = get_user_model()


class PermissionService:
    """
    Centralized service for handling all invitation-related permissions

    Provides methods to check:
    - Invitation sending permissions
    - Invitation management permissions
    - Statistics viewing permissions
    - Expiry extension permissions
    - Role-based access control

    All permission logic is consolidated here to avoid duplication
    and ensure consistent permission checking across the app.
    """

    # Role constants - centralized here
    class Roles:
        ADMIN = "admin"
        MANAGER = "manager"
        MEMBER = "member"

    def __init__(self):
        """Initialize the permission service"""
        # No need to import here anymore - moved to module level
        self._user_has_role = user_has_role
        self._user_has_permission = user_has_permission
        self._roles = RoleCodeName
        self._permissions = PermissionCodeName

    def can_send_invitations(self, user: "AbstractUser") -> bool:
        """
        Check if user can send invitations

        Args:
            user: User to check permissions for

        Returns:
            bool: True if user can send invitations
        """
        if not user or not user.is_authenticated:
            return False

        # Superusers can always send invitations
        if user.is_superuser:
            return True

        # Check for admin or manager roles
        return (
            self._user_has_role(user, self._roles.ADMIN)
            or self._user_has_role(user, self._roles.MANAGER)
            or self._user_has_permission(user, self._permissions.SEND_INVITATIONS)
        )

    def can_manage_all_invitations(self, user: "AbstractUser") -> bool:
        """
        Check if user can manage all invitations (admin-level access)

        Args:
            user: User to check permissions for

        Returns:
            bool: True if user can manage all invitations
        """
        if not user or not user.is_authenticated:
            return False

        # Superusers can always manage all invitations
        if user.is_superuser:
            return True

        # Only admins can manage all invitations
        return self._user_has_role(
            user, self._roles.ADMIN
        ) or self._user_has_permission(user, self._permissions.MANAGE_INVITATIONS)

    def can_manage_own_invitations(self, user: "AbstractUser") -> bool:
        """
        Check if user can manage their own invitations

        Args:
            user: User to check permissions for

        Returns:
            bool: True if user can manage their own invitations
        """
        if not user or not user.is_authenticated:
            return False

        # Any authenticated user can manage their own invitations
        return True

    def can_manage_invitation(
        self, user: "AbstractUser", invitation_owner: "AbstractUser"
    ) -> bool:
        """
        Check if user can manage a specific invitation based on ownership

        Args:
            user: User requesting access
            invitation_owner: User who sent the invitation

        Returns:
            bool: True if user can manage the invitation
        """
        if not user or not user.is_authenticated:
            return False

        # User can manage their own invitations
        if user == invitation_owner:
            return True

        # Admins can manage all invitations
        return self.can_manage_all_invitations(user)

    def can_view_stats(self, user: "AbstractUser") -> bool:
        """
        Check if user can view invitation statistics

        Args:
            user: User to check permissions for

        Returns:
            bool: True if user can view statistics
        """
        if not user or not user.is_authenticated:
            return False

        # Superusers can always view stats
        if user.is_superuser:
            return True

        # Admins and managers can view stats
        return self._user_has_role(user, self._roles.ADMIN) or self._user_has_role(
            user, self._roles.MANAGER
        )

    def can_extend_expiry(self, user: "AbstractUser") -> bool:
        """
        Check if user can extend invitation expiry dates

        Args:
            user: User to check permissions for

        Returns:
            bool: True if user can extend expiry dates
        """
        if not user or not user.is_authenticated:
            return False

        # Superusers can always extend expiry
        if user.is_superuser:
            return True

        # Only admins can extend expiry
        return self._user_has_role(user, self._roles.ADMIN)

    def can_send_bulk_invitations(self, user: "AbstractUser") -> bool:
        """
        Check if user can send bulk invitations

        Args:
            user: User to check permissions for

        Returns:
            bool: True if user can send bulk invitations
        """
        if not user or not user.is_authenticated:
            return False

        # Superusers can always send bulk invitations
        if user.is_superuser:
            return True

        # Admins and managers can send bulk invitations
        return self._user_has_role(user, self._roles.ADMIN) or self._user_has_role(
            user, self._roles.MANAGER
        )

    def can_view_all_invitations(self, user: "AbstractUser") -> bool:
        """
        Check if user can view all invitations (not just their own)

        Args:
            user: User to check permissions for

        Returns:
            bool: True if user can view all invitations
        """
        if not user or not user.is_authenticated:
            return False

        # Superusers can view all invitations
        if user.is_superuser:
            return True

        # Admins can view all invitations
        return self._user_has_role(user, self._roles.ADMIN)

    def has_admin_role(self, user: "AbstractUser") -> bool:
        """
        Check if user has admin role

        Args:
            user: User to check

        Returns:
            bool: True if user is admin
        """
        if not user or not user.is_authenticated:
            return False

        return user.is_superuser or self._user_has_role(user, self._roles.ADMIN)

    def has_manager_role(self, user: "AbstractUser") -> bool:
        """
        Check if user has manager role

        Args:
            user: User to check

        Returns:
            bool: True if user is manager
        """
        if not user or not user.is_authenticated:
            return False

        return (
            user.is_superuser
            or self._user_has_role(user, self._roles.ADMIN)
            or self._user_has_role(user, self._roles.MANAGER)
        )

    def get_permission_context(self, user: "AbstractUser") -> dict:
        """
        Get comprehensive permission context for a user
        Useful for frontend permission handling and debugging

        Args:
            user: User to get context for

        Returns:
            dict: Dictionary of all permission flags
        """
        if not user or not user.is_authenticated:
            return {
                "is_authenticated": False,
                "can_send_invitations": False,
                "can_manage_all_invitations": False,
                "can_manage_own_invitations": False,
                "can_view_stats": False,
                "can_extend_expiry": False,
                "can_send_bulk_invitations": False,
                "can_view_all_invitations": False,
                "has_admin_role": False,
                "has_manager_role": False,
            }

        return {
            "is_authenticated": True,
            "is_superuser": user.is_superuser,
            "can_send_invitations": self.can_send_invitations(user),
            "can_manage_all_invitations": self.can_manage_all_invitations(user),
            "can_manage_own_invitations": self.can_manage_own_invitations(user),
            "can_view_stats": self.can_view_stats(user),
            "can_extend_expiry": self.can_extend_expiry(user),
            "can_send_bulk_invitations": self.can_send_bulk_invitations(user),
            "can_view_all_invitations": self.can_view_all_invitations(user),
            "has_admin_role": self.has_admin_role(user),
            "has_manager_role": self.has_manager_role(user),
        }

    def require_send_invitations_permission(self, user: "AbstractUser") -> None:
        """
        Raise permission error if user cannot send invitations

        Args:
            user: User to check

        Raises:
            PermissionError: If user lacks permission
        """
        if not self.can_send_invitations(user):
            raise PermissionError("You do not have permission to send invitations")

    def require_manage_all_invitations_permission(self, user: "AbstractUser") -> None:
        """
        Raise permission error if user cannot manage all invitations

        Args:
            user: User to check

        Raises:
            PermissionError: If user lacks permission
        """
        if not self.can_manage_all_invitations(user):
            raise PermissionError(
                "You do not have permission to manage all invitations"
            )

    def require_stats_permission(self, user: "AbstractUser") -> None:
        """
        Raise permission error if user cannot view stats

        Args:
            user: User to check

        Raises:
            PermissionError: If user lacks permission
        """
        if not self.can_view_stats(user):
            raise PermissionError("You do not have permission to view statistics")

    def require_extend_expiry_permission(self, user: "AbstractUser") -> None:
        """
        Raise permission error if user cannot extend expiry

        Args:
            user: User to check

        Raises:
            PermissionError: If user lacks permission
        """
        if not self.can_extend_expiry(user):
            raise PermissionError("Only administrators can extend invitation expiry")

    def require_bulk_invitations_permission(self, user: "AbstractUser") -> None:
        """
        Raise permission error if user cannot send bulk invitations

        Args:
            user: User to check

        Raises:
            PermissionError: If user lacks permission
        """
        if not self.can_send_bulk_invitations(user):
            raise PermissionError("You do not have permission to send bulk invitations")
