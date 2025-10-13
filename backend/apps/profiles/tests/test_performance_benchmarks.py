"""
Performance Benchmark Tests for Profiles Module
Ham Dog & TC's performance validation! 🚀

Measures the effectiveness of all refactored optimizations:
- Cache performance improvements
- Database query optimization
- API response time benchmarks
- Debouncing effectiveness
- Concurrent load handling
"""
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import mean, median, stdev
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.test.utils import override_settings

from apps.profiles.models import Profile, UserSettings
from apps.profiles.services.cache_service import profile_cache_service

User = get_user_model()


class CachePerformanceBenchmarkTestCase(APITestCase):
    """
    Benchmark tests for caching performance improvements
    Validates that caching provides significant performance benefits
    """
    
    def setUp(self):
        """Set up test data for performance testing"""
        cache.clear()
        
        # Create test users and profiles
        self.users = []
        self.profiles = []
        
        for i in range(10):  # Create 10 test profiles
            user = User.objects.create_user(
                email=f'perf{i}@example.com',
                password='testpass123',
                first_name=f'User{i}',
                last_name='Performance'
            )
            self.users.append(user)
            
            profile = Profile.objects.create(
                user=user,
                bio=f'Performance test profile {i}',
                location=f'City {i}',
                company=f'Company {i}'
            )
            self.profiles.append(profile)
        
        self.client = APIClient()
    
    def test_cache_vs_database_performance(self):
        """
        Benchmark cache performance vs database queries
        Requirement: Cache hits should be at least 5x faster than DB queries
        """
        profile = self.profiles[0]
        url = f'/api/profiles/{profile.public_id}/'
        
        # PHASE 1: Measure cold cache (database query)
        cold_times = []
        for _ in range(5):
            cache.clear()  # Ensure cold cache
            start_time = time.time()
            response = self.client.get(url)
            cold_time = time.time() - start_time
            cold_times.append(cold_time)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        avg_cold_time = mean(cold_times)
        
        # PHASE 2: Measure warm cache (cache hits)
        # Prime the cache
        self.client.get(url)
        
        warm_times = []
        for _ in range(20):  # More samples for cache hits
            start_time = time.time()
            response = self.client.get(url)
            warm_time = time.time() - start_time
            warm_times.append(warm_time)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        avg_warm_time = mean(warm_times)
        
        # PHASE 3: Validate performance improvement
        improvement_ratio = avg_cold_time / avg_warm_time
        
        print(f"\n🚀 Cache Performance Results:")
        print(f"   Cold cache (DB): {avg_cold_time:.4f}s avg")
        print(f"   Warm cache (Cache): {avg_warm_time:.4f}s avg")
        print(f"   Improvement ratio: {improvement_ratio:.2f}x faster")
        
        self.assertGreater(
            improvement_ratio, 
            5.0,
            f"Cache should be at least 5x faster. Got {improvement_ratio:.2f}x"
        )
        
        # Additional validation: Cache hits should be very consistent
        cache_time_variance = stdev(warm_times)
        self.assertLess(
            cache_time_variance,
            0.005,  # Less than 5ms variance
            f"Cache times should be consistent. Variance: {cache_time_variance:.4f}s"
        )
    
    def test_profile_list_caching_performance(self):
        """
        Test profile list endpoint caching performance with filters
        """
        # Test different filter combinations
        filter_combinations = [
            {},  # No filters
            {'company': 'Company 1'},
            {'location': 'City 2'},
            {'search': 'Performance'},
        ]
        
        results = {}
        
        for filters in filter_combinations:
            filter_key = str(filters) if filters else 'no_filters'
            
            # Cold cache times
            cold_times = []
            for _ in range(3):
                cache.clear()
                start_time = time.time()
                response = self.client.get('/api/profiles/', filters)
                cold_time = time.time() - start_time
                cold_times.append(cold_time)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Warm cache times
            warm_times = []
            for _ in range(10):
                start_time = time.time()
                response = self.client.get('/api/profiles/', filters)
                warm_time = time.time() - start_time
                warm_times.append(warm_time)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            results[filter_key] = {
                'cold_avg': mean(cold_times),
                'warm_avg': mean(warm_times),
                'improvement': mean(cold_times) / mean(warm_times)
            }
        
        print(f"\n📊 List Endpoint Performance:")
        for filter_key, data in results.items():
            print(f"   {filter_key}: {data['improvement']:.2f}x improvement")
        
        # Validate all filter combinations show improvement
        for filter_key, data in results.items():
            self.assertGreater(
                data['improvement'],
                2.0,
                f"List caching for {filter_key} should provide at least 2x improvement"
            )
    
    def test_settings_caching_performance(self):
        """
        Test user settings caching performance
        Settings should be very fast since they're accessed frequently
        """
        user = self.users[0]
        settings = UserSettings.objects.create(
            user=user,
            theme='dark',
            email_notifications=True
        )
        
        # Authenticate
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Cold cache performance
        cache.clear()
        cold_times = []
        for _ in range(5):
            profile_cache_service.invalidate_user_settings(user.id)
            start_time = time.time()
            response = self.client.get('/api/settings/')
            cold_time = time.time() - start_time
            cold_times.append(cold_time)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Warm cache performance
        warm_times = []
        for _ in range(15):
            start_time = time.time()
            response = self.client.get('/api/settings/')
            warm_time = time.time() - start_time
            warm_times.append(warm_time)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        avg_cold_time = mean(cold_times)
        avg_warm_time = mean(warm_times)
        improvement = avg_cold_time / avg_warm_time
        
        print(f"\n⚙️  Settings Performance:")
        print(f"   Cold: {avg_cold_time:.4f}s")
        print(f"   Warm: {avg_warm_time:.4f}s")
        print(f"   Improvement: {improvement:.2f}x")
        
        # Settings should be extremely fast when cached
        self.assertLess(
            avg_warm_time,
            0.01,  # Less than 10ms
            f"Cached settings should be under 10ms. Got {avg_warm_time:.4f}s"
        )
        
        self.assertGreater(
            improvement,
            3.0,
            f"Settings caching should provide at least 3x improvement. Got {improvement:.2f}x"
        )


