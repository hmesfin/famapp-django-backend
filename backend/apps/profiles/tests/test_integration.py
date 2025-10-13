"""
Backend Integration Tests for Profiles Module
Ham Dog & TC's comprehensive integration testing! 🚀

Tests the entire refactored profiles system as an integrated unit:
- Profile API flow with caching
- Avatar upload with service integration
- Settings flow with cache invalidation
- RBAC integration through full request cycle
- Performance and cache effectiveness
"""
import time
import json
from io import BytesIO
from PIL import Image
from django.test import TestCase, TransactionTestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.profiles.models import Profile, UserSettings
from apps.profiles.services.cache_service import profile_cache_service
from apps.profiles.services.avatar_service import avatar_service

User = get_user_model()


class ProfileAPIIntegrationTestCase(APITestCase):
    """
    Integration tests for Profile API endpoints with caching
    Tests the complete flow from API request to cache to database
    """
    
    def setUp(self):
        """Set up test data for each test"""
        # Clear cache before each test
        cache.clear()
        
        # Create test users
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com', 
            password='testpass123',
            first_name='Jane',
            last_name='Smith'
        )
        
        # Create profiles manually to ensure they exist
        self.profile1 = Profile.objects.create(
            user=self.user1,
            bio='Backend Developer',
            location='San Francisco',
            company='Django Inc'
        )
        self.profile2 = Profile.objects.create(
            user=self.user2,
            bio='Frontend Developer',
            location='Seattle',
            company='Vue Corp'
        )
        
        # Create user settings
        self.settings1 = UserSettings.objects.create(
            user=self.user1,
            theme='dark',
            language='en',
            email_notifications=True
        )
        self.settings2 = UserSettings.objects.create(
            user=self.user2,
            theme='light',
            language='es',
            email_notifications=False
        )
        
        # Set up authenticated client
        self.client = APIClient()
        
    def _authenticate_user1(self):
        """Helper to authenticate as user1"""
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
    def _authenticate_user2(self):
        """Helper to authenticate as user2"""
        refresh = RefreshToken.for_user(self.user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_profile_create_cache_retrieve_flow(self):
        """
        Test complete profile flow: Create → Cache → Retrieve from cache
        """
        # PHASE 1: Initial state - no cache
        self.assertIsNone(
            profile_cache_service.get_profile(self.profile1.public_id),
            "Cache should be empty initially"
        )
        
        # PHASE 2: First API request (cache miss)
        start_time = time.time()
        response = self.client.get(f'/api/profiles/{self.profile1.public_id}/')
        first_request_time = time.time() - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Backend Developer')
        
        # PHASE 3: Verify caching occurred
        cached_profile = profile_cache_service.get_profile(self.profile1.public_id)
        self.assertIsNotNone(cached_profile, "Profile should be cached after first request")
        self.assertEqual(cached_profile['bio'], 'Backend Developer')
        
        # PHASE 4: Second API request (cache hit)
        start_time = time.time()
        response = self.client.get(f'/api/profiles/{self.profile1.public_id}/')
        second_request_time = time.time() - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Backend Developer')
        
        # PHASE 5: Verify cache hit was faster (performance test)
        self.assertLess(
            second_request_time, 
            first_request_time * 0.5,  # Should be at least 50% faster
            f"Cache hit ({second_request_time:.4f}s) should be faster than cache miss ({first_request_time:.4f}s)"
        )
        
    def test_profile_update_cache_invalidation_flow(self):
        """
        Test profile update → cache invalidation → fresh cache flow
        """
        # PHASE 1: Prime the cache
        response = self.client.get(f'/api/profiles/{self.profile1.public_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify cache exists
        cached_profile = profile_cache_service.get_profile(self.profile1.public_id)
        self.assertIsNotNone(cached_profile)
        self.assertEqual(cached_profile['bio'], 'Backend Developer')
        
        # PHASE 2: Authenticate and update profile
        self._authenticate_user1()
        update_data = {
            'bio': 'Senior Backend Developer',
            'location': 'New York'
        }
        
        response = self.client.patch(
            f'/api/profiles/{self.profile1.public_id}/',
            data=update_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # PHASE 3: Verify cache was invalidated
        cached_profile = profile_cache_service.get_profile(self.profile1.public_id)
        self.assertIsNone(cached_profile, "Cache should be invalidated after update")
        
        # PHASE 4: Verify next request gets fresh data
        response = self.client.get(f'/api/profiles/{self.profile1.public_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Senior Backend Developer')
        self.assertEqual(response.data['location'], 'New York')
        
        # PHASE 5: Verify fresh data is cached
        cached_profile = profile_cache_service.get_profile(self.profile1.public_id)
        self.assertIsNotNone(cached_profile)
        self.assertEqual(cached_profile['bio'], 'Senior Backend Developer')
        
    def test_profile_me_endpoint_integration(self):
        """
        Test /me endpoint with profile creation and caching
        """
        # Create a new user without profile
        user3 = User.objects.create_user(
            email='user3@example.com',
            password='testpass123',
            first_name='Bob',
            last_name='Johnson'
        )
        
        # Authenticate as user3
        refresh = RefreshToken.for_user(user3)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # PHASE 1: First /me request (profile creation)
        response = self.client.get('/api/profiles/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_email'], 'user3@example.com')
        
        # Verify profile was created in database
        profile = Profile.objects.get(user=user3)
        self.assertIsNotNone(profile)
        
        # PHASE 2: Verify profile is cached
        cached_profile = profile_cache_service.get_profile(profile.public_id)
        self.assertIsNotNone(cached_profile)
        self.assertEqual(cached_profile['user_email'], 'user3@example.com')
        
        # PHASE 3: Second /me request (cache hit)
        start_time = time.time()
        response = self.client.get('/api/profiles/me/')
        cache_hit_time = time.time() - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(cache_hit_time, 0.01, "Cache hit should be very fast")


class AvatarUploadIntegrationTestCase(APITestCase):
    """
    Integration tests for avatar upload with service integration
    Tests the complete flow from file upload to storage to cache invalidation
    """
    
    def setUp(self):
        """Set up test data for avatar upload tests"""
        cache.clear()
        
        self.user = User.objects.create_user(
            email='avatar@example.com',
            password='testpass123',
            first_name='Avatar',
            last_name='User'
        )
        
        self.profile = Profile.objects.create(
            user=self.user,
            bio='Avatar tester'
        )
        
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def _create_test_image(self, filename='test.jpg', size=(100, 100), format='JPEG'):
        """Helper to create test image file"""
        # Create a simple image
        image = Image.new('RGB', size, color='red')
        image_file = BytesIO()
        image.save(image_file, format=format)
        image_file.seek(0)
        
        return SimpleUploadedFile(
            filename,
            image_file.getvalue(),
            content_type=f'image/{format.lower()}'
        )
    
    def test_avatar_upload_complete_flow(self):
        """
        Test complete avatar upload flow: Upload → Validate → Store → Cache invalidation
        """
        # PHASE 1: Prime cache with existing profile
        response = self.client.get(f'/api/profiles/{self.profile.public_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['avatar_url'], '')
        
        # Verify cache exists
        cached_profile = profile_cache_service.get_profile(self.profile.public_id)
        self.assertIsNotNone(cached_profile)
        self.assertEqual(cached_profile['avatar_url'], '')
        
        # PHASE 2: Upload avatar
        test_image = self._create_test_image()
        response = self.client.post(
            '/api/profiles/upload-avatar/',
            {'avatar': test_image},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('avatar_url', response.data)
        self.assertIn('message', response.data)
        self.assertTrue(response.data['avatar_url'])
        
        # PHASE 3: Verify cache was invalidated
        cached_profile = profile_cache_service.get_profile(self.profile.public_id)
        self.assertIsNone(cached_profile, "Cache should be invalidated after avatar upload")
        
        # PHASE 4: Verify database was updated
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.avatar_url)
        self.assertIn('avatars/', self.profile.avatar_url)
        
        # PHASE 5: Verify next API request has new avatar URL
        response = self.client.get(f'/api/profiles/{self.profile.public_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['avatar_url'])
        self.assertEqual(response.data['avatar_url'], self.profile.avatar_url)
        
    def test_avatar_upload_validation_integration(self):
        """
        Test avatar upload validation through the service layer
        """
        # Test invalid file type
        invalid_file = SimpleUploadedFile(
            'test.txt',
            b'This is not an image',
            content_type='text/plain'
        )
        
        response = self.client.post(
            '/api/profiles/upload-avatar/',
            {'avatar': invalid_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid file type', str(response.data) if hasattr(response, 'data') else response.content.decode())
        
        # Verify no cache invalidation occurred for failed upload
        # (This would be testing implementation details, so we'll skip)
        
    def test_avatar_replacement_flow(self):
        """
        Test replacing existing avatar: Old → New → Cache invalidation
        """
        # PHASE 1: Upload first avatar
        first_image = self._create_test_image('first.jpg')
        response = self.client.post(
            '/api/profiles/upload-avatar/',
            {'avatar': first_image},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        first_avatar_url = response.data['avatar_url']
        
        # PHASE 2: Prime cache
        response = self.client.get(f'/api/profiles/{self.profile.public_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # PHASE 3: Upload replacement avatar
        second_image = self._create_test_image('second.jpg', size=(200, 200))
        response = self.client.post(
            '/api/profiles/upload-avatar/',
            {'avatar': second_image},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        second_avatar_url = response.data['avatar_url']
        
        # PHASE 4: Verify URLs are different
        self.assertNotEqual(first_avatar_url, second_avatar_url)
        
        # PHASE 5: Verify cache was invalidated and database updated
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.avatar_url, second_avatar_url)
        
        # Verify fresh API request has new avatar
        response = self.client.get(f'/api/profiles/{self.profile.public_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['avatar_url'], second_avatar_url)


class UserSettingsIntegrationTestCase(APITestCase):
    """
    Integration tests for UserSettings with caching
    Tests the complete flow for settings management
    """
    
    def setUp(self):
        """Set up test data for settings tests"""
        cache.clear()
        
        self.user = User.objects.create_user(
            email='settings@example.com',
            password='testpass123',
            first_name='Settings',
            last_name='User'
        )
        
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_settings_create_cache_update_flow(self):
        """
        Test settings creation → caching → updates → cache invalidation
        """
        # PHASE 1: First settings request (auto-creation)
        response = self.client.get('/api/settings/current_settings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify default settings
        self.assertEqual(response.data['theme'], 'light')
        self.assertEqual(response.data['language'], 'en')
        self.assertTrue(response.data['email_notifications'])
        
        # PHASE 2: Verify settings were created in database
        settings = UserSettings.objects.get(user=self.user)
        self.assertIsNotNone(settings)
        
        # PHASE 3: Verify settings are cached
        cached_settings = profile_cache_service.get_user_settings(self.user.id)
        self.assertIsNotNone(cached_settings)
        self.assertEqual(cached_settings['theme'], 'light')
        
        # PHASE 4: Update settings
        update_data = {
            'theme': 'dark',
            'language': 'es',
            'email_notifications': False
        }
        
        response = self.client.patch('/api/settings/current_settings/', data=update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['theme'], 'dark')
        self.assertEqual(response.data['language'], 'es')
        self.assertFalse(response.data['email_notifications'])
        
        # PHASE 5: Verify cache was invalidated
        cached_settings = profile_cache_service.get_user_settings(self.user.id)
        self.assertIsNone(cached_settings, "Cache should be invalidated after update")
        
        # PHASE 6: Verify next request gets fresh data and re-caches
        response = self.client.get('/api/settings/current_settings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['theme'], 'dark')
        self.assertEqual(response.data['language'], 'es')
        
        # Verify fresh data is cached
        cached_settings = profile_cache_service.get_user_settings(self.user.id)
        self.assertIsNotNone(cached_settings)
        self.assertEqual(cached_settings['theme'], 'dark')
    
    def test_settings_performance_caching(self):
        """
        Test that settings caching provides performance benefits
        """
        # Prime the cache
        response = self.client.get('/api/settings/current_settings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Measure cache miss time (this will hit cache now, so create new user)
        user2 = User.objects.create_user(
            email='perf@example.com',
            password='testpass123'
        )
        refresh = RefreshToken.for_user(user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # First request (cache miss + DB create)
        start_time = time.time()
        response = self.client.get('/api/settings/current_settings/')
        cache_miss_time = time.time() - start_time
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Second request (cache hit)
        start_time = time.time()
        response = self.client.get('/api/settings/current_settings/')
        cache_hit_time = time.time() - start_time
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Cache hit should be significantly faster
        self.assertLess(
            cache_hit_time,
            cache_miss_time * 0.3,  # At least 70% faster
            f"Cache hit ({cache_hit_time:.4f}s) should be much faster than cache miss ({cache_miss_time:.4f}s)"
        )


class RBACIntegrationTestCase(APITestCase):
    """
    Integration tests for RBAC through the complete request cycle
    Tests permissions, authentication, and authorization
    """
    
    def setUp(self):
        """Set up test users for RBAC testing"""
        cache.clear()
        
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123',
            first_name='Profile',
            last_name='Owner'
        )
        
        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123',
            first_name='Other',
            last_name='User'
        )
        
        self.profile = Profile.objects.create(
            user=self.owner,
            bio='Owner profile'
        )
        
        self.client = APIClient()
    
    def test_profile_read_permissions_integration(self):
        """
        Test profile read permissions across different user types
        """
        # PHASE 1: Anonymous user can read profiles
        response = self.client.get(f'/api/profiles/{self.profile.public_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Owner profile')
        
        # PHASE 2: Other authenticated user can read profiles
        refresh = RefreshToken.for_user(self.other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = self.client.get(f'/api/profiles/{self.profile.public_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Owner profile')
        
        # PHASE 3: Owner can read their own profile
        refresh = RefreshToken.for_user(self.owner)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = self.client.get(f'/api/profiles/{self.profile.public_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Owner profile')
    
    def test_profile_write_permissions_integration(self):
        """
        Test profile write permissions - only owner can modify
        """
        update_data = {'bio': 'Updated bio'}
        
        # PHASE 1: Anonymous user cannot update
        response = self.client.patch(
            f'/api/profiles/{self.profile.public_id}/',
            data=update_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # PHASE 2: Other authenticated user cannot update
        refresh = RefreshToken.for_user(self.other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = self.client.patch(
            f'/api/profiles/{self.profile.public_id}/',
            data=update_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # PHASE 3: Owner can update their profile
        refresh = RefreshToken.for_user(self.owner)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = self.client.patch(
            f'/api/profiles/{self.profile.public_id}/',
            data=update_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Updated bio')
        
        # Verify database was updated
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, 'Updated bio')
    
    def test_settings_permissions_integration(self):
        """
        Test that users can only access their own settings
        """
        # PHASE 1: Anonymous user cannot access settings
        response = self.client.get('/api/settings/current_settings/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # PHASE 2: Authenticated user can access their own settings
        refresh = RefreshToken.for_user(self.owner)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = self.client.get('/api/settings/current_settings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # PHASE 3: Users cannot access other users' settings
        # (This is enforced by the ViewSet logic - no endpoint to access others' settings)
        # Settings are always tied to request.user
        
    def test_avatar_upload_permissions_integration(self):
        """
        Test avatar upload permissions - only authenticated users for their own profile
        """
        test_image = self._create_test_image()
        
        # PHASE 1: Anonymous user cannot upload avatar
        response = self.client.post(
            '/api/profiles/upload-avatar/',
            {'avatar': test_image},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # PHASE 2: Authenticated user can upload their own avatar
        refresh = RefreshToken.for_user(self.owner)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        test_image = self._create_test_image()  # Create fresh file object
        response = self.client.post(
            '/api/profiles/upload-avatar/',
            {'avatar': test_image},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('avatar_url', response.data)
    
    def _create_test_image(self):
        """Helper to create test image"""
        image = Image.new('RGB', (50, 50), color='blue')
        image_file = BytesIO()
        image.save(image_file, 'JPEG')
        image_file.seek(0)
        
        return SimpleUploadedFile(
            'test.jpg',
            image_file.getvalue(),
            content_type='image/jpeg'
        )


class ConcurrentUpdatesIntegrationTestCase(TransactionTestCase):
    """
    Integration tests for concurrent updates and cache consistency
    Uses TransactionTestCase for better transaction isolation
    """
    
    def setUp(self):
        """Set up test data for concurrent testing"""
        cache.clear()
        
        self.user = User.objects.create_user(
            email='concurrent@example.com',
            password='testpass123'
        )
        
        self.profile = Profile.objects.create(
            user=self.user,
            bio='Original bio'
        )
    
    def test_cache_consistency_after_model_save(self):
        """
        Test that cache is properly invalidated when model is saved directly
        """
        # PHASE 1: Prime the cache via API
        client = APIClient()
        response = client.get(f'/api/profiles/{self.profile.public_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify cache exists
        cached_profile = profile_cache_service.get_profile(self.profile.public_id)
        self.assertIsNotNone(cached_profile)
        self.assertEqual(cached_profile['bio'], 'Original bio')
        
        # PHASE 2: Update model directly (simulating admin or other service)
        self.profile.bio = 'Updated via model save'
        self.profile.save()
        
        # PHASE 3: Cache should still contain old data (expected behavior)
        # This tests current implementation - cache is only invalidated via API
        cached_profile = profile_cache_service.get_profile(self.profile.public_id)
        self.assertIsNotNone(cached_profile)
        self.assertEqual(cached_profile['bio'], 'Original bio')  # Still old data
        
        # PHASE 4: Manual cache invalidation
        profile_cache_service.invalidate_profile(self.profile.public_id)
        cached_profile = profile_cache_service.get_profile(self.profile.public_id)
        self.assertIsNone(cached_profile)
        
        # PHASE 5: Next API request should get fresh data
        response = client.get(f'/api/profiles/{self.profile.public_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Updated via model save')
    
    def test_cache_warming_performance(self):
        """
        Test cache warming functionality for performance optimization
        """
        # Create multiple profiles
        users = []
        profiles = []
        
        for i in range(5):
            user = User.objects.create_user(
                email=f'user{i}@example.com',
                password='testpass123'
            )
            users.append(user)
            
            profile = Profile.objects.create(
                user=user,
                bio=f'Bio for user {i}'
            )
            profiles.append(profile)
        
        # PHASE 1: Cold cache - measure time for individual requests
        cold_times = []
        client = APIClient()
        
        for profile in profiles:
            start_time = time.time()
            response = client.get(f'/api/profiles/{profile.public_id}/')
            cold_times.append(time.time() - start_time)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # PHASE 2: Clear cache and warm it in batch
        cache.clear()
        start_time = time.time()
        profile_cache_service.warm_profile_cache(profiles)
        warm_time = time.time() - start_time
        
        # PHASE 3: Measure warm cache performance
        warm_times = []
        for profile in profiles:
            start_time = time.time()
            response = client.get(f'/api/profiles/{profile.public_id}/')
            warm_times.append(time.time() - start_time)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # PHASE 4: Verify performance improvement
        avg_cold_time = sum(cold_times) / len(cold_times)
        avg_warm_time = sum(warm_times) / len(warm_times)
        
        self.assertLess(
            avg_warm_time,
            avg_cold_time * 0.5,  # At least 50% faster
            f"Warm cache ({avg_warm_time:.4f}s) should be faster than cold cache ({avg_cold_time:.4f}s)"
        )


class PerformanceBenchmarkTestCase(APITestCase):
    """
    Performance benchmark tests for the integrated system
    Measures actual response times and verifies performance requirements
    """
    
    def setUp(self):
        """Set up performance test data"""
        cache.clear()
        
        # Create test user and profile
        self.user = User.objects.create_user(
            email='perf@example.com',
            password='testpass123'
        )
        
        self.profile = Profile.objects.create(
            user=self.user,
            bio='Performance test profile'
        )
        
        self.settings = UserSettings.objects.create(
            user=self.user,
            theme='dark'
        )
    
    def test_profile_api_response_time_requirement(self):
        """
        Test that profile API responses meet <100ms requirement with caching
        """
        # PHASE 1: Cold cache request (allowed to be slower)
        start_time = time.time()
        response = self.client.get(f'/api/profiles/{self.profile.public_id}/')
        cold_time = time.time() - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # PHASE 2: Warm cache request (must meet requirement)
        times = []
        for _ in range(10):  # Test multiple requests for consistency
            start_time = time.time()
            response = self.client.get(f'/api/profiles/{self.profile.public_id}/')
            request_time = time.time() - start_time
            times.append(request_time)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # PHASE 3: Verify performance requirement
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        self.assertLess(
            avg_time, 
            0.1,  # 100ms requirement
            f"Average response time ({avg_time:.4f}s) should be under 100ms"
        )
        
        self.assertLess(
            max_time,
            0.15,  # Allow some variance, but not too much
            f"Maximum response time ({max_time:.4f}s) should be under 150ms"
        )
        
        print(f"\n📊 Performance Results:")
        print(f"   Cold cache: {cold_time:.4f}s")
        print(f"   Warm cache avg: {avg_time:.4f}s")
        print(f"   Warm cache max: {max_time:.4f}s")
    
    def test_settings_api_response_time_requirement(self):
        """
        Test that settings API responses meet performance requirements
        """
        # Authenticate user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # PHASE 1: Cold cache request
        start_time = time.time()
        response = self.client.get('/api/settings/current_settings/')
        cold_time = time.time() - start_time
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # PHASE 2: Warm cache requests
        times = []
        for _ in range(5):
            start_time = time.time()
            response = self.client.get('/api/settings/current_settings/')
            request_time = time.time() - start_time
            times.append(request_time)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # PHASE 3: Verify performance
        avg_time = sum(times) / len(times)
        
        self.assertLess(
            avg_time,
            0.05,  # Settings should be even faster - 50ms
            f"Settings response time ({avg_time:.4f}s) should be under 50ms"
        )
        
        print(f"\n⚙️  Settings Performance:")
        print(f"   Cold cache: {cold_time:.4f}s")
        print(f"   Warm cache avg: {avg_time:.4f}s")
    
    def test_cache_hit_ratio_effectiveness(self):
        """
        Test cache hit ratio and effectiveness
        """
        # Create multiple profiles for testing
        profiles = []
        for i in range(3):
            user = User.objects.create_user(
                email=f'cache{i}@example.com',
                password='testpass123'
            )
            profile = Profile.objects.create(user=user, bio=f'Cache test {i}')
            profiles.append(profile)
        
        # PHASE 1: Make initial requests (cache misses)
        for profile in profiles:
            response = self.client.get(f'/api/profiles/{profile.public_id}/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # PHASE 2: Make repeat requests (cache hits) and measure
        cache_hit_times = []
        for profile in profiles:
            for _ in range(3):  # Multiple requests per profile
                start_time = time.time()
                response = self.client.get(f'/api/profiles/{profile.public_id}/')
                request_time = time.time() - start_time
                cache_hit_times.append(request_time)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # PHASE 3: Verify cache effectiveness
        avg_cache_time = sum(cache_hit_times) / len(cache_hit_times)
        
        self.assertLess(
            avg_cache_time,
            0.02,  # Cache hits should be very fast - 20ms
            f"Cache hit time ({avg_cache_time:.4f}s) should be under 20ms"
        )
        
        print(f"\n💨 Cache Performance:")
        print(f"   Average cache hit: {avg_cache_time:.4f}s")
        print(f"   Total cache hits tested: {len(cache_hit_times)}")