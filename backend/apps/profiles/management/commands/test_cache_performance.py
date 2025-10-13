"""
Management command to test caching performance in profiles app
Verifies Redis caching is working and improving performance
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.test.utils import override_settings
from apps.users.models import User
from apps.profiles.models import Profile, UserSettings
from apps.profiles.services.cache_service import ProfileCacheService
import time
import statistics


class Command(BaseCommand):
    help = 'Test cache performance for profile operations'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("Testing Profile Cache Performance")
        self.stdout.write("=" * 60)
        
        # Initialize cache service
        self.cache_service = ProfileCacheService()
        
        # Clear cache before testing
        cache.clear()
        self.stdout.write("🧹 Cache cleared")
        
        # Run tests
        self.test_profile_caching()
        self.test_settings_caching()
        self.test_cache_invalidation()
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("✅ All cache tests completed!"))
    
    def test_profile_caching(self):
        """Test profile caching performance"""
        self.stdout.write("\n📊 Test 1: Profile Caching Performance")
        self.stdout.write("-" * 40)
        
        # Get a test user
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.WARNING("No users found, skipping test"))
            return
        
        # Ensure profile exists
        profile, _ = Profile.objects.get_or_create(
            user=user,
            defaults={'bio': 'Test bio', 'location': 'Test location'}
        )
        
        # Test 1: Cold cache (database hit)
        start = time.time()
        result1 = self.cache_service.get_profile_by_user_id(user.id)
        cold_time = (time.time() - start) * 1000  # Convert to ms
        
        # Test 2: Warm cache (cache hit)
        start = time.time()
        result2 = self.cache_service.get_profile_by_user_id(user.id)
        warm_time = (time.time() - start) * 1000
        
        # Verify same data
        if result1 and result2:
            assert result1.id == result2.id, "Cache returned different data!"
        
        # Calculate improvement
        if warm_time > 0:
            improvement = cold_time / warm_time
        else:
            improvement = float('inf')
        
        self.stdout.write(f"🔹 Cold cache (DB): {cold_time:.2f}ms")
        self.stdout.write(f"🔹 Warm cache (Redis): {warm_time:.2f}ms")
        self.stdout.write(f"🚀 Performance improvement: {improvement:.1f}x faster")
        
        if improvement > 5:
            self.stdout.write(self.style.SUCCESS("✅ PASS: Significant cache performance gain"))
        else:
            self.stdout.write(self.style.WARNING("⚠️ WARNING: Cache improvement less than expected"))
    
    def test_settings_caching(self):
        """Test user settings caching"""
        self.stdout.write("\n📊 Test 2: User Settings Caching")
        self.stdout.write("-" * 40)
        
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.WARNING("No users found, skipping test"))
            return
        
        # Ensure settings exist
        settings, _ = UserSettings.objects.get_or_create(
            user=user,
            defaults={'theme': 'dark', 'language': 'en'}
        )
        
        # Clear specific cache
        cache_key = f'user_settings:{user.id}'
        cache.delete(cache_key)
        
        # Test cold vs warm cache
        times = {'cold': [], 'warm': []}
        
        for i in range(3):
            # Cold cache
            cache.delete(cache_key)
            start = time.time()
            _ = self.cache_service.get_user_settings(user.id)
            times['cold'].append((time.time() - start) * 1000)
            
            # Warm cache
            start = time.time()
            _ = self.cache_service.get_user_settings(user.id)
            times['warm'].append((time.time() - start) * 1000)
        
        avg_cold = statistics.mean(times['cold'])
        avg_warm = statistics.mean(times['warm'])
        improvement = avg_cold / avg_warm if avg_warm > 0 else float('inf')
        
        self.stdout.write(f"🔹 Avg cold cache: {avg_cold:.2f}ms")
        self.stdout.write(f"🔹 Avg warm cache: {avg_warm:.2f}ms")
        self.stdout.write(f"🚀 Performance improvement: {improvement:.1f}x faster")
        
        if improvement > 5:
            self.stdout.write(self.style.SUCCESS("✅ PASS: Settings cache working efficiently"))
        else:
            self.stdout.write(self.style.WARNING("⚠️ WARNING: Cache improvement less than expected"))
    
    def test_cache_invalidation(self):
        """Test that cache is properly invalidated on updates"""
        self.stdout.write("\n📊 Test 3: Cache Invalidation")
        self.stdout.write("-" * 40)
        
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.WARNING("No users found, skipping test"))
            return
        
        profile, _ = Profile.objects.get_or_create(
            user=user,
            defaults={'bio': 'Original bio', 'location': 'Original location'}
        )
        
        # Cache the profile
        cached_profile = self.cache_service.get_profile_by_user_id(user.id)
        original_bio = cached_profile.bio if cached_profile else ''
        
        # Update profile (should invalidate cache)
        profile.bio = 'Updated bio'
        profile.save()
        self.cache_service.invalidate_profile_by_user_id(user.id)
        
        # Get profile again (should hit database)
        updated_profile = self.cache_service.get_profile_by_user_id(user.id)
        new_bio = updated_profile.bio if updated_profile else ''
        
        # Verify update
        if new_bio == 'Updated bio' and original_bio != new_bio:
            self.stdout.write(self.style.SUCCESS("✅ PASS: Cache invalidation working correctly"))
            self.stdout.write(f"   Original: '{original_bio}'")
            self.stdout.write(f"   Updated: '{new_bio}'")
        else:
            self.stdout.write(self.style.ERROR("❌ FAIL: Cache invalidation not working"))
        
        # Restore original
        profile.bio = original_bio
        profile.save()
    
    def _measure_operation(self, operation, iterations=10):
        """Helper to measure operation performance"""
        times = []
        for _ in range(iterations):
            start = time.time()
            operation()
            times.append((time.time() - start) * 1000)
        return statistics.mean(times)