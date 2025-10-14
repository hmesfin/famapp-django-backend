"""
Authentication URL Configuration
FamApp JWT Auth Endpoints

Following the Ten Commandments:
- Clean RESTful URL structure
- JWT token endpoints
- Simple authentication flow
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import auth_views
from . import otp_views
from . import password_reset_views

app_name = "auth"

urlpatterns = [
    # JWT Token endpoints
    path(
        "login/",
        auth_views.CustomTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", auth_views.logout, name="logout"),
    # User registration
    path("register/", auth_views.register, name="register"),
    # User profile
    path("profile/", auth_views.user_profile, name="profile"),
    # Auth utilities
    path("check/", auth_views.auth_check, name="auth_check"),
    # Password reset endpoints
    path(
        "forgot-password/", password_reset_views.forgot_password, name="forgot_password"
    ),
    path(
        "reset-password/",
        password_reset_views.reset_password_confirm,
        name="reset_password_confirm",
    ),
    # OTP verification endpoints (replaces magic link verification)
    path("verify-otp/", otp_views.verify_otp, name="verify_otp"),
    path("resend-otp/", otp_views.resend_otp, name="resend_otp"),
]