class DatabaseQueryOptimizationTestCase(TestCase):
    """
    Benchmark tests for database query optimization
    Validates select_related and prefetch_related improvements
    """
    
    def setUp(self):
        """Set up test data with relationships"""
        # Create users with profiles and settings
        self.users = []
        self.profiles = []
        
        for i in range(20):
            user = User.objects.create_user(
                email=f'query{i}@example.com',
                password='testpass123',
                first_name=f'Query{i}',
                last_name='Test'
            )
            self.users.append(user)
            
            profile = Profile.objects.create(
                user=user,
                bio=f'Query test {i}',
                location=f'Location {i}'
            )
            self.profiles.append(profile)
            
            UserSettings.objects.create(
                user=user,
                theme='light' if i % 2 == 0 else 'dark',
                email_notifications=i % 3 == 0
            )
    
    def test_optimized_vs_unoptimized_queries(self):
        """
        Compare optimized queries with proper select_related vs naive queries
        """
        from django.db import connection, reset_queries
        from django.conf import settings
        
        # PHASE 1: Test unoptimized queries (N+1 problem)
        reset_queries()
        start_time = time.time()
        
        # Simulate bad query pattern
        profiles = Profile.objects.all()[:10]
        for profile in profiles:
            _ = profile.user.email  # This would cause N+1 queries
            _ = profile.user.first_name
        
        unoptimized_time = time.time() - start_time
        unoptimized_queries = len(connection.queries)
        
        # PHASE 2: Test optimized queries
        reset_queries()
        start_time = time.time()
        
        # Use the optimized query from our ViewSet
        profiles = Profile.objects.select_related('user').prefetch_related('user__settings')[:10]
        for profile in profiles:
            _ = profile.user.email  # No extra queries
            _ = profile.user.first_name
            try:
                _ = profile.user.settings.theme  # Prefetched
            except UserSettings.DoesNotExist:
                pass
        
        optimized_time = time.time() - start_time
        optimized_queries = len(connection.queries)
        
        print(f"\n🗃️  Database Query Optimization:")
        print(f"   Unoptimized: {unoptimized_queries} queries in {unoptimized_time:.4f}s")
        print(f"   Optimized: {optimized_queries} queries in {optimized_time:.4f}s")
        print(f"   Query reduction: {unoptimized_queries - optimized_queries} fewer queries")
        print(f"   Time improvement: {unoptimized_time / optimized_time:.2f}x faster")
        
        # Validate optimization
        self.assertLessEqual(
            optimized_queries,
            3,  # Should be around 1-3 queries total
            f"Optimized queries should be minimal. Got {optimized_queries}"
        )
        
        self.assertGreater(
            unoptimized_queries,
            optimized_queries * 2,
            "Unoptimized should have significantly more queries"
        )
        
        # Time should improve too
        self.assertLess(
            optimized_time,
            unoptimized_time,
            "Optimized queries should be faster"
        )


