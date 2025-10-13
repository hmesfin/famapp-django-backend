"""
Serializer tests for profiles app
Ham Dog & TC's TDD for API serialization!

Following Commandments #3 & #4: Contextual serializers without __all__!
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request

from apps.profiles.models import Profile, UserSettings
from apps.profiles.api.serializers import (
    ProfileListSerializer,
    ProfileDetailSerializer,
    ProfileUpdateSerializer,
    UserSettingsSerializer,
    UserSettingsUpdateSerializer
)

User = get_user_model()


@pytest.fixture
def api_request():
    """Create a mock API request for serializer context"""
    factory = APIRequestFactory()
    request = factory.get('/')
    return Request(request)


@pytest.mark.django_db
class TestProfileSerializers:
    """Test suite for Profile serializers"""

    def test_profile_list_serializer_fields(self, api_request):
        """Test ProfileListSerializer returns only necessary fields for list view"""
        user = User.objects.create_user(email="list@test.com")
        profile = Profile.objects.create(
            user=user,
            bio="Test bio",
            location="Test location",
            company="Test company"
        )
        
        serializer = ProfileListSerializer(profile, context={'request': api_request})
        data = serializer.data
        
        # Should have limited fields for list view
        assert 'public_id' in data
        assert 'user_email' in data
        assert 'bio' in data
        assert 'avatar_url' in data
        assert 'location' in data
        
        # Should NOT have timestamps in list view
        assert 'created_at' not in data
        assert 'updated_at' not in data

    def test_profile_detail_serializer_fields(self, api_request):
        """Test ProfileDetailSerializer returns all relevant fields"""
        user = User.objects.create_user(
            email="detail@test.com",
            first_name="Ham",
            last_name="Dog"
        )
        profile = Profile.objects.create(
            user=user,
            bio="Detailed bio",
            location="Code Heaven",
            website="https://hamdog.dev",
            company="Ham Dog & TC Inc.",
            avatar_url="https://example.com/avatar.jpg"
        )
        
        serializer = ProfileDetailSerializer(profile, context={'request': api_request})
        data = serializer.data
        
        # Should have all public fields
        assert data['public_id'] == str(profile.public_id)
        assert data['user_email'] == "detail@test.com"
        assert data['user_full_name'] == "Ham Dog"
        assert data['bio'] == "Detailed bio"
        assert data['location'] == "Code Heaven"
        assert data['website'] == "https://hamdog.dev"
        assert data['company'] == "Ham Dog & TC Inc."
        assert data['avatar_url'] == "https://example.com/avatar.jpg"
        assert 'created_at' in data
        assert 'updated_at' in data

    def test_profile_update_serializer_validation(self):
        """Test ProfileUpdateSerializer validates input correctly"""
        # Valid data
        valid_data = {
            'bio': 'Updated bio',
            'location': 'New location',
            'website': 'https://valid-url.com',
            'company': 'New company',
            'avatar_url': 'https://avatar.com/new.jpg'
        }
        serializer = ProfileUpdateSerializer(data=valid_data)
        assert serializer.is_valid()
        
        # Invalid website URL
        invalid_data = {
            'website': 'not-a-url'
        }
        serializer = ProfileUpdateSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert 'website' in serializer.errors

    def test_profile_update_serializer_partial_update(self):
        """Test ProfileUpdateSerializer allows partial updates"""
        user = User.objects.create_user(email="update@test.com")
        profile = Profile.objects.create(
            user=user,
            bio="Original bio",
            location="Original location"
        )
        
        # Update only bio
        data = {'bio': 'Updated bio only'}
        serializer = ProfileUpdateSerializer(
            profile, 
            data=data, 
            partial=True
        )
        assert serializer.is_valid()
        serializer.save()
        
        profile.refresh_from_db()
        assert profile.bio == 'Updated bio only'
        assert profile.location == 'Original location'  # Unchanged


@pytest.mark.django_db
class TestUserSettingsSerializers:
    """Test suite for UserSettings serializers"""

    def test_user_settings_serializer_fields(self, api_request):
        """Test UserSettingsSerializer returns all settings fields"""
        user = User.objects.create_user(email="settings@test.com")
        settings = UserSettings.objects.create(
            user=user,
            theme="dark",
            language="es",
            timezone="America/New_York",
            email_notifications=False,
            push_notifications=True,
            profile_visibility="private",
            show_email=True,
            show_activity=False
        )
        
        serializer = UserSettingsSerializer(settings, context={'request': api_request})
        data = serializer.data
        
        # Check all fields are present
        assert data['public_id'] == str(settings.public_id)
        assert data['theme'] == "dark"
        assert data['language'] == "es"
        assert data['timezone'] == "America/New_York"
        assert data['email_notifications'] is False
        assert data['push_notifications'] is True
        assert data['profile_visibility'] == "private"
        assert data['show_email'] is True
        assert data['show_activity'] is False
        assert 'metadata' in data

    def test_user_settings_update_serializer_validation(self):
        """Test UserSettingsUpdateSerializer validates choices correctly"""
        # Valid theme
        valid_data = {'theme': 'dark'}
        serializer = UserSettingsUpdateSerializer(data=valid_data)
        assert serializer.is_valid()
        
        # Invalid theme
        invalid_data = {'theme': 'rainbow'}
        serializer = UserSettingsUpdateSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert 'theme' in serializer.errors
        
        # Valid visibility
        valid_data = {'profile_visibility': 'private'}
        serializer = UserSettingsUpdateSerializer(data=valid_data)
        assert serializer.is_valid()
        
        # Invalid visibility
        invalid_data = {'profile_visibility': 'secret'}
        serializer = UserSettingsUpdateSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert 'profile_visibility' in serializer.errors

    def test_user_settings_update_metadata(self):
        """Test updating metadata field with JSON data"""
        user = User.objects.create_user(email="metadata@test.com")
        settings = UserSettings.objects.create(user=user)
        
        metadata = {
            "dashboard_layout": "grid",
            "notifications": {
                "sound": True,
                "desktop": False
            }
        }
        
        serializer = UserSettingsUpdateSerializer(
            settings,
            data={'metadata': metadata},
            partial=True
        )
        assert serializer.is_valid()
        serializer.save()
        
        settings.refresh_from_db()
        assert settings.metadata['dashboard_layout'] == "grid"
        assert settings.metadata['notifications']['sound'] is True

    def test_user_settings_serializer_read_only_fields(self):
        """Test that certain fields are read-only"""
        user = User.objects.create_user(email="readonly@test.com")
        settings = UserSettings.objects.create(user=user)
        
        # Try to update read-only fields
        data = {
            'public_id': 'new-uuid',  # Should be read-only
            'created_at': '2024-01-01T00:00:00Z',  # Should be read-only
            'theme': 'dark'  # Should be writable
        }
        
        serializer = UserSettingsUpdateSerializer(
            settings,
            data=data,
            partial=True
        )
        assert serializer.is_valid()
        serializer.save()
        
        settings.refresh_from_db()
        # Read-only fields should not change
        assert str(settings.public_id) != 'new-uuid'
        # Writable field should change
        assert settings.theme == 'dark'