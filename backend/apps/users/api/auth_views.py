"""
Authentication API Views
Ham Dog & TC's JWT Authentication with RBAC Integration

Following the Ten Commandments:
- JWT tokens for stateless authentication
- RBAC integration in token responses
- Clean error handling
- Template-ready for users
"""
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.permissions.models import Permission, Role
from .serializers import UserCreateSerializer
from .auth_utils import send_verification_email


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer with hybrid id/uuid approach and RBAC data.
    
    Uses integer id as primary key (JWT compatible) with UUID field for external URLs.
    Uses email instead of username for authentication.
    """
    
    username_field = 'email'
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Keep it simple for now - no custom claims
        # token['user_id'] = user.pk
        # token['email'] = user.email
        
        return token
    
    def validate(self, attrs):
        # First, perform standard validation
        data = super().validate(attrs)
        
        # Check if user has verified their email
        user = self.user
        if not user.email_verified:
            # Send a new verification email (give them a lifeline!)
            email_sent = send_verification_email(user)
            
            # Hard block login - no tokens for schemers!
            from rest_framework import serializers
            raise serializers.ValidationError({
                'non_field_errors': [
                    'Email verification required. We\'ve sent you a new verification link. Please check your inbox and verify your email before logging in.'
                ],
                'requires_email_verification': True,
                'email': user.email,
                'email_sent': email_sent,
                'message': 'Verification email sent!' if email_sent else 'Failed to send verification email. Please use the resend option.'
            })
        
        # Add user data and RBAC info to response
        user_data = {
            'id': user.pk,  # Integer primary key
            'public_id': str(user.public_id),  # Public UUID for external URLs
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'date_joined': user.date_joined,
            'last_login': user.last_login,
        }
        
        # Get RBAC data
        rbac_data = {
            'roles': [role.code_name for role in user.get_active_roles()],
            'permissions': [perm.code_name for perm in user.get_all_permissions()],
        }
        
        data.update({
            'user': user_data,
            'rbac': rbac_data,
        })
        
        return data


User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view that includes user data and RBAC info.
    
    This extends the default JWT view to return user information
    and permissions alongside the tokens.
    """
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view that can optionally return updated user data.
    """
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # You can add updated user data here if needed
            # For now, just return the new access token
            pass
        
        return response


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user with email verification requirement.
    
    Expected payload:
    {
        "email": "user@example.com",
        "password": "secure_password",
        "first_name": "John",
        "last_name": "Doe"
    }
    
    Flow:
    1. Create user with email_verified=False
    2. Assign Guest role automatically
    3. Send email verification with signed token
    4. Return user info with JWT tokens (user can login but will get warnings)
    """
    from apps.permissions.models import Role
    
    serializer = UserCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        # Create user with email verification required
        user = serializer.save()
        user.email_verified = False  # Our own email verification field
        user.save()
        
        # Assign Guest role automatically
        try:
            guest_role = Role.objects.get(code_name='guest')
            user.assign_role(guest_role)
        except Role.DoesNotExist:
            # If Guest role doesn't exist, create it or handle gracefully
            pass
        
        # Send verification email using utility function
        email_sent = send_verification_email(user)
        
        # Prepare user data (no tokens until verification!)
        user_data = {
            'id': user.pk,
            'public_id': str(user.public_id),
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'email_verified': user.email_verified,
            'date_joined': user.date_joined,
        }
        
        return Response({
            'user': user_data,
            'message': 'Registration successful! Please check your email to verify your account.',
            'email_sent': email_sent,
            'requires_email_verification': True
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout(request):
    """
    Logout user by blacklisting the refresh token.
    
    Expected payload:
    {
        "refresh": "refresh_token_string"
    }
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Refresh token required'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_profile(request):
    """
    Get current user's profile with RBAC data.
    
    Requires authentication.
    """
    user = request.user
    
    user_data = {
        'id': user.pk,
        'public_id': str(user.public_id),
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_active': user.is_active,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
    }
    
    # Get RBAC data
    rbac_data = {
        'roles': [role.code_name for role in user.get_active_roles()],
        'permissions': [perm.code_name for perm in user.get_all_permissions()],
    }
    
    return Response({
        'user': user_data,
        'rbac': rbac_data,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def auth_check(request):
    """
    Check if the current request is authenticated.
    
    This is useful for frontend to check token validity.
    """
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user_id': request.user.pk,
            'email': request.user.email,
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'authenticated': False,
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def available_permissions(request):
    """
    Get all available permissions in the system.
    
    This is useful for frontend to know what permissions exist.
    """
    permissions = Permission.objects.filter(is_active=True).order_by('category', 'name')
    
    permissions_data = []
    for perm in permissions:
        permissions_data.append({
            'code_name': perm.code_name,
            'name': perm.name,
            'description': perm.description,
            'category': perm.category,
        })
    
    return Response({
        'permissions': permissions_data,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def available_roles(request):
    """
    Get all available roles in the system.
    
    This is useful for frontend to know what roles exist.
    """
    roles = Role.objects.filter(is_active=True).order_by('name')
    
    roles_data = []
    for role in roles:
        roles_data.append({
            'code_name': role.code_name,
            'name': role.name,
            'description': role.description,
            'is_system_role': role.is_system_role,
            'permissions': [perm.code_name for perm in role.permissions.filter(is_active=True)],
        })
    
    return Response({
        'roles': roles_data,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
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
    from django.contrib.sites.shortcuts import get_current_site
    
    email = request.data.get('email')
    if not email:
        return Response(
            {'error': 'Email address is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if user exists
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # For security, don't reveal if email exists or not
        return Response({
            'message': 'If an account with this email exists, you will receive a password reset link.'
        }, status=status.HTTP_200_OK)
    
    # Use Django's built-in password reset form
    form = PasswordResetForm({'email': email})
    if form.is_valid():
        # This will send the email
        form.save(
            request=request,
            use_https=request.is_secure(),
            email_template_name='registration/password_reset_email.txt',
            html_email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt',
        )
    
    return Response({
        'message': 'If an account with this email exists, you will receive a password reset link.'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    """
    Verify user's email address using signed token.
    
    Expected payload:
    {
        "token": "signed_verification_token"
    }
    """
    from django.core.signing import Signer, BadSignature
    
    token = request.data.get('token')
    if not token:
        return Response(
            {'error': 'Verification token is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Verify the signed token
        signer = Signer()
        original_value = signer.unsign(token)
        
        # Parse the token format: "email_verify_{user_pk}_{email}"
        if not original_value.startswith('email_verify_'):
            raise BadSignature("Invalid token format")
            
        parts = original_value.split('_', 2)  # Split into ['email', 'verify', '{pk}_{email}']
        if len(parts) != 3:
            raise BadSignature("Invalid token format")
            
        user_and_email = parts[2].split('_', 1)  # Split '{pk}_{email}' into [pk, email]
        if len(user_and_email) != 2:
            raise BadSignature("Invalid token format")
            
        user_pk = int(user_and_email[0])
        email = user_and_email[1]
        
        # Find and verify the user
        user = User.objects.get(pk=user_pk, email=email)
        
        if user.email_verified:
            return Response({
                'message': 'Email is already verified. You can log in now.',
                'verified': True,
                'email': user.email
            }, status=status.HTTP_200_OK)
        
        # Mark email as verified
        user.email_verified = True
        user.save()
        
        return Response({
            'message': 'Email verified successfully! You can now log in.',
            'verified': True,
            'email': user.email
        }, status=status.HTTP_200_OK)
        
    except BadSignature:
        return Response({
            'error': 'Invalid or expired verification token.',
            'invalid': True
        }, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({
            'error': 'Invalid verification token.',
            'invalid': True
        }, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({
            'error': 'Invalid verification token format.',
            'invalid': True
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'An error occurred during verification. Please try again.',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_email(request):
    """
    Resend email verification for a user.
    
    Expected payload:
    {
        "email": "user@example.com"
    }
    """
    email = request.data.get('email')
    if not email:
        return Response(
            {'error': 'Email address is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)
        
        # Only resend if user email is not yet verified
        if user.email_verified:
            return Response({
                'message': 'This email address is already verified.'
            }, status=status.HTTP_200_OK)
        
        # Send new verification email using utility function
        email_sent = send_verification_email(user)
        
        return Response({
            'message': 'Verification email sent. Please check your inbox.' if email_sent else 'Failed to send verification email. Please try again later.',
            'email': user.email,
            'email_sent': email_sent
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        # For security, don't reveal if email exists or not
        return Response({
            'message': 'If an account with this email exists, you will receive a verification email.'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
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
    
    token = request.data.get('token')
    uid = request.data.get('uid')
    password = request.data.get('password')
    password_confirm = request.data.get('password_confirm')
    
    if not all([token, uid, password, password_confirm]):
        return Response(
            {'error': 'All fields are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if password != password_confirm:
        return Response(
            {'error': 'Passwords do not match'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Decode the user ID
        user_id = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {'error': 'Invalid reset link'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if token is valid
    if not default_token_generator.check_token(user, token):
        return Response(
            {'error': 'Invalid or expired reset token'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Set the new password
    form = SetPasswordForm(user, {'new_password1': password, 'new_password2': password_confirm})
    if form.is_valid():
        form.save()
        return Response({
            'message': 'Password has been reset successfully. You can now log in with your new password.'
        }, status=status.HTTP_200_OK)
    else:
        return Response(
            {'error': form.errors}, 
            status=status.HTTP_400_BAD_REQUEST
        )