"""
Authentication URL Configuration
Ham Dog & TC's JWT Auth Endpoints

Following the Ten Commandments:
- Clean RESTful URL structure
- JWT token endpoints
- RBAC integration endpoints
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import auth_views

app_name = "auth"

urlpatterns = [
    # JWT Token endpoints - using our custom view with email verification handling
    path(
        "login/",
        auth_views.CustomTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "login-custom/",
        auth_views.CustomTokenObtainPairView.as_view(),
        name="token_obtain_pair_custom",
    ),  # Alias for frontend compatibility
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", auth_views.logout, name="logout"),
    # User registration
    path("register/", auth_views.register, name="register"),
    # User profile
    path("profile/", auth_views.user_profile, name="profile"),
    # Auth utilities
    path("check/", auth_views.auth_check, name="auth_check"),
    # RBAC endpoints (public for frontend to know available roles/permissions)
    path(
        "permissions/", auth_views.available_permissions, name="available_permissions"
    ),
    path("roles/", auth_views.available_roles, name="available_roles"),
    # Password reset endpoints
    path("forgot-password/", auth_views.forgot_password, name="forgot_password"),
    path(
        "reset-password/",
        auth_views.reset_password_confirm,
        name="reset_password_confirm",
    ),
    # Email verification endpoints
    path("verify-email/", auth_views.verify_email, name="verify_email"),
    path(
        "resend-verification/",
        auth_views.resend_verification_email,
        name="resend_verification",
    ),
]
