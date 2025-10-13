"""
Django Management Command to Seed RBAC System
Ham Dog & TC's Bootstrapping Command for Template Users

Following the Ten Commandments:
- Make it easy to get started with sensible defaults
- Provide flexibility for users to customize
- Document everything for the template users
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.permissions.models import Permission, Role


class Command(BaseCommand):
    help = 'Seed the RBAC system with basic permissions and roles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing permissions and roles before seeding',
        )
        parser.add_argument(
            '--permissions-only',
            action='store_true',
            help='Only seed permissions, not roles',
        )
        parser.add_argument(
            '--roles-only',
            action='store_true',
            help='Only seed roles, not permissions',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.HTTP_INFO('🎭 Seeding RBAC System for DjVue Orchestra')
        )

        if options['clear']:
            self._clear_existing_data()

        with transaction.atomic():
            if not options['roles_only']:
                self._seed_permissions()
            
            if not options['permissions_only']:
                self._seed_roles()

        self.stdout.write(
            self.style.SUCCESS('✅ RBAC system seeded successfully!')
        )

    def _clear_existing_data(self):
        """Clear existing permissions and roles."""
        self.stdout.write('🧹 Clearing existing RBAC data...')
        
        # Only clear non-system roles
        roles_deleted = Role.objects.filter(is_system_role=False).delete()[0]
        permissions_deleted = Permission.objects.all().delete()[0]
        
        self.stdout.write(
            f'   Deleted {permissions_deleted} permissions and {roles_deleted} roles'
        )

    def _seed_permissions(self):
        """Seed basic permissions for a typical application."""
        self.stdout.write('📋 Creating basic permissions...')
        
        # Define basic permissions
        permissions_data = [
            # User Management
            {
                'code_name': 'view_users',
                'name': 'View Users',
                'description': 'Can view user profiles and information',
                'category': 'user_management'
            },
            {
                'code_name': 'create_users',
                'name': 'Create Users',
                'description': 'Can create new user accounts',
                'category': 'user_management'
            },
            {
                'code_name': 'edit_users',
                'name': 'Edit Users',
                'description': 'Can modify user profiles and information',
                'category': 'user_management'
            },
            {
                'code_name': 'delete_users',
                'name': 'Delete Users',
                'description': 'Can delete user accounts',
                'category': 'user_management'
            },
            
            # Role & Permission Management
            {
                'code_name': 'manage_roles',
                'name': 'Manage Roles',
                'description': 'Can create, edit, and delete roles',
                'category': 'rbac'
            },
            {
                'code_name': 'manage_permissions',
                'name': 'Manage Permissions',
                'description': 'Can create, edit, and delete permissions',
                'category': 'rbac'
            },
            {
                'code_name': 'assign_roles',
                'name': 'Assign Roles',
                'description': 'Can assign and remove roles from users',
                'category': 'rbac'
            },
            {
                'code_name': 'view_rbac',
                'name': 'View RBAC',
                'description': 'Can view roles, permissions, and assignments',
                'category': 'rbac'
            },
            
            # Content Management (Example for template users)
            {
                'code_name': 'view_content',
                'name': 'View Content',
                'description': 'Can view published content',
                'category': 'content'
            },
            {
                'code_name': 'create_content',
                'name': 'Create Content',
                'description': 'Can create new content',
                'category': 'content'
            },
            {
                'code_name': 'edit_content',
                'name': 'Edit Content',
                'description': 'Can modify existing content',
                'category': 'content'
            },
            {
                'code_name': 'delete_content',
                'name': 'Delete Content',
                'description': 'Can delete content',
                'category': 'content'
            },
            {
                'code_name': 'publish_content',
                'name': 'Publish Content',
                'description': 'Can publish content for public viewing',
                'category': 'content'
            },
            
            # Reporting & Analytics
            {
                'code_name': 'view_reports',
                'name': 'View Reports',
                'description': 'Can view system reports and analytics',
                'category': 'reporting'
            },
            {
                'code_name': 'export_data',
                'name': 'Export Data',
                'description': 'Can export data and reports',
                'category': 'reporting'
            },
            
            # System Administration
            {
                'code_name': 'system_admin',
                'name': 'System Administration',
                'description': 'Full system administration access',
                'category': 'admin'
            },
            {
                'code_name': 'view_logs',
                'name': 'View Logs',
                'description': 'Can view system logs and audit trails',
                'category': 'admin'
            },
            {
                'code_name': 'manage_settings',
                'name': 'Manage Settings',
                'description': 'Can modify system settings and configuration',
                'category': 'admin'
            },
        ]

        created_count = 0
        for perm_data in permissions_data:
            permission, created = Permission.objects.get_or_create(
                code_name=perm_data['code_name'],
                defaults=perm_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'   ✓ Created permission: {permission.name}')
            else:
                self.stdout.write(f'   - Already exists: {permission.name}')

        self.stdout.write(
            self.style.SUCCESS(f'📋 Created {created_count} permissions')
        )

    def _seed_roles(self):
        """Seed basic roles with appropriate permissions."""
        self.stdout.write('👥 Creating basic roles...')

        # Get permissions for role assignments
        permissions = {
            perm.code_name: perm for perm in Permission.objects.all()
        }

        # Define basic roles
        roles_data = [
            {
                'code_name': 'super_admin',
                'name': 'Super Administrator',
                'description': 'Full system access - can do anything',
                'is_system_role': True,
                'permissions': list(permissions.keys())  # All permissions
            },
            {
                'code_name': 'admin',
                'name': 'Administrator',
                'description': 'System administrator with broad access',
                'is_system_role': True,
                'permissions': [
                    'view_users', 'create_users', 'edit_users',
                    'manage_roles', 'assign_roles', 'view_rbac',
                    'view_content', 'create_content', 'edit_content', 'publish_content',
                    'view_reports', 'export_data',
                    'view_logs', 'manage_settings'
                ]
            },
            {
                'code_name': 'manager',
                'name': 'Manager',
                'description': 'Team manager with user and content management access',
                'is_system_role': False,
                'permissions': [
                    'view_users', 'edit_users',
                    'view_rbac', 'assign_roles',
                    'view_content', 'create_content', 'edit_content', 'publish_content',
                    'view_reports', 'export_data'
                ]
            },
            {
                'code_name': 'editor',
                'name': 'Content Editor',
                'description': 'Content creator and editor',
                'is_system_role': False,
                'permissions': [
                    'view_users',
                    'view_content', 'create_content', 'edit_content',
                    'view_reports'
                ]
            },
            {
                'code_name': 'viewer',
                'name': 'Viewer',
                'description': 'Read-only access to content and basic information',
                'is_system_role': False,
                'permissions': [
                    'view_users',
                    'view_content',
                    'view_reports'
                ]
            },
            {
                'code_name': 'guest',
                'name': 'Guest',
                'description': 'Limited guest access',
                'is_system_role': False,
                'permissions': [
                    'view_content'
                ]
            }
        ]

        created_count = 0
        for role_data in roles_data:
            role_permissions = role_data.pop('permissions')
            role, created = Role.objects.get_or_create(
                code_name=role_data['code_name'],
                defaults=role_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'   ✓ Created role: {role.name}')
                
                # Assign permissions to role
                valid_permissions = []
                for perm_code in role_permissions:
                    if perm_code in permissions:
                        valid_permissions.append(permissions[perm_code])
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'   ⚠️ Permission not found: {perm_code}')
                        )
                
                role.permissions.set(valid_permissions)
                self.stdout.write(
                    f'     Assigned {len(valid_permissions)} permissions'
                )
            else:
                self.stdout.write(f'   - Already exists: {role.name}')

        self.stdout.write(
            self.style.SUCCESS(f'👥 Created {created_count} roles')
        )