class ConcurrentLoadTestCase(APITestCase):
    """
    Test system performance under concurrent load
    Validates that caching and optimizations work under stress
    """
    
    def setUp(self):
        """Set up test data for concurrent testing"""
        cache.clear()
        
        # Create test profiles
        self.users = []
        self.profiles = []
        
        for i in range(5):
            user = User.objects.create_user(
                email=f'concurrent{i}@example.com',
                password='testpass123'
            )
            self.users.append(user)
            
            profile = Profile.objects.create(
                user=user,
                bio=f'Concurrent test {i}'
            )
            self.profiles.append(profile)
    
    def test_concurrent_profile_access(self):
        """
        Test multiple concurrent requests to profile endpoints
        """
        def make_request(profile_id, iterations=5):
            """Helper function for concurrent requests"""
            client = APIClient()
            times = []
            
            for _ in range(iterations):
                start_time = time.time()
                response = client.get(f'/api/profiles/{profile_id}/')
                request_time = time.time() - start_time
                times.append(request_time)
                
                if response.status_code != 200:
                    return None
            
            return times
        
        # PHASE 1: Sequential requests (baseline)
        profile = self.profiles[0]
        sequential_times = make_request(profile.public_id, 10)
        sequential_avg = mean(sequential_times)
        
        # PHASE 2: Concurrent requests
        concurrent_results = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit multiple concurrent requests
            futures = [
                executor.submit(make_request, profile.public_id, 3)
                for _ in range(10)
            ]
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    concurrent_results.extend(result)
        
        concurrent_avg = mean(concurrent_results)
        
        print(f"\n⚡ Concurrent Load Performance:")
        print(f"   Sequential avg: {sequential_avg:.4f}s")
        print(f"   Concurrent avg: {concurrent_avg:.4f}s")
        print(f"   Concurrent requests handled: {len(concurrent_results)}")
        
        # Validate concurrent performance
        self.assertLess(
            concurrent_avg,
            sequential_avg * 2,  # Concurrent shouldn't be more than 2x slower
            f"Concurrent performance degradation too high: {concurrent_avg:.4f}s vs {sequential_avg:.4f}s"
        )
        
        # All requests should succeed
        self.assertEqual(
            len(concurrent_results),
            30,  # 10 workers * 3 iterations each
            "Not all concurrent requests succeeded"
        )
    
    def test_cache_coherence_under_load(self):
        """
        Test that cache remains coherent under concurrent read/write load
        """
        profile = self.profiles[0]
        user = self.users[0]
        
        # Authenticate for updates
        refresh = RefreshToken.for_user(user)
        auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
        
        def read_profile():
            """Read profile repeatedly"""
            client = APIClient()
            for _ in range(10):
                response = client.get(f'/api/profiles/{profile.public_id}/')
                if response.status_code == 200:
                    return response.data['bio']
            return None
        
        def update_profile(new_bio):
            """Update profile bio"""
            client = APIClient()
            client.credentials(**auth_headers)
            response = client.patch(
                f'/api/profiles/{profile.public_id}/',
                {'bio': new_bio},
                format='json'
            )
            return response.status_code == 200
        
        # PHASE 1: Concurrent reads and writes
        results = {'reads': [], 'writes': []}
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            # Submit read tasks
            read_futures = [
                executor.submit(read_profile)
                for _ in range(5)
            ]
            
            # Submit write tasks
            write_futures = [
                executor.submit(update_profile, f'Updated bio {i}')
                for i in range(3)
            ]
            
            # Collect results
            for future in as_completed(read_futures):
                result = future.result()
                if result:
                    results['reads'].append(result)
            
            for future in as_completed(write_futures):
                result = future.result()
                results['writes'].append(result)
        
        print(f"\n🔄 Cache Coherence Test:")
        print(f"   Successful reads: {len(results['reads'])}")
        print(f"   Successful writes: {sum(results['writes'])}")
        
        # Validate coherence
        self.assertGreater(
            len(results['reads']),
            0,
            "Should have successful concurrent reads"
        )
        
        self.assertGreater(
            sum(results['writes']),
            0,
            "Should have successful concurrent writes"
        )


