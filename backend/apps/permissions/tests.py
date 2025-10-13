"""
Tests for RBAC System
Ham Dog & TC's Comprehensive Permission Testing Suite

Following the Ten Commandments:
- Test all the things!
- Make sure our RBAC system is bulletproof
- Document expected behavior through tests
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from .models import Permission, Role, UserRole, Resource, UserPermission


User = get_user_model()


class PermissionModelTest(TestCase):
    """Test the Permission model."""
    
    def test_permission_creation(self):
        """Test creating a permission."""
        permission = Permission.objects.create(
            code_name='test_permission',
            name='Test Permission',
            description='A test permission',
            category='testing'
        )
        
        self.assertEqual(str(permission), 'Test Permission (test_permission)')
        self.assertTrue(permission.is_active)
        self.assertEqual(permission.category, 'testing')
    
    def test_permission_unique_code_name(self):
        """Test that permission code names must be unique."""
        Permission.objects.create(
            code_name='test_permission',
            name='Test Permission 1'
        )
        
        with self.assertRaises(Exception):
            Permission.objects.create(
                code_name='test_permission',
                name='Test Permission 2'
            )


class RoleModelTest(TestCase):
    """Test the Role model."""
    
    def setUp(self):
        """Set up test data."""
        self.permission1 = Permission.objects.create(
            code_name='perm1',
            name='Permission 1'
        )
        self.permission2 = Permission.objects.create(
            code_name='perm2',
            name='Permission 2'
        )
    
    def test_role_creation(self):
        """Test creating a role."""
        role = Role.objects.create(
            code_name='test_role',
            name='Test Role',
            description='A test role'
        )
        
        self.assertEqual(str(role), 'Test Role (test_role)')
        self.assertTrue(role.is_active)
        self.assertFalse(role.is_system_role)
    
    def test_role_permissions(self):
        """Test role permission management."""
        role = Role.objects.create(
            code_name='test_role',
            name='Test Role'
        )
        
        # Add permissions to role
        role.permissions.add(self.permission1, self.permission2)
        
        self.assertEqual(role.permissions.count(), 2)
        self.assertIn(self.permission1, role.permissions.all())
        self.assertIn(self.permission2, role.permissions.all())
    
    def test_role_has_permission(self):
        """Test the has_permission method."""
        role = Role.objects.create(
            code_name='test_role',
            name='Test Role'
        )
        role.permissions.add(self.permission1)
        
        self.assertTrue(role.has_permission('perm1'))
        self.assertFalse(role.has_permission('perm2'))
    
    def test_get_permission_codes(self):
        """Test getting permission codes for a role."""
        role = Role.objects.create(
            code_name='test_role',
            name='Test Role'
        )
        role.permissions.add(self.permission1, self.permission2)
        
        codes = role.get_permission_codes()
        self.assertIn('perm1', codes)
        self.assertIn('perm2', codes)
        self.assertEqual(len(codes), 2)


class UserRBACTest(TestCase):
    """Test RBAC functionality on the User model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.permission1 = Permission.objects.create(
            code_name='view_content',
            name='View Content'
        )
        self.permission2 = Permission.objects.create(
            code_name='edit_content',
            name='Edit Content'
        )
        
        self.role = Role.objects.create(
            code_name='editor',
            name='Editor'
        )
        self.role.permissions.add(self.permission1, self.permission2)
    
    def test_user_role_assignment(self):
        """Test assigning roles to users."""
        user_role = self.user.assign_role(self.role)
        
        self.assertIsInstance(user_role, UserRole)
        self.assertEqual(user_role.user, self.user)
        self.assertEqual(user_role.role, self.role)
        self.assertTrue(user_role.is_active)
        self.assertTrue(user_role.is_valid())
    
    def test_user_has_role(self):
        """Test checking if user has a role."""
        self.assertFalse(self.user.has_role('editor'))
        
        self.user.assign_role(self.role)
        self.assertTrue(self.user.has_role('editor'))
    
    def test_user_has_permission_via_role(self):
        """Test user permissions via role assignment."""
        self.assertFalse(self.user.has_permission('view_content'))
        
        self.user.assign_role(self.role)
        self.assertTrue(self.user.has_permission('view_content'))
        self.assertTrue(self.user.has_permission('edit_content'))
        self.assertFalse(self.user.has_permission('delete_content'))
    
    def test_user_direct_permission(self):
        """Test direct permission assignment to users."""
        permission = Permission.objects.create(
            code_name='special_permission',
            name='Special Permission'
        )
        
        self.assertFalse(self.user.has_permission('special_permission'))
        
        user_permission = self.user.grant_permission(permission)
        self.assertIsInstance(user_permission, UserPermission)
        self.assertTrue(self.user.has_permission('special_permission'))
    
    def test_user_role_removal(self):
        """Test removing roles from users."""
        self.user.assign_role(self.role)
        self.assertTrue(self.user.has_role('editor'))
        
        success = self.user.remove_role(self.role)
        self.assertTrue(success)
        self.assertFalse(self.user.has_role('editor'))
    
    def test_user_permission_revocation(self):
        """Test revoking direct permissions from users."""
        permission = Permission.objects.create(
            code_name='revokable_permission',
            name='Revokable Permission'
        )
        
        self.user.grant_permission(permission)
        self.assertTrue(self.user.has_permission('revokable_permission'))
        
        success = self.user.revoke_permission(permission)
        self.assertTrue(success)
        self.assertFalse(self.user.has_permission('revokable_permission'))
    
    def test_expired_role_assignment(self):
        """Test expired role assignments."""
        past_time = timezone.now() - timedelta(days=1)
        
        user_role = self.user.assign_role(
            self.role,
            expires_at=past_time
        )
        
        self.assertTrue(user_role.is_expired())
        self.assertFalse(user_role.is_valid())
        # User should not have permissions from expired role
        self.assertFalse(self.user.has_permission('view_content'))
    
    def test_inactive_role_assignment(self):
        """Test inactive role assignments."""
        user_role = self.user.assign_role(self.role)
        user_role.is_active = False
        user_role.save()
        
        self.assertFalse(user_role.is_valid())
        self.assertFalse(self.user.has_role('editor'))
    
    def test_get_active_roles(self):
        """Test getting active roles for a user."""
        role2 = Role.objects.create(
            code_name='manager',
            name='Manager'
        )
        
        # Assign active role
        self.user.assign_role(self.role)
        
        # Assign inactive role
        user_role2 = self.user.assign_role(role2)
        user_role2.is_active = False
        user_role2.save()
        
        active_roles = self.user.get_active_roles()
        self.assertEqual(len(active_roles), 1)
        self.assertEqual(active_roles[0], self.role)
    
    def test_get_all_permissions(self):
        """Test getting all permissions for a user."""
        # Permission via role
        self.user.assign_role(self.role)
        
        # Direct permission
        direct_permission = Permission.objects.create(
            code_name='direct_perm',
            name='Direct Permission'
        )
        self.user.grant_permission(direct_permission)
        
        all_permissions = self.user.get_all_permissions()
        permission_codes = [p.code_name for p in all_permissions]
        
        self.assertIn('view_content', permission_codes)
        self.assertIn('edit_content', permission_codes)
        self.assertIn('direct_perm', permission_codes)


class ResourcePermissionTest(TestCase):
    """Test resource-specific permissions."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.permission = Permission.objects.create(
            code_name='edit_article',
            name='Edit Article'
        )
        
        self.resource = Resource.objects.create(
            resource_type='article',
            resource_id='123',
            name='Test Article'
        )
    
    def test_resource_specific_permission(self):
        """Test granting permission for specific resource."""
        # User doesn't have permission initially
        self.assertFalse(self.user.has_permission('edit_article', self.resource))
        
        # Grant permission for specific resource
        self.user.grant_permission(self.permission, resource=self.resource)
        
        # User now has permission for this resource
        self.assertTrue(self.user.has_permission('edit_article', self.resource))
        
        # But not for other resources or general permission
        other_resource = Resource.objects.create(
            resource_type='article',
            resource_id='456',
            name='Other Article'
        )
        self.assertFalse(self.user.has_permission('edit_article', other_resource))
        self.assertFalse(self.user.has_permission('edit_article'))  # No resource specified
