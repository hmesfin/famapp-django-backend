"""
Password Reset API Views
FamApp Password Reset Flow

Handles:
- Password reset request (forgot password)
- Password reset confirmation with token
"""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password(request):
    """
    Initiate password reset by sending email with reset link.

    Expected payload:
    {
        "email": "user@example.com"
    }
    """
    from django.contrib.auth.forms import PasswordResetForm

    email = request.data.get("email")
    if not email:
        return Response(
            {"error": "Email address is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if user exists
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # For security, don't reveal if email exists or not
        return Response(
            {
                "message": "If an account with this email exists, you will receive a password reset link.",
            },
            status=status.HTTP_200_OK,
        )

    # Use Django's built-in password reset form
    form = PasswordResetForm({"email": email})
    if form.is_valid():
        # This will send the email
        form.save(
            request=request,
            use_https=request.is_secure(),
            email_template_name="registration/password_reset_email.txt",
            html_email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
        )

    return Response(
        {
            "message": "If an account with this email exists, you will receive a password reset link.",
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_confirm(request):
    """
    Confirm password reset with token and set new password.

    Expected payload:
    {
        "token": "password_reset_token",
        "uid": "encoded_user_id",
        "password": "new_password",
        "password_confirm": "new_password"
    }
    """
    from django.contrib.auth.forms import SetPasswordForm
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_decode

    token = request.data.get("token")
    uid = request.data.get("uid")
    password = request.data.get("password")
    password_confirm = request.data.get("password_confirm")

    if not all([token, uid, password, password_confirm]):
        return Response(
            {"error": "All fields are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if password != password_confirm:
        return Response(
            {"error": "Passwords do not match"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Decode the user ID
        user_id = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {"error": "Invalid reset link"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if token is valid
    if not default_token_generator.check_token(user, token):
        return Response(
            {"error": "Invalid or expired reset token"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Set the new password
    form = SetPasswordForm(
        user,
        {"new_password1": password, "new_password2": password_confirm},
    )
    if form.is_valid():
        form.save()
        return Response(
            {
                "message": "Password has been reset successfully. You can now log in with your new password.",
            },
            status=status.HTTP_200_OK,
        )
    return Response({"error": form.errors}, status=status.HTTP_400_BAD_REQUEST)