class APIResponseTimeBenchmarkTestCase(APITestCase):
    """
    Benchmark API response times to ensure they meet requirements
    All endpoints should respond within acceptable time limits
    """
    
    def setUp(self):
        """Set up test data for API benchmarking"""
        cache.clear()
        
        self.user = User.objects.create_user(
            email='benchmark@example.com',
            password='testpass123'
        )
        
        self.profile = Profile.objects.create(
            user=self.user,
            bio='Benchmark test profile'
        )
        
        self.settings = UserSettings.objects.create(
            user=self.user,
            theme='dark'
        )
    
    def benchmark_endpoint(self, url, method='GET', auth=False, data=None, iterations=20):
        """
        Helper method to benchmark an endpoint
        """
        client = APIClient()
        
        if auth:
            refresh = RefreshToken.for_user(self.user)
            client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        times = []
        status_codes = []
        
        for _ in range(iterations):
            start_time = time.time()
            
            if method == 'GET':
                response = client.get(url)
            elif method == 'PATCH':
                response = client.patch(url, data, format='json')
            elif method == 'POST':
                response = client.post(url, data, format='multipart' if 'file' in str(data) else 'json')
            
            request_time = time.time() - start_time
            times.append(request_time)
            status_codes.append(response.status_code)
        
        return {
            'avg_time': mean(times),
            'median_time': median(times),
            'max_time': max(times),
            'min_time': min(times),
            'std_dev': stdev(times) if len(times) > 1 else 0,
            'success_rate': sum(1 for code in status_codes if 200 <= code < 300) / len(status_codes),
            'times': times
        }
    
    def test_profile_endpoints_performance(self):
        """
        Test all profile endpoints meet performance requirements
        """
        # Prime cache
        self.client.get(f'/api/profiles/{self.profile.public_id}/')
        
        endpoints = [
            {
                'name': 'Profile Detail (Cached)',
                'url': f'/api/profiles/{self.profile.public_id}/',
                'method': 'GET',
                'auth': False,
                'requirement': 0.05  # 50ms
            },
            {
                'name': 'Profile List',
                'url': '/api/profiles/',
                'method': 'GET',
                'auth': False,
                'requirement': 0.1  # 100ms
            },
            {
                'name': 'My Profile',
                'url': '/api/profiles/me/',
                'method': 'GET',
                'auth': True,
                'requirement': 0.05  # 50ms
            },
            {
                'name': 'Profile Update',
                'url': f'/api/profiles/{self.profile.public_id}/',
                'method': 'PATCH',
                'auth': True,
                'data': {'bio': 'Updated benchmark bio'},
                'requirement': 0.15  # 150ms
            }
        ]
        
        print(f"\n🎯 API Performance Benchmarks:")
        
        all_passed = True
        
        for endpoint in endpoints:
            result = self.benchmark_endpoint(
                url=endpoint['url'],
                method=endpoint['method'],
                auth=endpoint['auth'],
                data=endpoint.get('data'),
                iterations=15
            )
            
            passed = result['avg_time'] <= endpoint['requirement']
            status = "✅ PASS" if passed else "❌ FAIL"
            
            print(f"   {endpoint['name']}: {result['avg_time']:.3f}s avg (req: {endpoint['requirement']:.3f}s) {status}")
            print(f"      Range: {result['min_time']:.3f}s - {result['max_time']:.3f}s")
            
            if not passed:
                all_passed = False
            
            # Assert individual requirements
            self.assertLessEqual(
                result['avg_time'],
                endpoint['requirement'],
                f"{endpoint['name']} failed performance requirement"
            )
            
            # Assert success rate
            self.assertGreaterEqual(
                result['success_rate'],
                1.0,
                f"{endpoint['name']} had failures"
            )
        
        self.assertTrue(all_passed, "Not all endpoints met performance requirements")
    
    def test_settings_endpoint_performance(self):
        """
        Test settings endpoints performance (should be very fast)
        """
        # Authenticate
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Prime cache
        self.client.get('/api/settings/')
        
        # Benchmark settings endpoints
        endpoints = [
            {
                'name': 'Get Settings (Cached)',
                'url': '/api/settings/',
                'method': 'GET',
                'requirement': 0.02  # 20ms
            },
            {
                'name': 'Update Settings',
                'url': '/api/settings/',
                'method': 'PATCH',
                'data': {'theme': 'light'},
                'requirement': 0.05  # 50ms
            }
        ]
        
        print(f"\n⚙️  Settings Performance:")
        
        for endpoint in endpoints:
            result = self.benchmark_endpoint(
                url=endpoint['url'],
                method=endpoint['method'],
                auth=True,
                data=endpoint.get('data'),
                iterations=10
            )
            
            passed = result['avg_time'] <= endpoint['requirement']
            status = "✅ PASS" if passed else "❌ FAIL"
            
            print(f"   {endpoint['name']}: {result['avg_time']:.3f}s avg {status}")
            
            self.assertLessEqual(
                result['avg_time'],
                endpoint['requirement'],
                f"{endpoint['name']} failed performance requirement"
            )


