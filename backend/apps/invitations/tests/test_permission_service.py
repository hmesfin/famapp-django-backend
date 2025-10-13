"""
Tests for the PermissionService
Comprehensive test coverage for all permission checking methods

Ham Dog & TC's Testing Philosophy:
- Test all permission methods thoroughly
- Cover edge cases and role combinations
- Mock the role checking functions to control test scenarios
- Clear test organization by permission type
"""

from unittest.mock import patch, MagicMock
import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.invitations.services.permission_service import PermissionService
from apps.permissions.constants import RoleCodeName, PermissionCodeName

User = get_user_model()


class TestPermissionService(TestCase):
    """Test cases for PermissionService"""

    def setUp(self):
        """Set up test dependencies"""
        self.service = PermissionService()

        # Create test users
        self.superuser = User.objects.create_user(
            email="super@example.com", password="testpass123", is_superuser=True
        )

        self.admin_user = User.objects.create_user(
            email="admin@example.com", password="testpass123"
        )

        self.manager_user = User.objects.create_user(
            email="manager@example.com", password="testpass123"
        )

        self.regular_user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )

        self.anonymous_user = None

    # Helper methods for mocking role checks
    def mock_admin_role(self, user):
        """Mock user having admin role"""
        return user == self.admin_user or user == self.superuser

    def mock_manager_role(self, user):
        """Mock user having manager role"""
        return user in [self.manager_user, self.admin_user, self.superuser]

    def mock_no_role(self, user):
        """Mock user having no special roles"""
        return user == self.superuser  # Only superuser passes

    # Tests for can_send_invitations
    def test_can_send_invitations_superuser(self):
        """Superusers can always send invitations"""
        result = self.service.can_send_invitations(self.superuser)
        self.assertTrue(result)
        # No need to mock for superuser - early return

    def test_can_send_invitations_admin(self):
        """Admins can send invitations"""

        # Mock the service's instance methods directly
        def role_side_effect(user, role_name):
            if user == self.admin_user and role_name == RoleCodeName.ADMIN:
                return True
            return False

        self.service._user_has_role = MagicMock(side_effect=role_side_effect)
        self.service._user_has_permission = MagicMock(return_value=False)

        result = self.service.can_send_invitations(self.admin_user)
        self.assertTrue(result)

    def test_can_send_invitations_manager(self):
        """Managers can send invitations"""

        # Mock manager role = True for manager_user
        def role_side_effect(user, role_name):
            if user == self.manager_user and role_name == RoleCodeName.MANAGER:
                return True
            return False

        self.service._user_has_role = MagicMock(side_effect=role_side_effect)
        self.service._user_has_permission = MagicMock(return_value=False)

        result = self.service.can_send_invitations(self.manager_user)
        self.assertTrue(result)

    def test_can_send_invitations_permission(self):
        """Users with send_invitations permission can send"""

        # Mock permission = True when checking for SEND_INVITATIONS
        def permission_side_effect(user, perm_name):
            if (
                user == self.regular_user
                and perm_name == PermissionCodeName.SEND_INVITATIONS
            ):
                return True
            return False

        self.service._user_has_role = MagicMock(return_value=False)  # No roles
        self.service._user_has_permission = MagicMock(
            side_effect=permission_side_effect
        )

        result = self.service.can_send_invitations(self.regular_user)
        self.assertTrue(result)

    def test_can_send_invitations_regular_user_denied(self):
        """Regular users without roles/permissions cannot send"""
        self.service._user_has_role = MagicMock(return_value=False)
        self.service._user_has_permission = MagicMock(return_value=False)

        result = self.service.can_send_invitations(self.regular_user)
        self.assertFalse(result)

    def test_can_send_invitations_anonymous_denied(self):
        """Anonymous users cannot send invitations"""
        result = self.service.can_send_invitations(self.anonymous_user)
        self.assertFalse(result)

    # Tests for can_manage_all_invitations
    def test_can_manage_all_invitations_superuser(self):
        """Superusers can manage all invitations"""
        result = self.service.can_manage_all_invitations(self.superuser)
        self.assertTrue(result)

    def test_can_manage_all_invitations_admin(self):
        """Admins can manage all invitations"""

        # Mock admin role = True for admin_user
        def role_side_effect(user, role_name):
            if user == self.admin_user and role_name == RoleCodeName.ADMIN:
                return True
            return False

        self.service._user_has_role = MagicMock(side_effect=role_side_effect)
        self.service._user_has_permission = MagicMock(return_value=False)

        result = self.service.can_manage_all_invitations(self.admin_user)
        self.assertTrue(result)

    def test_can_manage_all_invitations_manager_denied(self):
        """Managers cannot manage all invitations (admin-only)"""
        self.service._user_has_role = MagicMock(return_value=False)  # No admin role
        self.service._user_has_permission = MagicMock(
            return_value=False
        )  # No manage permission

        result = self.service.can_manage_all_invitations(self.manager_user)
        self.assertFalse(result)

    def test_can_manage_all_invitations_permission(self):
        """Users with manage_invitations permission can manage all"""

        # Mock permission = True when checking for MANAGE_INVITATIONS
        def permission_side_effect(user, perm_name):
            if (
                user == self.regular_user
                and perm_name == PermissionCodeName.MANAGE_INVITATIONS
            ):
                return True
            return False

        self.service._user_has_role = MagicMock(return_value=False)  # No admin role
        self.service._user_has_permission = MagicMock(
            side_effect=permission_side_effect
        )

        result = self.service.can_manage_all_invitations(self.regular_user)
        self.assertTrue(result)

    # Tests for can_manage_own_invitations
    def test_can_manage_own_invitations_authenticated(self):
        """Any authenticated user can manage their own invitations"""
        result = self.service.can_manage_own_invitations(self.regular_user)
        self.assertTrue(result)

    def test_can_manage_own_invitations_anonymous_denied(self):
        """Anonymous users cannot manage invitations"""
        result = self.service.can_manage_own_invitations(self.anonymous_user)
        self.assertFalse(result)

    # Tests for can_manage_invitation (ownership-based)
    def test_can_manage_invitation_owner(self):
        """Users can manage invitations they sent"""
        # No need to mock for owner check - it's a simple equality
        result = self.service.can_manage_invitation(
            self.regular_user, self.regular_user
        )
        self.assertTrue(result)

    def test_can_manage_invitation_admin_other_user(self):
        """Admins can manage invitations sent by others"""

        # Mock admin role = True for admin_user
        def role_side_effect(user, role_name):
            if user == self.admin_user and role_name == RoleCodeName.ADMIN:
                return True
            return False

        self.service._user_has_role = MagicMock(side_effect=role_side_effect)
        self.service._user_has_permission = MagicMock(return_value=False)

        result = self.service.can_manage_invitation(self.admin_user, self.regular_user)
        self.assertTrue(result)

    def test_can_manage_invitation_regular_user_other_user_denied(self):
        """Regular users cannot manage invitations sent by others"""
        # No need to mock for this case - regular users can't manage others' invitations
        # This is determined purely by user equality check
        result = self.service.can_manage_invitation(
            self.regular_user, self.manager_user
        )
        self.assertFalse(result)

    # Tests for can_view_stats
    def test_can_view_stats_superuser(self):
        """Superusers can view stats"""
        result = self.service.can_view_stats(self.superuser)
        self.assertTrue(result)

    def test_can_view_stats_admin(self):
        """Admins can view stats"""

        def role_side_effect(user, role_name):
            if user == self.admin_user and role_name == RoleCodeName.ADMIN:
                return True
            return False

        self.service._user_has_role = MagicMock(side_effect=role_side_effect)

        result = self.service.can_view_stats(self.admin_user)
        self.assertTrue(result)

    def test_can_view_stats_manager(self):
        """Managers can view stats"""

        def role_side_effect(user, role_name):
            if user == self.manager_user and role_name == RoleCodeName.MANAGER:
                return True
            return False

        self.service._user_has_role = MagicMock(side_effect=role_side_effect)

        result = self.service.can_view_stats(self.manager_user)
        self.assertTrue(result)

    def test_can_view_stats_regular_user_denied(self):
        """Regular users cannot view stats"""
        self.service._user_has_role = MagicMock(return_value=False)

        result = self.service.can_view_stats(self.regular_user)
        self.assertFalse(result)

    # Tests for can_extend_expiry
    def test_can_extend_expiry_superuser(self):
        """Superusers can extend expiry"""
        result = self.service.can_extend_expiry(self.superuser)
        self.assertTrue(result)

    def test_can_extend_expiry_admin(self):
        """Admins can extend expiry"""

        def role_side_effect(user, role_name):
            if user == self.admin_user and role_name == RoleCodeName.ADMIN:
                return True
            return False

        self.service._user_has_role = MagicMock(side_effect=role_side_effect)

        result = self.service.can_extend_expiry(self.admin_user)
        self.assertTrue(result)

    def test_can_extend_expiry_manager_denied(self):
        """Managers cannot extend expiry (admin-only)"""
        self.service._user_has_role = MagicMock(return_value=False)

        result = self.service.can_extend_expiry(self.manager_user)
        self.assertFalse(result)

    # Tests for can_send_bulk_invitations
    def test_can_send_bulk_invitations_admin(self):
        """Admins can send bulk invitations"""

        def role_side_effect(user, role_name):
            if user == self.admin_user and role_name == RoleCodeName.ADMIN:
                return True
            return False

        self.service._user_has_role = MagicMock(side_effect=role_side_effect)

        result = self.service.can_send_bulk_invitations(self.admin_user)
        self.assertTrue(result)

    def test_can_send_bulk_invitations_manager(self):
        """Managers can send bulk invitations"""

        def role_side_effect(user, role_name):
            if user == self.manager_user and role_name == RoleCodeName.MANAGER:
                return True
            return False

        self.service._user_has_role = MagicMock(side_effect=role_side_effect)

        result = self.service.can_send_bulk_invitations(self.manager_user)
        self.assertTrue(result)

    def test_can_send_bulk_invitations_regular_user_denied(self):
        """Regular users cannot send bulk invitations"""
        self.service._user_has_role = MagicMock(return_value=False)

        result = self.service.can_send_bulk_invitations(self.regular_user)
        self.assertFalse(result)

    # Tests for can_view_all_invitations
    def test_can_view_all_invitations_admin(self):
        """Admins can view all invitations"""

        def role_side_effect(user, role_name):
            if user == self.admin_user and role_name == RoleCodeName.ADMIN:
                return True
            return False

        self.service._user_has_role = MagicMock(side_effect=role_side_effect)

        result = self.service.can_view_all_invitations(self.admin_user)
        self.assertTrue(result)

    def test_can_view_all_invitations_manager_denied(self):
        """Managers cannot view all invitations (admin-only)"""
        self.service._user_has_role = MagicMock(return_value=False)

        result = self.service.can_view_all_invitations(self.manager_user)
        self.assertFalse(result)

    # Tests for role checking methods
    def test_has_admin_role(self):
        """Test admin role checking"""

        def role_side_effect(user, role_name):
            if user == self.admin_user and role_name == RoleCodeName.ADMIN:
                return True
            return False

        self.service._user_has_role = MagicMock(side_effect=role_side_effect)

        result = self.service.has_admin_role(self.admin_user)
        self.assertTrue(result)
        self.service._user_has_role.assert_called_with(
            self.admin_user, RoleCodeName.ADMIN
        )

    def test_has_manager_role(self):
        """Test manager role checking"""

        # Mock manager=True for manager_user
        def role_side_effect(user, role_name):
            if user == self.manager_user and role_name == RoleCodeName.MANAGER:
                return True
            return False

        self.service._user_has_role = MagicMock(side_effect=role_side_effect)

        result = self.service.has_manager_role(self.manager_user)
        self.assertTrue(result)

    # Tests for get_permission_context
    def test_get_permission_context_authenticated(self):
        """Test permission context for authenticated user"""
        self.service._user_has_role = MagicMock(return_value=False)
        self.service._user_has_permission = MagicMock(return_value=False)

        context = self.service.get_permission_context(self.regular_user)

        self.assertTrue(context["is_authenticated"])
        self.assertFalse(context["is_superuser"])
        self.assertIn("can_send_invitations", context)
        self.assertIn("can_manage_all_invitations", context)
        self.assertIn("can_view_stats", context)

    def test_get_permission_context_anonymous(self):
        """Test permission context for anonymous user"""
        context = self.service.get_permission_context(self.anonymous_user)

        self.assertFalse(context["is_authenticated"])
        self.assertFalse(context["can_send_invitations"])
        self.assertFalse(context["can_manage_all_invitations"])
        self.assertFalse(context["can_view_stats"])

    # Tests for require_* methods (permission enforcement)
    def test_require_send_invitations_permission_success(self):
        """Test permission enforcement passes when user has permission"""

        # Mock admin role = True for admin_user
        def role_side_effect(user, role_name):
            if user == self.admin_user and role_name == RoleCodeName.ADMIN:
                return True
            return False

        self.service._user_has_role = MagicMock(side_effect=role_side_effect)
        self.service._user_has_permission = MagicMock(return_value=False)

        # Should not raise exception
        self.service.require_send_invitations_permission(self.admin_user)

    def test_require_send_invitations_permission_denied(self):
        """Test permission enforcement raises error when user lacks permission"""
        self.service._user_has_role = MagicMock(return_value=False)
        self.service._user_has_permission = MagicMock(return_value=False)

        with self.assertRaises(PermissionError) as cm:
            self.service.require_send_invitations_permission(self.regular_user)

        self.assertIn("permission to send invitations", str(cm.exception))

    def test_require_stats_permission_denied(self):
        """Test stats permission enforcement"""
        self.service._user_has_role = MagicMock(return_value=False)
        self.service._user_has_permission = MagicMock(return_value=False)

        with self.assertRaises(PermissionError) as cm:
            self.service.require_stats_permission(self.regular_user)

        self.assertIn("permission to view statistics", str(cm.exception))

    def test_require_extend_expiry_permission_denied(self):
        """Test expiry extension permission enforcement"""
        self.service._user_has_role = MagicMock(return_value=False)

        with self.assertRaises(PermissionError) as cm:
            self.service.require_extend_expiry_permission(self.regular_user)

        self.assertIn("administrators can extend", str(cm.exception))

    def test_require_bulk_invitations_permission_denied(self):
        """Test bulk invitations permission enforcement"""
        self.service._user_has_role = MagicMock(return_value=False)

        with self.assertRaises(PermissionError) as cm:
            self.service.require_bulk_invitations_permission(self.regular_user)

        self.assertIn("permission to send bulk invitations", str(cm.exception))

    # Edge cases and error handling
    def test_all_methods_handle_none_user(self):
        """Test all methods gracefully handle None user"""
        methods_to_test = [
            "can_send_invitations",
            "can_manage_all_invitations",
            "can_manage_own_invitations",
            "can_view_stats",
            "can_extend_expiry",
            "can_send_bulk_invitations",
            "can_view_all_invitations",
            "has_admin_role",
            "has_manager_role",
        ]

        for method_name in methods_to_test:
            method = getattr(self.service, method_name)
            result = method(None)
            self.assertFalse(result, f"{method_name} should return False for None user")

    def test_can_manage_invitation_with_none_users(self):
        """Test can_manage_invitation handles None users"""
        self.service._user_has_role = MagicMock(
            return_value=False
        )  # No admin role for regular user
        self.service._user_has_permission = MagicMock(return_value=False)

        result = self.service.can_manage_invitation(None, self.regular_user)
        self.assertFalse(result)

        # Test with None owner - regular user cannot manage (owner != user, no admin permissions)
        result = self.service.can_manage_invitation(self.regular_user, None)
        self.assertFalse(result)  # Regular user can't manage orphaned invitations

        # But an admin can manage invitations with None owner
        def role_side_effect(user, role_name):
            if user == self.admin_user and role_name == RoleCodeName.ADMIN:
                return True
            return False

        self.service._user_has_role = MagicMock(side_effect=role_side_effect)
        result = self.service.can_manage_invitation(self.admin_user, None)
        self.assertTrue(result)  # Admin can manage orphaned invitations
