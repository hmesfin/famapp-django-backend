"""
Management command to seed initial roles and permissions
Run with: python manage.py seed_roles
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.permissions.models import Permission, Role
from apps.permissions.constants import (
    RoleCodeName,
    PermissionCodeName,
    ROLE_CHOICES,
    DEFAULT_ROLE_PERMISSIONS,
)


class Command(BaseCommand):
    help = "Seeds initial roles and permissions for the RBAC system"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force recreation of roles and permissions even if they exist",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        force = options.get("force", False)

        self.stdout.write("🌱 Seeding roles and permissions...\n")

        # Create all permissions first
        permissions_data = [
            # Invitation permissions
            (
                PermissionCodeName.SEND_INVITATIONS,
                "Send Invitations",
                "Can send invitations to new users",
                "invitations",
            ),
            (
                PermissionCodeName.VIEW_ALL_INVITATIONS,
                "View All Invitations",
                "Can view all invitations in the system",
                "invitations",
            ),
            (
                PermissionCodeName.MANAGE_INVITATIONS,
                "Manage Invitations",
                "Can manage (resend, cancel) all invitations",
                "invitations",
            ),
            # User management
            (
                PermissionCodeName.MANAGE_USERS,
                "Manage Users",
                "Can create, edit, and delete users",
                "users",
            ),
            (
                PermissionCodeName.VIEW_ALL_USERS,
                "View All Users",
                "Can view all users in the system",
                "users",
            ),
            (
                PermissionCodeName.EDIT_USER_ROLES,
                "Edit User Roles",
                "Can assign and modify user roles",
                "users",
            ),
            # Project permissions
            (
                PermissionCodeName.CREATE_PROJECTS,
                "Create Projects",
                "Can create new projects",
                "projects",
            ),
            (
                PermissionCodeName.EDIT_ALL_PROJECTS,
                "Edit All Projects",
                "Can edit any project",
                "projects",
            ),
            (
                PermissionCodeName.DELETE_PROJECTS,
                "Delete Projects",
                "Can delete projects",
                "projects",
            ),
            (
                PermissionCodeName.VIEW_ALL_PROJECTS,
                "View All Projects",
                "Can view all projects",
                "projects",
            ),
            # General permissions
            (
                PermissionCodeName.ACCESS_ADMIN_PANEL,
                "Access Admin Panel",
                "Can access the Django admin panel",
                "admin",
            ),
            (
                PermissionCodeName.VIEW_ANALYTICS,
                "View Analytics",
                "Can view system analytics and reports",
                "analytics",
            ),
            (
                PermissionCodeName.MANAGE_SETTINGS,
                "Manage Settings",
                "Can manage system settings",
                "settings",
            ),
        ]

        created_permissions = {}
        for code_name, name, description, category in permissions_data:
            if force:
                permission, created = Permission.objects.update_or_create(
                    code_name=code_name,
                    defaults={
                        "name": name,
                        "description": description,
                        "category": category,
                        "is_active": True,
                    },
                )
            else:
                permission, created = Permission.objects.get_or_create(
                    code_name=code_name,
                    defaults={
                        "name": name,
                        "description": description,
                        "category": category,
                        "is_active": True,
                    },
                )

            created_permissions[code_name] = permission

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ Created permission: {name}")
                )
            else:
                self.stdout.write(f"  ⏭️  Permission already exists: {name}")

        # Create roles
        self.stdout.write("\n🎭 Creating roles...\n")

        for role_code, role_name in ROLE_CHOICES:
            if force:
                role, created = Role.objects.update_or_create(
                    code_name=role_code,
                    defaults={
                        "name": role_name,
                        "description": f"{role_name} role with predefined permissions",
                        "is_active": True,
                        "is_system_role": True,
                    },
                )
            else:
                role, created = Role.objects.get_or_create(
                    code_name=role_code,
                    defaults={
                        "name": role_name,
                        "description": f"{role_name} role with predefined permissions",
                        "is_active": True,
                        "is_system_role": True,
                    },
                )

            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✅ Created role: {role_name}"))
            else:
                self.stdout.write(f"  ⏭️  Role already exists: {role_name}")

            # Assign permissions to role
            permission_codes = DEFAULT_ROLE_PERMISSIONS.get(role_code, [])
            permissions_to_add = [
                created_permissions[perm_code]
                for perm_code in permission_codes
                if perm_code in created_permissions
            ]

            if permissions_to_add:
                role.permissions.clear()  # Clear existing permissions if force
                role.permissions.add(*permissions_to_add)
                self.stdout.write(
                    f"    📝 Assigned {len(permissions_to_add)} permissions to {role_name}"
                )

        # Summary
        self.stdout.write(self.style.SUCCESS("\n✨ Seeding completed successfully!"))
        self.stdout.write(f"  - Total permissions: {Permission.objects.count()}")
        self.stdout.write(f"  - Total roles: {Role.objects.count()}")

        # Show role-permission summary
        self.stdout.write("\n📊 Role-Permission Summary:")
        for role in Role.objects.filter(is_system_role=True):
            perm_count = role.permissions.count()
            self.stdout.write(f"  - {role.name}: {perm_count} permissions")
            if perm_count > 0 and options.get("verbosity", 1) >= 2:
                for perm in role.permissions.all():
                    self.stdout.write(f"      • {perm.name}")
