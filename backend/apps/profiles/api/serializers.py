"""
API Serializers for profiles app
Ham Dog & TC's contextual serializers!

Following Commandments #3 & #4: 
- No __all__ gluttony
- Contextual serializers for different use cases
"""
from rest_framework import serializers
from apps.profiles.models import Profile, UserSettings


class ProfileListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for profile lists.
    Returns only essential fields for list views.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'public_id',
            'user_email',
            'bio',
            'avatar_url',
            'location',
        ]
        read_only_fields = ['public_id']


class ProfileDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for single profile views.
    Returns all public profile information.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = [
            'public_id',
            'user_email',
            'user_full_name',
            'bio',
            'location',
            'website',
            'company',
            'avatar_url',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['public_id', 'created_at', 'updated_at']
    
    def get_user_full_name(self, obj):
        """Get user's full name or email if name not set"""
        user = obj.user
        full_name = f"{user.first_name} {user.last_name}".strip()
        return full_name if full_name else user.email


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating profile information.
    Only allows updating profile-specific fields.
    """
    class Meta:
        model = Profile
        fields = [
            'bio',
            'location',
            'website',
            'company',
            'avatar_url',
        ]
    
    def validate_website(self, value):
        """Ensure website is a valid URL"""
        if value and not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("Website must be a valid URL")
        return value
    
    def validate_avatar_url(self, value):
        """Ensure avatar URL is valid"""
        if value and not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("Avatar URL must be a valid URL")
        return value


class UserSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for user settings.
    Returns all user preference settings.
    """
    class Meta:
        model = UserSettings
        fields = [
            'public_id',
            'theme',
            'language',
            'timezone',
            'email_notifications',
            'push_notifications',
            'profile_visibility',
            'show_email',
            'show_activity',
            'metadata',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['public_id', 'created_at', 'updated_at']


class UserSettingsUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user settings.
    Validates choices and allows partial updates.
    """
    class Meta:
        model = UserSettings
        fields = [
            'theme',
            'language',
            'timezone',
            'email_notifications',
            'push_notifications',
            'profile_visibility',
            'show_email',
            'show_activity',
            'metadata',
        ]
    
    def validate_theme(self, value):
        """Validate theme choice"""
        valid_themes = dict(UserSettings.THEME_CHOICES).keys()
        if value not in valid_themes:
            raise serializers.ValidationError(
                f"Invalid theme. Must be one of: {', '.join(valid_themes)}"
            )
        return value
    
    def validate_profile_visibility(self, value):
        """Validate visibility choice"""
        valid_choices = dict(UserSettings.VISIBILITY_CHOICES).keys()
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Invalid visibility. Must be one of: {', '.join(valid_choices)}"
            )
        return value