"""
Django Admin for RBAC Models
Ham Dog & TC's Beautiful Admin Interface for Permission Management

Following the Ten Commandments:
- Make it easy to manage roles and permissions
- Provide clear visibility into user assignments
- Keep it intuitive for template users
"""

from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Permission, Role, UserRole, Resource, UserPermission


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ["name", "code_name", "category", "is_active", "created_at"]
    list_filter = ["category", "is_active", "created_at"]
    search_fields = ["name", "code_name", "description"]
    ordering = ["category", "name"]
    readonly_fields = ["uuid", "created_at", "updated_at"]

    fieldsets = (
        (
            None,
            {"fields": ("code_name", "name", "description", "category", "is_active")},
        ),
        (
            _("Metadata"),
            {"fields": ("uuid", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("roles")

    def has_delete_permission(self, request, obj=None):
        # Allow deletion only if permission is not used in any roles
        if obj:
            return not obj.roles.exists()
        return True


class PermissionInline(admin.TabularInline):
    model = Role.permissions.through
    extra = 0
    verbose_name = _("Permission")
    verbose_name_plural = _("Permissions")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "code_name",
        "get_permission_count",
        "get_user_count",
        "is_active",
        "is_system_role",
    ]
    list_filter = ["is_active", "is_system_role", "created_at"]
    search_fields = ["name", "code_name", "description"]
    ordering = ["name"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    filter_horizontal = ["permissions"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "code_name",
                    "name",
                    "description",
                    "is_active",
                    "is_system_role",
                )
            },
        ),
        (_("Permissions"), {"fields": ("permissions",)}),
        (
            _("Metadata"),
            {"fields": ("uuid", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_permission_count(self, obj):
        return obj.permissions.filter(is_active=True).count()

    get_permission_count.short_description = _("Active Permissions")

    def get_user_count(self, obj):
        return obj.user_assignments.filter(is_active=True).count()

    get_user_count.short_description = _("Active Users")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("permissions", "user_assignments")
        )

    def has_delete_permission(self, request, obj=None):
        # System roles cannot be deleted
        if obj and obj.is_system_role:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "role",
        "is_active",
        "assigned_by",
        "expires_at",
        "created_at",
    ]
    list_filter = ["is_active", "role", "expires_at", "created_at"]
    search_fields = ["user__email", "user__first_name", "user__last_name", "role__name"]
    ordering = ["-created_at"]
    readonly_fields = [
        "uuid",
        "created_at",
        "updated_at",
        "is_expired_display",
        "is_valid_display",
    ]
    autocomplete_fields = ["user", "role", "assigned_by"]

    fieldsets = (
        (None, {"fields": ("user", "role", "is_active")}),
        (_("Assignment Details"), {"fields": ("assigned_by", "expires_at", "context")}),
        (
            _("Status"),
            {
                "fields": ("is_expired_display", "is_valid_display"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Metadata"),
            {"fields": ("uuid", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def is_expired_display(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: red;">Yes</span>')
        return format_html('<span style="color: green;">No</span>')

    is_expired_display.short_description = _("Is Expired")

    def is_valid_display(self, obj):
        if obj.is_valid():
            return format_html('<span style="color: green;">Valid</span>')
        return format_html('<span style="color: red;">Invalid</span>')

    is_valid_display.short_description = _("Is Valid")

    def get_queryset(self, request):
        return (
            super().get_queryset(request).select_related("user", "role", "assigned_by")
        )


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ["name", "resource_type", "resource_id", "created_at"]
    list_filter = ["resource_type", "created_at"]
    search_fields = ["name", "resource_type", "resource_id", "description"]
    ordering = ["resource_type", "name"]
    readonly_fields = ["uuid", "created_at", "updated_at"]

    fieldsets = (
        (None, {"fields": ("resource_type", "resource_id", "name", "description")}),
        (_("Additional Data"), {"fields": ("metadata",), "classes": ("collapse",)}),
        (
            _("Metadata"),
            {"fields": ("uuid", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("userpermission_set")


@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "permission",
        "resource",
        "is_active",
        "granted_by",
        "expires_at",
        "created_at",
    ]
    list_filter = [
        "is_active",
        "permission__category",
        "resource__resource_type",
        "expires_at",
        "created_at",
    ]
    search_fields = [
        "user__email",
        "user__first_name",
        "user__last_name",
        "permission__name",
        "permission__code_name",
        "resource__name",
    ]
    ordering = ["-created_at"]
    readonly_fields = [
        "uuid",
        "created_at",
        "updated_at",
        "is_expired_display",
        "is_valid_display",
    ]
    autocomplete_fields = ["user", "permission", "resource", "granted_by"]

    fieldsets = (
        (None, {"fields": ("user", "permission", "resource", "is_active")}),
        (_("Grant Details"), {"fields": ("granted_by", "expires_at", "context")}),
        (
            _("Status"),
            {
                "fields": ("is_expired_display", "is_valid_display"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Metadata"),
            {"fields": ("uuid", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def is_expired_display(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: red;">Yes</span>')
        return format_html('<span style="color: green;">No</span>')

    is_expired_display.short_description = _("Is Expired")

    def is_valid_display(self, obj):
        if obj.is_valid():
            return format_html('<span style="color: green;">Valid</span>')
        return format_html('<span style="color: red;">Invalid</span>')

    is_valid_display.short_description = _("Is Valid")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user", "permission", "resource", "granted_by")
        )


# Customize admin site header
admin.site.site_header = _("DjVue Orchestra RBAC Administration")
admin.site.site_title = _("RBAC Admin")
admin.site.index_title = _("Role-Based Access Control Management")
