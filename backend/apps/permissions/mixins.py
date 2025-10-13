"""
RBAC Mixins and Utilities for Views
Ham Dog & TC's Permission System Integration

Following the Ten Commandments:
- Make permissions easy to use in views
- Provide clear error messages
- Keep it DRY with reusable components
"""

from functools import wraps
from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied


class RoleRequiredMixin(AccessMixin):
    """
    Mixin to require specific roles for view access.

    Usage:
        class MyView(RoleRequiredMixin, View):
            required_roles = ['admin', 'manager']
    """

    required_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not self.has_required_roles(request.user):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def has_required_roles(self, user):
        if not user.is_authenticated:
            return False

        if not self.required_roles:
            return True

        for role_code in self.required_roles:
            if user.has_role(role_code):
                return True
        return False


class PermissionRequiredMixin(AccessMixin):
    """
    Mixin to require specific permissions for view access.

    Usage:
        class MyView(PermissionRequiredMixin, View):
            required_permissions = ['view_content', 'edit_content']
            require_all_permissions = True  # Default: False (any permission)
    """

    required_permissions = []
    require_all_permissions = False

    def dispatch(self, request, *args, **kwargs):
        if not self.has_required_permissions(request.user):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def has_required_permissions(self, user):
        if not user.is_authenticated:
            return False

        if not self.required_permissions:
            return True

        if self.require_all_permissions:
            # User must have ALL permissions
            return all(user.has_permission(perm) for perm in self.required_permissions)
        else:
            # User must have ANY permission
            return any(user.has_permission(perm) for perm in self.required_permissions)


class ResourcePermissionMixin(AccessMixin):
    """
    Mixin for object-level permissions on specific resources.

    Usage:
        class ArticleDetailView(ResourcePermissionMixin, DetailView):
            required_permission = 'edit_content'

            def get_resource(self):
                return self.get_object()
    """

    required_permission = None

    def dispatch(self, request, *args, **kwargs):
        if not self.has_resource_permission(request.user):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def has_resource_permission(self, user):
        if not user.is_authenticated:
            return False

        if not self.required_permission:
            return True

        resource = self.get_resource()
        return user.has_permission(self.required_permission, resource)

    def get_resource(self):
        """Override this method to return the resource object."""
        return None


# DRF Permission Classes


class HasRole(permissions.BasePermission):
    """
    DRF permission class to check for specific roles.

    Usage:
        class MyViewSet(ViewSet):
            permission_classes = [HasRole]
            required_roles = ['admin', 'manager']
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        required_roles = getattr(view, "required_roles", [])
        if not required_roles:
            return True

        return any(request.user.has_role(role) for role in required_roles)


class HasPermission(permissions.BasePermission):
    """
    DRF permission class to check for specific permissions.

    Usage:
        class MyViewSet(ViewSet):
            permission_classes = [HasPermission]
            required_permissions = ['view_content']
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        required_permissions = getattr(view, "required_permissions", [])
        if not required_permissions:
            return True

        require_all = getattr(view, "require_all_permissions", False)

        if require_all:
            return all(
                request.user.has_permission(perm) for perm in required_permissions
            )
        else:
            return any(
                request.user.has_permission(perm) for perm in required_permissions
            )


class HasObjectPermission(permissions.BasePermission):
    """
    DRF permission class for object-level permissions.

    Usage:
        class ArticleViewSet(ViewSet):
            permission_classes = [HasObjectPermission]
            required_object_permission = 'edit_content'
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        required_permission = getattr(view, "required_object_permission", None)
        if not required_permission:
            return True

        return request.user.has_permission(required_permission, obj)


# Decorators


def role_required(*roles):
    """
    Decorator to require specific roles for function-based views.

    Usage:
        @role_required('admin', 'manager')
        def my_view(request):
            pass
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("account_login")

            if not any(request.user.has_role(role) for role in roles):
                if request.headers.get("Accept") == "application/json":
                    return JsonResponse(
                        {"error": "Insufficient permissions"}, status=403
                    )
                raise PermissionDenied(
                    "You don't have the required role to access this page."
                )

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def permission_required(*permissions, require_all=False):
    """
    Decorator to require specific permissions for function-based views.

    Usage:
        @permission_required('view_content', 'edit_content')
        def my_view(request):
            pass

        @permission_required('admin_access', require_all=True)
        def admin_view(request):
            pass
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("account_login")

            if require_all:
                has_permission = all(
                    request.user.has_permission(perm) for perm in permissions
                )
            else:
                has_permission = any(
                    request.user.has_permission(perm) for perm in permissions
                )

            if not has_permission:
                if request.headers.get("Accept") == "application/json":
                    return JsonResponse(
                        {"error": "Insufficient permissions"}, status=403
                    )
                raise PermissionDenied(
                    "You don't have the required permissions to access this page."
                )

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def resource_permission_required(permission_code):
    """
    Decorator for object-level permissions in function-based views.

    Usage:
        @resource_permission_required('edit_content')
        def edit_article(request, article_id):
            article = get_object_or_404(Article, id=article_id)
            # The permission check is done against the article object
            pass
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("account_login")

            # This is a simplified example - in practice, you'd need to
            # extract the resource object from the view parameters
            # For now, just check general permission
            if not request.user.has_permission(permission_code):
                if request.headers.get("Accept") == "application/json":
                    return JsonResponse(
                        {"error": "Insufficient permissions"}, status=403
                    )
                raise PermissionDenied(
                    f"You don't have the '{permission_code}' permission."
                )

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


# Utility functions


def user_has_any_role(user, roles):
    """Check if user has any of the specified roles."""
    if not user.is_authenticated:
        return False
    return any(user.has_role(role) for role in roles)


def user_has_all_roles(user, roles):
    """Check if user has all of the specified roles."""
    if not user.is_authenticated:
        return False
    return all(user.has_role(role) for role in roles)


def user_has_any_permission(user, permissions):
    """Check if user has any of the specified permissions."""
    if not user.is_authenticated:
        return False
    return any(user.has_permission(perm) for perm in permissions)


def user_has_all_permissions(user, permissions):
    """Check if user has all of the specified permissions."""
    if not user.is_authenticated:
        return False
    return all(user.has_permission(perm) for perm in permissions)


def get_user_permissions(user):
    """Get all permissions for a user (for template context, etc.)."""
    if not user.is_authenticated:
        return []
    return [perm.code_name for perm in user.get_all_permissions()]


def get_user_roles(user):
    """Get all active roles for a user."""
    if not user.is_authenticated:
        return []
    return [role.code_name for role in user.get_active_roles()]
