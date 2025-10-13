"""
ViewSet tests for profiles app
Ham Dog & TC's TDD for API endpoints!

Testing all CRUD operations and permissions
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.profiles.models import Profile, UserSettings

User = get_user_model()


@pytest.fixture
def api_client():
    """Create an API client for testing"""
    return APIClient()


@pytest.fixture
def authenticated_user():
    """Create an authenticated user with profile and settings"""
    user = User.objects.create_user(
        email="auth_user@test.com",
        first_name="Auth",
        last_name="User"
    )
    Profile.objects.create(
        user=user,
        bio="Authenticated user bio",
        location="Test City"
    )
    UserSettings.objects.create(
        user=user,
        theme="dark"
    )
    return user


@pytest.fixture
def other_user():
    """Create another user for permission testing"""
    user = User.objects.create_user(
        email="other_user@test.com",
        first_name="Other",
        last_name="User"
    )
    Profile.objects.create(
        user=user,
        bio="Other user bio"
    )
    UserSettings.objects.create(user=user)
    return user


@pytest.mark.django_db
class TestProfileViewSet:
    """Test suite for Profile API endpoints"""

    def test_list_profiles_public(self, api_client):
        """Test that profile list is publicly accessible"""
        # Create some profiles
        for i in range(3):
            user = User.objects.create_user(email=f"user{i}@test.com")
            Profile.objects.create(user=user, bio=f"Bio {i}")
        
        response = api_client.get('/api/v1/profiles/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_retrieve_profile_by_public_id(self, api_client, authenticated_user):
        """Test retrieving a single profile by public_id"""
        profile = authenticated_user.profile
        
        response = api_client.get(f'/api/v1/profiles/{profile.public_id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['public_id'] == str(profile.public_id)
        assert response.data['bio'] == "Authenticated user bio"
        assert 'user_full_name' in response.data

    def test_retrieve_own_profile(self, api_client, authenticated_user):
        """Test retrieving own profile via /me endpoint"""
        api_client.force_authenticate(user=authenticated_user)
        
        response = api_client.get('/api/v1/profiles/me/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user_email'] == "auth_user@test.com"
        assert response.data['bio'] == "Authenticated user bio"

    def test_update_own_profile(self, api_client, authenticated_user):
        """Test that users can update their own profile"""
        api_client.force_authenticate(user=authenticated_user)
        profile = authenticated_user.profile
        
        update_data = {
            'bio': 'Updated bio!',
            'location': 'New City',
            'website': 'https://newsite.com'
        }
        
        response = api_client.patch(
            f'/api/v1/profiles/{profile.public_id}/',
            update_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        profile.refresh_from_db()
        assert profile.bio == 'Updated bio!'
        assert profile.location == 'New City'
        assert profile.website == 'https://newsite.com'

    def test_cannot_update_other_profile(self, api_client, authenticated_user, other_user):
        """Test that users cannot update other users' profiles"""
        api_client.force_authenticate(user=authenticated_user)
        other_profile = other_user.profile
        
        update_data = {'bio': 'Hacked bio!'}
        
        response = api_client.patch(
            f'/api/v1/profiles/{other_profile.public_id}/',
            update_data
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        other_profile.refresh_from_db()
        assert other_profile.bio == "Other user bio"  # Unchanged

    def test_profile_creation_not_allowed(self, api_client, authenticated_user):
        """Test that profiles cannot be created via API (auto-created with user)"""
        api_client.force_authenticate(user=authenticated_user)
        
        response = api_client.post('/api/v1/profiles/', {})
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_profile_deletion_not_allowed(self, api_client, authenticated_user):
        """Test that profiles cannot be deleted via API"""
        api_client.force_authenticate(user=authenticated_user)
        profile = authenticated_user.profile
        
        response = api_client.delete(f'/api/v1/profiles/{profile.public_id}/')
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_unauthenticated_cannot_update_profile(self, api_client, authenticated_user):
        """Test that unauthenticated users cannot update profiles"""
        profile = authenticated_user.profile
        
        update_data = {'bio': 'Unauthorized update'}
        
        response = api_client.patch(
            f'/api/v1/profiles/{profile.public_id}/',
            update_data
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserSettingsViewSet:
    """Test suite for UserSettings API endpoints"""

    def test_retrieve_own_settings(self, api_client, authenticated_user):
        """Test that users can retrieve their own settings"""
        api_client.force_authenticate(user=authenticated_user)
        
        response = api_client.get('/api/v1/settings/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['theme'] == "dark"
        assert 'email_notifications' in response.data
        assert 'metadata' in response.data

    def test_update_own_settings(self, api_client, authenticated_user):
        """Test that users can update their own settings"""
        api_client.force_authenticate(user=authenticated_user)
        
        update_data = {
            'theme': 'light',
            'language': 'es',
            'email_notifications': False,
            'metadata': {'custom': 'data'}
        }
        
        response = api_client.patch('/api/v1/settings/', update_data)
        
        assert response.status_code == status.HTTP_200_OK
        settings = authenticated_user.settings
        settings.refresh_from_db()
        assert settings.theme == 'light'
        assert settings.language == 'es'
        assert settings.email_notifications is False
        assert settings.metadata['custom'] == 'data'

    def test_cannot_access_other_user_settings(self, api_client, authenticated_user, other_user):
        """Test that users cannot access other users' settings"""
        api_client.force_authenticate(user=authenticated_user)
        
        # Try to get other user's settings by ID (should not work)
        other_settings = other_user.settings
        response = api_client.get(f'/api/v1/settings/{other_settings.public_id}/')
        
        # Should either 404 or return own settings only
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]

    def test_unauthenticated_cannot_access_settings(self, api_client):
        """Test that unauthenticated users cannot access settings"""
        response = api_client.get('/api/v1/settings/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_settings_auto_created_on_first_access(self, api_client):
        """Test that settings are auto-created if they don't exist"""
        user = User.objects.create_user(email="no_settings@test.com")
        api_client.force_authenticate(user=user)
        
        # User has no settings initially
        assert not hasattr(user, 'settings')
        
        response = api_client.get('/api/v1/settings/')
        
        assert response.status_code == status.HTTP_200_OK
        # Settings should now exist with defaults
        user.refresh_from_db()
        assert hasattr(user, 'settings')
        assert user.settings.theme == 'light'  # Default value

    def test_invalid_theme_validation(self, api_client, authenticated_user):
        """Test that invalid theme values are rejected"""
        api_client.force_authenticate(user=authenticated_user)
        
        update_data = {'theme': 'rainbow'}  # Invalid theme
        
        response = api_client.patch('/api/v1/settings/', update_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'theme' in response.data

    def test_invalid_visibility_validation(self, api_client, authenticated_user):
        """Test that invalid visibility values are rejected"""
        api_client.force_authenticate(user=authenticated_user)
        
        update_data = {'profile_visibility': 'invisible'}  # Invalid
        
        response = api_client.patch('/api/v1/settings/', update_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'profile_visibility' in response.data


@pytest.mark.django_db
class TestProfileSearch:
    """Test suite for profile search functionality"""

    def test_search_profiles_by_email(self, api_client):
        """Test searching profiles by user email"""
        User.objects.create_user(email="john.doe@test.com")
        User.objects.create_user(email="jane.smith@test.com")
        User.objects.create_user(email="bob.jones@test.com")
        
        # Auto-create profiles for all users
        for user in User.objects.all():
            Profile.objects.get_or_create(user=user)
        
        response = api_client.get('/api/v1/profiles/', {'search': 'jane'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert 'jane.smith@test.com' in response.data['results'][0]['user_email']

    def test_search_profiles_by_location(self, api_client):
        """Test searching profiles by location"""
        for i, location in enumerate(['New York', 'Los Angeles', 'New York']):
            user = User.objects.create_user(email=f"user{i}@test.com")
            Profile.objects.create(user=user, location=location)
        
        response = api_client.get('/api/v1/profiles/', {'search': 'New York'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_filter_profiles_by_company(self, api_client):
        """Test filtering profiles by company"""
        for i, company in enumerate(['Apple', 'Google', 'Apple']):
            user = User.objects.create_user(email=f"user{i}@test.com")
            Profile.objects.create(user=user, company=company)
        
        response = api_client.get('/api/v1/profiles/', {'company': 'Apple'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        for result in response.data['results']:
            profile = Profile.objects.get(public_id=result['public_id'])
            assert profile.company == 'Apple'