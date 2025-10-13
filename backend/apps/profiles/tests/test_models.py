"""
Tests for Profile and UserSettings models
Ham Dog & TC's TDD Salvation!

Following Commandment #6: TDD as salvation of our code!
"""
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from apps.profiles.models import Profile, UserSettings
from decimal import Decimal

User = get_user_model()


@pytest.mark.django_db
class TestProfileModel:
    """Test suite for Profile model"""

    def test_profile_creation_with_user(self):
        """Test that a profile can be created and linked to a user"""
        user = User.objects.create_user(
            email="hamdog@test.com"
        )
        profile = Profile.objects.create(
            user=user,
            bio="Socialist coder who believes in TDD salvation",
            location="Code Heaven",
            website="https://hamdog.dev",
            company="Ham Dog & TC Inc."
        )
        
        assert profile.user == user
        assert profile.bio == "Socialist coder who believes in TDD salvation"
        assert profile.location == "Code Heaven"
        assert profile.website == "https://hamdog.dev"
        assert profile.company == "Ham Dog & TC Inc."
        assert profile.public_id is not None  # UUID should be auto-generated
        assert profile.created_at is not None
        assert profile.updated_at is not None

    def test_profile_one_to_one_with_user(self):
        """Test that each user can only have one profile"""
        user = User.objects.create_user(
            email="tc@test.com"
        )
        
        # Create first profile
        profile1 = Profile.objects.create(user=user)
        
        # Attempt to create second profile should fail
        with pytest.raises(IntegrityError):
            Profile.objects.create(user=user)

    def test_profile_str_representation(self):
        """Test the string representation of Profile"""
        user = User.objects.create_user(
            email="test@test.com"
        )
        profile = Profile.objects.create(user=user)
        
        assert str(profile) == f"Profile for test@test.com"

    def test_profile_avatar_url_field(self):
        """Test that profile can store avatar URL"""
        user = User.objects.create_user(
            email="avatar@test.com"
        )
        profile = Profile.objects.create(
            user=user,
            avatar_url="https://example.com/avatar.jpg"
        )
        
        assert profile.avatar_url == "https://example.com/avatar.jpg"

    def test_profile_optional_fields_are_nullable(self):
        """Test that all profile fields except user are optional"""
        user = User.objects.create_user(
            email="minimal@test.com"
        )
        profile = Profile.objects.create(user=user)
        
        assert profile.bio == ""
        assert profile.location == ""
        assert profile.website == ""
        assert profile.company == ""
        assert profile.avatar_url == ""

    def test_profile_inherits_from_base_model(self):
        """Test that Profile inherits from BaseModel with all features"""
        user = User.objects.create_user(
            email="base@test.com"
        )
        profile = Profile.objects.create(user=user)
        
        # Check BaseModel features
        assert hasattr(profile, 'public_id')
        assert hasattr(profile, 'created_at')
        assert hasattr(profile, 'updated_at')
        assert hasattr(profile, 'is_deleted')
        assert hasattr(profile, 'soft_delete')
        assert hasattr(profile, 'restore')

    def test_profile_soft_delete(self):
        """Test soft delete functionality"""
        user = User.objects.create_user(
            email="softdel@test.com"
        )
        profile = Profile.objects.create(user=user)
        
        # Soft delete the profile
        profile.soft_delete(user=user)
        
        assert profile.is_deleted is True
        assert profile.deleted_at is not None
        assert profile.deleted_by == user
        assert not profile.is_active

    def test_profile_cascade_delete_with_user(self):
        """Test that profile is deleted when user is deleted"""
        user = User.objects.create_user(
            email="cascade@test.com"
        )
        profile = Profile.objects.create(user=user)
        profile_id = profile.id
        
        # Delete the user
        user.delete()
        
        # Profile should also be deleted
        assert not Profile.objects.filter(id=profile_id).exists()


@pytest.mark.django_db
class TestUserSettingsModel:
    """Test suite for UserSettings model"""

    def test_user_settings_creation(self):
        """Test that user settings can be created with defaults"""
        user = User.objects.create_user(
            email="settings@test.com"
        )
        settings = UserSettings.objects.create(user=user)
        
        assert settings.user == user
        assert settings.email_notifications is True  # Should default to True
        assert settings.push_notifications is False  # Should default to False
        assert settings.theme == "light"  # Should default to light
        assert settings.language == "en"  # Should default to English
        assert settings.timezone == "UTC"  # Should default to UTC

    def test_user_settings_one_to_one_with_user(self):
        """Test that each user can only have one settings object"""
        user = User.objects.create_user(
            email="unique@test.com"
        )
        
        # Create first settings
        settings1 = UserSettings.objects.create(user=user)
        
        # Attempt to create second settings should fail
        with pytest.raises(IntegrityError):
            UserSettings.objects.create(user=user)

    def test_user_settings_theme_choices(self):
        """Test that theme field only accepts valid choices"""
        user = User.objects.create_user(
            email="theme@test.com"
        )
        
        # Valid themes
        for theme in ["light", "dark", "auto"]:
            settings = UserSettings.objects.create(user=user)
            settings.theme = theme
            settings.full_clean()  # Should not raise
            settings.delete()

    def test_user_settings_language_choices(self):
        """Test that language field accepts common language codes"""
        user = User.objects.create_user(
            email="lang@test.com"
        )
        
        # Common language codes
        for lang in ["en", "es", "fr", "de", "zh", "ja"]:
            settings = UserSettings.objects.create(user=user)
            settings.language = lang
            settings.full_clean()  # Should not raise
            settings.delete()

    def test_user_settings_privacy_settings(self):
        """Test privacy-related settings"""
        user = User.objects.create_user(
            email="privacy@test.com"
        )
        settings = UserSettings.objects.create(
            user=user,
            profile_visibility="private",
            show_email=False,
            show_activity=False
        )
        
        assert settings.profile_visibility == "private"
        assert settings.show_email is False
        assert settings.show_activity is False

    def test_user_settings_visibility_choices(self):
        """Test profile visibility choices"""
        user = User.objects.create_user(
            email="visibility@test.com"
        )
        
        # Valid visibility options
        for visibility in ["public", "private", "friends"]:
            settings = UserSettings.objects.create(user=user)
            settings.profile_visibility = visibility
            settings.full_clean()  # Should not raise
            settings.delete()

    def test_user_settings_str_representation(self):
        """Test the string representation of UserSettings"""
        user = User.objects.create_user(
            email="str@test.com"
        )
        settings = UserSettings.objects.create(user=user)
        
        assert str(settings) == f"Settings for str@test.com"

    def test_user_settings_inherits_from_simple_base_model(self):
        """Test that UserSettings inherits from SimpleBaseModel"""
        user = User.objects.create_user(
            email="simple@test.com"
        )
        settings = UserSettings.objects.create(user=user)
        
        # Check SimpleBaseModel features
        assert hasattr(settings, 'public_id')
        assert hasattr(settings, 'created_at')
        assert hasattr(settings, 'updated_at')
        
        # Should NOT have audit/soft delete features
        assert not hasattr(settings, 'is_deleted')
        assert not hasattr(settings, 'soft_delete')

    def test_user_settings_cascade_delete_with_user(self):
        """Test that settings are deleted when user is deleted"""
        user = User.objects.create_user(
            email="cascade_settings@test.com"
        )
        settings = UserSettings.objects.create(user=user)
        settings_id = settings.id
        
        # Delete the user
        user.delete()
        
        # Settings should also be deleted
        assert not UserSettings.objects.filter(id=settings_id).exists()

    def test_user_settings_metadata_json_field(self):
        """Test that settings can store arbitrary metadata as JSON"""
        user = User.objects.create_user(
            email="meta@test.com"
        )
        metadata = {
            "last_tour_shown": "2024-01-01",
            "preferences": {
                "sidebar_collapsed": True,
                "default_view": "grid"
            }
        }
        settings = UserSettings.objects.create(
            user=user,
            metadata=metadata
        )
        
        assert settings.metadata == metadata
        assert settings.metadata["preferences"]["sidebar_collapsed"] is True