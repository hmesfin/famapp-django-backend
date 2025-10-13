"""
Constants for the permissions app
Defines standard roles and permissions for the system
"""


# System Role Code Names
class RoleCodeName:
    """Standard role code names used throughout the system"""

    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"
    GUEST = "guest"


# System Permission Code Names
class PermissionCodeName:
    """Standard permission code names"""

    # Invitation permissions
    SEND_INVITATIONS = "send_invitations"
    VIEW_ALL_INVITATIONS = "view_all_invitations"
    MANAGE_INVITATIONS = "manage_invitations"

    # User management
    MANAGE_USERS = "manage_users"
    VIEW_ALL_USERS = "view_all_users"
    EDIT_USER_ROLES = "edit_user_roles"

    # Project permissions
    CREATE_PROJECTS = "create_projects"
    EDIT_ALL_PROJECTS = "edit_all_projects"
    DELETE_PROJECTS = "delete_projects"
    VIEW_ALL_PROJECTS = "view_all_projects"

    # General permissions
    ACCESS_ADMIN_PANEL = "access_admin_panel"
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_SETTINGS = "manage_settings"


# Role choices for forms and models
ROLE_CHOICES = [
    (RoleCodeName.ADMIN, "Administrator"),
    (RoleCodeName.MANAGER, "Manager"),
    (RoleCodeName.MEMBER, "Member"),
    (RoleCodeName.VIEWER, "Viewer"),
    (RoleCodeName.GUEST, "Guest"),
]


# Role hierarchy (higher number = more privileges)
ROLE_HIERARCHY = {
    RoleCodeName.ADMIN: 100,
    RoleCodeName.MANAGER: 75,
    RoleCodeName.MEMBER: 50,
    RoleCodeName.VIEWER: 25,
    RoleCodeName.GUEST: 10,
}


# Default permissions for each role
DEFAULT_ROLE_PERMISSIONS = {
    RoleCodeName.ADMIN: [
        PermissionCodeName.SEND_INVITATIONS,
        PermissionCodeName.VIEW_ALL_INVITATIONS,
        PermissionCodeName.MANAGE_INVITATIONS,
        PermissionCodeName.MANAGE_USERS,
        PermissionCodeName.VIEW_ALL_USERS,
        PermissionCodeName.EDIT_USER_ROLES,
        PermissionCodeName.CREATE_PROJECTS,
        PermissionCodeName.EDIT_ALL_PROJECTS,
        PermissionCodeName.DELETE_PROJECTS,
        PermissionCodeName.VIEW_ALL_PROJECTS,
        PermissionCodeName.ACCESS_ADMIN_PANEL,
        PermissionCodeName.VIEW_ANALYTICS,
        PermissionCodeName.MANAGE_SETTINGS,
    ],
    RoleCodeName.MANAGER: [
        PermissionCodeName.SEND_INVITATIONS,  # Managers can also send invitations
        PermissionCodeName.VIEW_ALL_INVITATIONS,
        PermissionCodeName.VIEW_ALL_USERS,
        PermissionCodeName.CREATE_PROJECTS,
        PermissionCodeName.EDIT_ALL_PROJECTS,
        PermissionCodeName.VIEW_ALL_PROJECTS,
        PermissionCodeName.VIEW_ANALYTICS,
    ],
    RoleCodeName.MEMBER: [
        PermissionCodeName.CREATE_PROJECTS,
        PermissionCodeName.VIEW_ALL_PROJECTS,
    ],
    RoleCodeName.VIEWER: [
        PermissionCodeName.VIEW_ALL_PROJECTS,
    ],
    RoleCodeName.GUEST: [
        # Guests have no default permissions
    ],
}