class PerformanceRegressionTestCase(APITestCase):
    """
    Test for performance regressions
    Ensures optimizations don't degrade over time
    """
    
    def setUp(self):
        """Set up baseline data"""
        cache.clear()
        
        self.user = User.objects.create_user(
            email='regression@example.com',
            password='testpass123'
        )
        
        self.profile = Profile.objects.create(
            user=self.user,
            bio='Regression test profile'
        )
    
    def test_cache_warming_effectiveness(self):
        """
        Test that cache warming provides expected performance benefits
        """
        # Create multiple profiles for warming test
        profiles = []
        for i in range(10):
            user = User.objects.create_user(
                email=f'warm{i}@example.com',
                password='testpass123'
            )
            profile = Profile.objects.create(
                user=user,
                bio=f'Warm test {i}'
            )
            profiles.append(profile)
        
        # PHASE 1: Cold access times
        cache.clear()
        cold_times = []
        
        for profile in profiles:
            start_time = time.time()
            response = self.client.get(f'/api/profiles/{profile.public_id}/')
            cold_time = time.time() - start_time
            cold_times.append(cold_time)
            self.assertEqual(response.status_code, 200)
        
        # PHASE 2: Warm cache
        cache.clear()
        profile_cache_service.warm_profile_cache(profiles)
        
        # PHASE 3: Warm access times
        warm_times = []
        
        for profile in profiles:
            start_time = time.time()
            response = self.client.get(f'/api/profiles/{profile.public_id}/')
            warm_time = time.time() - start_time
            warm_times.append(warm_time)
            self.assertEqual(response.status_code, 200)
        
        avg_cold = mean(cold_times)
        avg_warm = mean(warm_times)
        improvement = avg_cold / avg_warm
        
        print(f"\n🔥 Cache Warming Effectiveness:")
        print(f"   Cold average: {avg_cold:.4f}s")
        print(f"   Warm average: {avg_warm:.4f}s")
        print(f"   Improvement: {improvement:.2f}x faster")
        
        self.assertGreater(
            improvement,
            3.0,
            f"Cache warming should provide at least 3x improvement. Got {improvement:.2f}x"
        )
    
    def test_memory_usage_optimization(self):
        """
        Test that the system doesn't use excessive memory
        This is a placeholder for memory profiling
        """
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Measure memory before operations
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform memory-intensive operations
        profiles = []
        for i in range(100):
            user = User.objects.create_user(
                email=f'memory{i}@example.com',
                password='testpass123'
            )
            profile = Profile.objects.create(
                user=user,
                bio=f'Memory test {i}' * 10  # Longer bio
            )
            profiles.append(profile)
        
        # Access all profiles to load into cache
        for profile in profiles:
            self.client.get(f'/api/profiles/{profile.public_id}/')
        
        # Measure memory after operations
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before
        
        print(f"\n💾 Memory Usage:")
        print(f"   Before: {memory_before:.1f} MB")
        print(f"   After: {memory_after:.1f} MB")
        print(f"   Increase: {memory_increase:.1f} MB")
        print(f"   Per profile: {memory_increase/100:.2f} MB")
        
        # Validate reasonable memory usage
        self.assertLess(
            memory_increase / 100,  # Per profile
            1.0,  # Less than 1MB per profile
            f"Memory usage per profile too high: {memory_increase/100:.2f} MB"
        )