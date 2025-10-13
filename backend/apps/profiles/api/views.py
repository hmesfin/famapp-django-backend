"""
API ViewSets for profiles app
Ham Dog & TC's RESTful endpoints!

Following DRY principles and proper permission handling
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings

from apps.profiles.models import Profile, UserSettings
from apps.profiles.api.serializers import (
    ProfileListSerializer,
    ProfileDetailSerializer,
    ProfileUpdateSerializer,
    UserSettingsSerializer,
    UserSettingsUpdateSerializer
)
from apps.profiles.permissions import IsOwnerOrReadOnly
from apps.profiles.services.avatar_service import avatar_service
from apps.profiles.services.cache_service import profile_cache_service
import hashlib


class ProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Profile model.
    
    List and retrieve are public.
    Update is restricted to profile owner.
    Create and delete are not allowed (profiles are auto-created with users).
    """
    queryset = Profile.objects.filter(is_deleted=False).select_related('user').prefetch_related('user__settings')
    lookup_field = 'public_id'
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'bio', 'location', 'company']
    filterset_fields = ['company', 'location']
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return ProfileListSerializer
        elif self.action in ['update', 'partial_update']:
            return ProfileUpdateSerializer
        else:
            return ProfileDetailSerializer
    
    def get_permissions(self):
        """Allow public access to list and retrieve"""
        if self.action in ['list', 'retrieve', 'me']:
            return [AllowAny()]
        return super().get_permissions()
    
    def _get_filters_hash(self, request) -> str:
        """Generate hash from query parameters for cache key"""
        # Sort query params for consistent hashing
        params = sorted(request.GET.items())
        params_str = '&'.join([f"{k}={v}" for k, v in params])
        return hashlib.md5(params_str.encode()).hexdigest()
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve single profile with caching"""
        public_id = kwargs.get(self.lookup_field)
        
        # Try cache first
        cached_profile = profile_cache_service.get_profile(public_id)
        if cached_profile:
            return Response(cached_profile)
        
        # Cache miss - get from database
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            # Cache the result
            profile_cache_service.set_profile(instance)
            
            return Response(serializer.data)
        except Exception:
            # Fall back to default behavior
            return super().retrieve(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """
        Get current user's profile with caching.
        Creates profile if it doesn't exist.
        """
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # For authenticated users, try to find their cached profile first
        # We need to get the profile to know the public_id for cache lookup
        try:
            profile = Profile.objects.select_related('user').prefetch_related('user__settings').get(
                user=request.user
            )
            
            # Check cache
            cached_profile = profile_cache_service.get_profile(profile.public_id)
            if cached_profile:
                return Response(cached_profile)
            
        except Profile.DoesNotExist:
            # Profile doesn't exist, create it
            profile = None
        
        # Cache miss or new profile - get/create from database
        profile, created = Profile.objects.select_related('user').prefetch_related('user__settings').get_or_create(
            user=request.user,
            defaults={'bio': '', 'location': ''}
        )
        
        # Cache the result
        profile_cache_service.set_profile(profile)
        
        serializer = ProfileDetailSerializer(profile, context={'request': request})
        return Response(serializer.data)
    
    @action(
        detail=False,
        methods=['post'],
        url_path='upload-avatar',
        parser_classes=[MultiPartParser, FormParser],
        permission_classes=[IsAuthenticated]
    )
    def upload_avatar(self, request):
        """
        Upload avatar image for current user's profile.
        Accepts multipart/form-data with 'avatar' field.
        
        Refactored to use AvatarService for separation of concerns.
        """
        if 'avatar' not in request.FILES:
            return Response(
                {'detail': 'No avatar file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        avatar_file = request.FILES['avatar']
        
        try:
            # Get or create profile (optimized query)
            profile, created = Profile.objects.select_related('user').prefetch_related('user__settings').get_or_create(
                user=request.user,
                defaults={'bio': '', 'location': ''}
            )
            
            # Use avatar service to handle the upload
            avatar_url = avatar_service.process_avatar_upload(
                file=avatar_file,
                user_id=request.user.id,
                old_avatar_url=profile.avatar_url,
                request=request
            )
            
            # Update profile with new avatar URL
            profile.avatar_url = avatar_url
            profile.save(update_fields=['avatar_url', 'updated_at'])
            
            # Invalidate cache after update
            profile_cache_service.invalidate_user_cache(
                user_id=request.user.id,
                public_id=profile.public_id
            )
            
            return Response({
                'avatar_url': avatar_url,
                'message': 'Avatar uploaded successfully'
            })
            
        except ValidationError as e:
            # Avatar service raises ValidationError with proper format
            return Response(
                e.detail,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'detail': f'Failed to upload avatar: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request, *args, **kwargs):
        """Disable profile creation via API"""
        return Response(
            {'detail': 'Profiles are automatically created with user registration'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def update(self, request, *args, **kwargs):
        """Update profile with cache invalidation"""
        response = super().update(request, *args, **kwargs)
        
        # Invalidate cache after successful update
        if response.status_code in [200, 201]:
            instance = self.get_object()
            profile_cache_service.invalidate_user_cache(
                user_id=instance.user.id,
                public_id=instance.public_id
            )
        
        return response
    
    def partial_update(self, request, *args, **kwargs):
        """Partial update profile with cache invalidation"""
        response = super().partial_update(request, *args, **kwargs)
        
        # Invalidate cache after successful update
        if response.status_code in [200, 201]:
            instance = self.get_object()
            profile_cache_service.invalidate_user_cache(
                user_id=instance.user.id,
                public_id=instance.public_id
            )
        
        return response

    def destroy(self, request, *args, **kwargs):
        """Disable profile deletion via API"""
        return Response(
            {'detail': 'Profile deletion is not allowed'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class UserSettingsViewSet(viewsets.GenericViewSet):
    """
    ViewSet for UserSettings model.
    
    Users can only access and update their own settings.
    Settings are auto-created if they don't exist.
    """
    serializer_class = UserSettingsSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch', 'put', 'head', 'options']
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.request.method in ['PATCH', 'PUT']:
            return UserSettingsUpdateSerializer
        return UserSettingsSerializer
    
    def get_object(self):
        """
        Get or create settings for the current user.
        Users can only access their own settings.
        """
        settings, created = UserSettings.objects.get_or_create(
            user=self.request.user,
            defaults={
                'theme': 'light',
                'language': 'en',
                'timezone': 'UTC',
                'email_notifications': True,
                'push_notifications': False,
                'profile_visibility': 'public',
                'show_email': False,
                'show_activity': True,
                'metadata': {}
            }
        )
        return settings
    
    @action(detail=False, methods=['get', 'patch', 'put'], url_path='')
    def current_settings(self, request):
        """
        Main endpoint for user settings with caching.
        GET: Retrieve current user's settings
        PATCH/PUT: Update current user's settings
        """
        if request.method == 'GET':
            # Try cache first for read operations
            cached_settings = profile_cache_service.get_user_settings(request.user.id)
            if cached_settings:
                return Response(cached_settings)
        
        # Cache miss or write operation - use database
        settings = self.get_object()
        
        if request.method == 'GET':
            # Cache the result for future requests
            profile_cache_service.set_user_settings(settings)
            serializer = self.get_serializer(settings)
            return Response(serializer.data)
        
        else:  # PATCH or PUT
            partial = request.method == 'PATCH'
            serializer = self.get_serializer(
                settings,
                data=request.data,
                partial=partial
            )
            
            if serializer.is_valid():
                serializer.save()
                
                # Invalidate cache after update
                profile_cache_service.invalidate_user_settings(request.user.id)
                
                # Return the full settings object after update
                full_serializer = UserSettingsSerializer(settings)
                return Response(full_serializer.data)
            
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )