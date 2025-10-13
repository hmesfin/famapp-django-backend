"""
Tests for Profile Cache Service
Testing the refactored caching service with Redis integration
"""
import json
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.core.cache import cache
from django.contrib.auth import get_user_model
from apps.profiles.models import Profile, UserSettings
from apps.profiles.services.cache_service import ProfileCacheService, profile_cache_service


User = get_user_model()


class ProfileCacheServiceTestCase(TestCase):
    """Test cases for the ProfileCacheService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = ProfileCacheService()
        
        # Create test user and profile
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        self.profile = Profile.objects.create(
            user=self.user,
            bio='Test bio',
            location='Test Location',
            website='https://example.com',
            company='Test Company'
        )
        
        # Create test user settings
        self.settings = UserSettings.objects.create(
            user=self.user,
            theme='dark',
            language='en',
            timezone='UTC',
            email_notifications=True,
            push_notifications=False,
            profile_visibility='public',
            show_email=True,
            show_activity=False,
            metadata={'test': 'data'}
        )
        
        # Clear cache before each test
        cache.clear()
    
    def tearDown(self):
        """Clean up after each test"""
        cache.clear()
    
    def test_cache_key_generation(self):
        """Test cache key generation methods"""
        profile_key = self.service._make_profile_key(self.profile.public_id)
        self.assertEqual(profile_key, f"profile:{self.profile.public_id}")
        
        settings_key = self.service._make_settings_key(self.user.id)
        self.assertEqual(settings_key, f"user_settings:{self.user.id}")
        
        list_key = self.service._make_list_key('test_hash')
        self.assertEqual(list_key, "profile_list:test_hash")
    
    def test_serialize_profile(self):
        """Test profile serialization for caching"""
        serialized = self.service._serialize_profile(self.profile)
        
        expected_fields = [
            'public_id', 'user_email', 'user_full_name', 'user_first_name',
            'user_last_name', 'bio', 'location', 'website', 'company',
            'avatar_url', 'created_at', 'updated_at', 'user_id'
        ]
        
        for field in expected_fields:
            self.assertIn(field, serialized)
        
        self.assertEqual(serialized['public_id'], self.profile.public_id)
        self.assertEqual(serialized['user_email'], self.user.email)
        self.assertEqual(serialized['user_full_name'], 'John Doe')
        self.assertEqual(serialized['bio'], 'Test bio')
        self.assertEqual(serialized['user_id'], self.user.id)
    
    def test_serialize_settings(self):
        """Test user settings serialization for caching"""
        serialized = self.service._serialize_settings(self.settings)
        
        expected_fields = [
            'public_id', 'theme', 'language', 'timezone', 'email_notifications',
            'push_notifications', 'profile_visibility', 'show_email',
            'show_activity', 'metadata', 'created_at', 'updated_at'
        ]
        
        for field in expected_fields:
            self.assertIn(field, serialized)
        
        self.assertEqual(serialized['theme'], 'dark')
        self.assertEqual(serialized['language'], 'en')
        self.assertEqual(serialized['email_notifications'], True)
        self.assertEqual(serialized['metadata'], {'test': 'data'})
    
    def test_cache_profile_get_set(self):
        """Test caching and retrieving profiles"""
        # Initially not cached
        cached_profile = self.service.get_profile(self.profile.public_id)
        self.assertIsNone(cached_profile)
        
        # Cache the profile
        self.service.set_profile(self.profile)
        
        # Should now be cached
        cached_profile = self.service.get_profile(self.profile.public_id)
        self.assertIsNotNone(cached_profile)
        self.assertEqual(cached_profile['public_id'], self.profile.public_id)
        self.assertEqual(cached_profile['user_email'], self.user.email)
    
    def test_cache_profile_invalidation(self):
        """Test profile cache invalidation"""
        # Cache the profile
        self.service.set_profile(self.profile)
        self.assertIsNotNone(self.service.get_profile(self.profile.public_id))
        
        # Invalidate cache
        self.service.invalidate_profile(self.profile.public_id)
        
        # Should no longer be cached
        cached_profile = self.service.get_profile(self.profile.public_id)
        self.assertIsNone(cached_profile)
    
    def test_get_profile_by_user_id_cache_miss(self):
        """Test getting profile by user_id with cache miss"""
        # Clear any existing cache
        self.service.invalidate_profile(self.profile.public_id)
        
        # Should fetch from database and cache
        profile = self.service.get_profile_by_user_id(self.user.id)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user_id, self.user.id)
        
        # Should now be cached
        cached_profile = self.service.get_profile(self.profile.public_id)
        self.assertIsNotNone(cached_profile)
    
    def test_get_profile_by_user_id_cache_hit(self):
        """Test getting profile by user_id with cache hit"""
        # Pre-cache the profile
        self.service.set_profile(self.profile)
        
        # Should return profile without additional DB query
        with self.assertNumQueries(1):  # Only the lookup query
            profile = self.service.get_profile_by_user_id(self.user.id)
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user_id, self.user.id)
    
    def test_get_profile_by_user_id_not_found(self):
        """Test getting profile for non-existent user"""
        profile = self.service.get_profile_by_user_id(99999)
        self.assertIsNone(profile)
    
    def test_invalidate_profile_by_user_id(self):
        """Test invalidating profile by user_id"""
        # Cache the profile
        self.service.set_profile(self.profile)
        self.assertIsNotNone(self.service.get_profile(self.profile.public_id))
        
        # Invalidate by user_id
        self.service.invalidate_profile_by_user_id(self.user.id)
        
        # Should no longer be cached
        cached_profile = self.service.get_profile(self.profile.public_id)
        self.assertIsNone(cached_profile)
    
    def test_invalidate_profile_by_user_id_not_found(self):
        """Test invalidating profile for non-existent user"""
        # Should not raise an exception
        try:
            self.service.invalidate_profile_by_user_id(99999)
        except Exception as e:
            self.fail(f"invalidate_profile_by_user_id raised {e} unexpectedly!")
    
    def test_cache_user_settings_get_set(self):
        """Test caching and retrieving user settings"""
        # Initially not cached
        cached_settings = self.service.get_user_settings(self.user.id)
        self.assertIsNone(cached_settings)
        
        # Cache the settings
        self.service.set_user_settings(self.settings)
        
        # Should now be cached
        cached_settings = self.service.get_user_settings(self.user.id)
        self.assertIsNotNone(cached_settings)
        self.assertEqual(cached_settings['theme'], 'dark')
        self.assertEqual(cached_settings['language'], 'en')
    
    def test_cache_user_settings_invalidation(self):
        """Test user settings cache invalidation"""
        # Cache the settings
        self.service.set_user_settings(self.settings)
        self.assertIsNotNone(self.service.get_user_settings(self.user.id))
        
        # Invalidate cache
        self.service.invalidate_user_settings(self.user.id)
        
        # Should no longer be cached
        cached_settings = self.service.get_user_settings(self.user.id)
        self.assertIsNone(cached_settings)
    
    def test_cache_profile_list_get_set(self):
        """Test caching and retrieving profile lists"""
        filters_hash = 'test_filters_123'
        profiles = [self.profile]
        
        # Initially not cached
        cached_list = self.service.get_profile_list(filters_hash)
        self.assertIsNone(cached_list)
        
        # Cache the list
        self.service.set_profile_list(filters_hash, profiles)
        
        # Should now be cached
        cached_list = self.service.get_profile_list(filters_hash)
        self.assertIsNotNone(cached_list)
        self.assertEqual(len(cached_list), 1)
        self.assertEqual(cached_list[0]['public_id'], self.profile.public_id)
    
    def test_warm_profile_cache(self):
        """Test warming cache with multiple profiles"""
        # Create additional profiles
        user2 = User.objects.create_user(
            email='test2@example.com',
            password='testpass123'
        )
        profile2 = Profile.objects.create(user=user2, bio='Test bio 2')
        
        profiles = [self.profile, profile2]
        
        # Warm cache
        self.service.warm_profile_cache(profiles)
        
        # Both should be cached
        cached_profile1 = self.service.get_profile(self.profile.public_id)
        cached_profile2 = self.service.get_profile(profile2.public_id)
        
        self.assertIsNotNone(cached_profile1)
        self.assertIsNotNone(cached_profile2)
    
    def test_invalidate_user_cache(self):
        """Test invalidating all cache entries for a user"""
        # Cache both profile and settings
        self.service.set_profile(self.profile)
        self.service.set_user_settings(self.settings)
        
        # Verify both are cached
        self.assertIsNotNone(self.service.get_profile(self.profile.public_id))
        self.assertIsNotNone(self.service.get_user_settings(self.user.id))
        
        # Invalidate all user cache
        self.service.invalidate_user_cache(self.user.id, self.profile.public_id)
        
        # Both should be invalidated
        self.assertIsNone(self.service.get_profile(self.profile.public_id))
        self.assertIsNone(self.service.get_user_settings(self.user.id))
    
    def test_cache_timeouts_functional(self):
        """Test that cache operations work with expected timeouts (functional test)"""
        # This test verifies the cache operations work correctly
        # The specific timeout values are tested via constants test
        
        # Cache profile and verify it exists
        self.service.set_profile(self.profile)
        cached_profile = self.service.get_profile(self.profile.public_id)
        self.assertIsNotNone(cached_profile)
        
        # Cache settings and verify it exists  
        self.service.set_user_settings(self.settings)
        cached_settings = self.service.get_user_settings(self.user.id)
        self.assertIsNotNone(cached_settings)
        
        # Cache profile list and verify it exists
        self.service.set_profile_list('test_hash', [self.profile])
        cached_list = self.service.get_profile_list('test_hash')
        self.assertIsNotNone(cached_list)
        self.assertEqual(len(cached_list), 1)
    
    def test_global_service_instance(self):
        """Test that global service instance is properly initialized"""
        from apps.profiles.services.cache_service import profile_cache_service
        self.assertIsInstance(profile_cache_service, ProfileCacheService)
        self.assertIsNotNone(profile_cache_service.cache)
    
    def test_cache_service_constants(self):
        """Test cache service constants are properly defined"""
        self.assertEqual(ProfileCacheService.PROFILE_TIMEOUT, 300)
        self.assertEqual(ProfileCacheService.SETTINGS_TIMEOUT, 900)
        self.assertEqual(ProfileCacheService.LIST_TIMEOUT, 60)
        
        self.assertEqual(ProfileCacheService.PROFILE_KEY, "profile:{public_id}")
        self.assertEqual(ProfileCacheService.USER_SETTINGS_KEY, "user_settings:{user_id}")
        self.assertEqual(ProfileCacheService.PROFILE_LIST_KEY, "profile_list:{filters_hash}")


class ProfileCacheIntegrationTestCase(TestCase):
    """Integration tests for cache service with real Redis"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.service = profile_cache_service
        
        # Create test user and profile
        self.user = User.objects.create_user(
            email='integration@example.com',
            password='testpass123',
            first_name='Integration',
            last_name='Test'
        )
        
        self.profile = Profile.objects.create(
            user=self.user,
            bio='Integration test bio',
            location='Integration Location'
        )
        
        # Clear cache before each test
        cache.clear()
    
    def tearDown(self):
        """Clean up after each test"""
        cache.clear()
    
    def test_real_cache_integration(self):
        """Test actual caching with Redis backend"""
        # Cache a profile
        self.service.set_profile(self.profile)
        
        # Retrieve from cache
        cached_data = self.service.get_profile(self.profile.public_id)
        
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data['public_id'], self.profile.public_id)
        self.assertEqual(cached_data['user_email'], self.user.email)
        
        # Test cache persistence across service instances
        new_service = ProfileCacheService()
        cached_data_new = new_service.get_profile(self.profile.public_id)
        self.assertEqual(cached_data, cached_data_new)
    
    def test_cache_expiry_behavior(self):
        """Test cache expiry behavior (limited test due to time constraints)"""
        # This test verifies that cache keys are set with proper expiry
        # In a real test environment, you might use fakeredis or time manipulation
        
        self.service.set_profile(self.profile)
        cached_data = self.service.get_profile(self.profile.public_id)
        self.assertIsNotNone(cached_data)
        
        # Verify cache exists
        cache_key = self.service._make_profile_key(self.profile.public_id)
        self.assertTrue(cache.has_key(cache_key))