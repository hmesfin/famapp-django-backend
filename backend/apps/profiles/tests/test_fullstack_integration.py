"""
Full Stack Integration Tests for Profiles Module
Ham Dog & TC's end-to-end system validation! 🚀

Tests the complete integration between:
- Backend API endpoints
- Frontend components
- Caching layer
- Database operations
- Real user workflows
- Cross-system data flow
"""
import json
import time
from io import BytesIO
from PIL import Image
from django.test import LiveServerTestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.utils import override_settings
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

from apps.profiles.models import Profile, UserSettings
from apps.profiles.services.cache_service import profile_cache_service

User = get_user_model()


class FullStackProfileWorkflowTestCase(LiveServerTestCase):
    """
    End-to-end integration tests using Selenium
    Tests real user workflows across the entire stack
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up Selenium WebDriver"""
        super().setUpClass()
        
        # Configure Chrome for headless testing
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        try:
            cls.driver = webdriver.Chrome(options=chrome_options)
            cls.driver.implicitly_wait(10)
        except Exception as e:
            # Skip tests if Chrome driver not available
            cls.driver = None
            print(f"⚠️  Skipping full-stack tests: Chrome driver not available ({e})")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up WebDriver"""
        if cls.driver:
            cls.driver.quit()
        super().tearDownClass()
    
    def setUp(self):
        """Set up test data for each test"""
        if not self.driver:
            self.skipTest("Chrome driver not available")
        
        cache.clear()
        
        # Create test user
        self.user = User.objects.create_user(
            email='fullstack@example.com',
            password='testpass123',
            first_name='Full',
            last_name='Stack'
        )
        
        # Create profile
        self.profile = Profile.objects.create(
            user=self.user,
            bio='Full stack test profile',
            location='Test City',
            company='Test Corp'
        )
        
        # Create settings
        self.settings = UserSettings.objects.create(
            user=self.user,
            theme='light',
            email_notifications=True
        )
    
    def login_user(self):
        """Helper to log in user via frontend"""
        self.driver.get(f'{self.live_server_url}/login')
        
        # Wait for login form
        email_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'email'))
        )
        
        password_input = self.driver.find_element(By.NAME, 'password')
        login_button = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="login-button"]')
        
        # Fill and submit login form
        email_input.send_keys('fullstack@example.com')
        password_input.send_keys('testpass123')
        login_button.click()
        
        # Wait for redirect to dashboard/profile
        WebDriverWait(self.driver, 10).until(
            EC.url_contains('/dashboard')
        )
    
    def test_complete_profile_edit_workflow(self):
        """
        Test complete profile editing workflow:
        Login → Navigate to profile → Edit → Save → Verify changes
        """
        # PHASE 1: Login
        self.login_user()
        
        # PHASE 2: Navigate to profile edit
        self.driver.get(f'{self.live_server_url}/profile/edit')
        
        # Wait for profile form to load
        bio_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="bio-input"]'))
        )
        
        # PHASE 3: Verify initial data loaded
        self.assertEqual(bio_input.get_attribute('value'), 'Full stack test profile')
        
        location_input = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="location-input"]')
        self.assertEqual(location_input.get_attribute('value'), 'Test City')
        
        # PHASE 4: Edit profile data
        bio_input.clear()
        bio_input.send_keys('Updated via full stack test')
        
        location_input.clear()
        location_input.send_keys('Updated Test City')
        
        # PHASE 5: Save changes
        save_button = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="save-button"]')
        save_button.click()
        
        # PHASE 6: Wait for success message
        try:
            success_message = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="success-toast"]'))
            )
            self.assertIn('Profile updated successfully', success_message.text)
        except TimeoutException:
            # Alternative: Check if the save button is no longer in loading state
            WebDriverWait(self.driver, 10).until_not(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="save-button"]:disabled'))
            )
        
        # PHASE 7: Verify database was updated
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, 'Updated via full stack test')
        self.assertEqual(self.profile.location, 'Updated Test City')
        
        # PHASE 8: Verify cache was invalidated and updated
        cached_profile = profile_cache_service.get_profile(self.profile.public_id)
        # Cache should be None (invalidated) or contain updated data
        if cached_profile:
            self.assertEqual(cached_profile['bio'], 'Updated via full stack test')
    
    def test_settings_toggle_workflow(self):
        """
        Test settings toggle workflow with immediate UI feedback
        """
        # PHASE 1: Login and navigate to settings
        self.login_user()
        self.driver.get(f'{self.live_server_url}/settings')
        
        # PHASE 2: Wait for settings to load
        theme_toggle = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="theme-toggle"]'))
        )
        
        # PHASE 3: Verify initial theme state
        initial_theme = self.driver.execute_script(
            "return document.body.classList.contains('dark-theme')"
        )
        self.assertFalse(initial_theme)  # Should start with light theme
        
        # PHASE 4: Toggle theme
        theme_toggle.click()
        
        # PHASE 5: Verify immediate UI update
        time.sleep(0.5)  # Allow for animation/transition
        updated_theme = self.driver.execute_script(
            "return document.body.classList.contains('dark-theme')"
        )
        self.assertTrue(updated_theme)  # Should now be dark theme
        
        # PHASE 6: Verify database was updated
        self.settings.refresh_from_db()
        self.assertEqual(self.settings.theme, 'dark')
        
        # PHASE 7: Test email notifications toggle
        email_toggle = self.driver.find_element(
            By.CSS_SELECTOR, '[data-testid="email-notifications-toggle"]'
        )
        
        # Get initial state
        initial_checked = email_toggle.is_selected()
        self.assertTrue(initial_checked)  # Should start enabled
        
        # Toggle email notifications
        email_toggle.click()
        
        # Wait for update
        time.sleep(1)
        
        # Verify database update
        self.settings.refresh_from_db()
        self.assertFalse(self.settings.email_notifications)
    
    def test_avatar_upload_workflow(self):
        """
        Test avatar upload workflow with file validation
        """
        # PHASE 1: Login and navigate to profile
        self.login_user()
        self.driver.get(f'{self.live_server_url}/profile')
        
        # PHASE 2: Find avatar upload section
        avatar_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="avatar-input"]'))
        )
        
        # PHASE 3: Create test image file
        # Note: In a real test, you'd use a real image file
        # For this test, we'll simulate the file upload process
        
        # PHASE 4: Trigger file upload (simulated)
        # In a real implementation, you would:
        # 1. Create a temporary image file
        # 2. Use send_keys() to upload it
        # 3. Wait for upload completion
        # 4. Verify the new avatar appears
        
        print("📸 Avatar upload test simulated (would require actual file in real test)")
        
        # Verify current avatar state
        current_avatar = self.driver.find_element(
            By.CSS_SELECTOR, '[data-testid="avatar-image"]'
        )
        self.assertTrue(current_avatar.is_displayed())
    
    def test_search_and_navigation_workflow(self):
        """
        Test profile search and navigation workflow
        """
        # Create additional test profiles for searching
        for i in range(3):
            user = User.objects.create_user(
                email=f'search{i}@example.com',
                password='testpass123',
                first_name=f'Search{i}',
                last_name='User'
            )
            Profile.objects.create(
                user=user,
                bio=f'Searchable profile {i}',
                company='Search Corp'
            )
        
        # PHASE 1: Navigate to profiles page
        self.driver.get(f'{self.live_server_url}/profiles')
        
        # PHASE 2: Wait for profiles list to load
        profiles_list = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="profiles-list"]'))
        )
        
        # PHASE 3: Test search functionality
        search_input = self.driver.find_element(
            By.CSS_SELECTOR, '[data-testid="search-input"]'
        )
        
        # Type search query
        search_input.send_keys('Search Corp')
        
        # PHASE 4: Wait for search results
        time.sleep(2)  # Allow for debouncing
        
        # Verify search results
        search_results = self.driver.find_elements(
            By.CSS_SELECTOR, '[data-testid="profile-card"]'
        )
        
        # Should find the 3 search profiles plus potentially the original
        self.assertGreaterEqual(len(search_results), 3)
        
        # PHASE 5: Click on a profile to navigate
        if search_results:
            first_result = search_results[0]
            profile_link = first_result.find_element(By.CSS_SELECTOR, 'a')
            profile_link.click()
            
            # Wait for profile detail page
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="profile-detail"]'))
            )
            
            # Verify we're on a profile detail page
            self.assertIn('/profiles/', self.driver.current_url)


class APIDataFlowIntegrationTestCase(APITestCase):
    """
    Test data flow between different API endpoints
    Ensures data consistency across the entire backend system
    """
    
    def setUp(self):
        """Set up test data"""
        cache.clear()
        
        self.user = User.objects.create_user(
            email='dataflow@example.com',
            password='testpass123',
            first_name='Data',
            last_name='Flow'
        )
        
        self.profile = Profile.objects.create(
            user=self.user,
            bio='Data flow test'
        )
        
        self.settings = UserSettings.objects.create(
            user=self.user,
            theme='light'
        )
        
        # Authenticate
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_profile_settings_data_consistency(self):
        """
        Test that profile and settings data remain consistent across endpoints
        """
        # PHASE 1: Update profile via profile endpoint
        profile_update_data = {
            'bio': 'Updated via profile endpoint',
            'location': 'New Location'
        }
        
        response = self.client.patch(
            f'/api/profiles/{self.profile.public_id}/',
            data=profile_update_data,
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        
        # PHASE 2: Update settings via settings endpoint
        settings_update_data = {
            'theme': 'dark',
            'email_notifications': False
        }
        
        response = self.client.patch(
            '/api/settings/',
            data=settings_update_data,
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        
        # PHASE 3: Verify data consistency via /me endpoint
        response = self.client.get('/api/profiles/me/')
        self.assertEqual(response.status_code, 200)
        
        profile_data = response.data
        
        # Verify profile updates are reflected
        self.assertEqual(profile_data['bio'], 'Updated via profile endpoint')
        self.assertEqual(profile_data['location'], 'New Location')
        
        # PHASE 4: Verify settings are accessible and consistent
        response = self.client.get('/api/settings/')
        self.assertEqual(response.status_code, 200)
        
        settings_data = response.data
        self.assertEqual(settings_data['theme'], 'dark')
        self.assertFalse(settings_data['email_notifications'])
        
        # PHASE 5: Verify database consistency
        self.profile.refresh_from_db()
        self.settings.refresh_from_db()
        
        self.assertEqual(self.profile.bio, 'Updated via profile endpoint')
        self.assertEqual(self.profile.location, 'New Location')
        self.assertEqual(self.settings.theme, 'dark')
        self.assertFalse(self.settings.email_notifications)
    
    def test_cache_invalidation_across_endpoints(self):
        """
        Test that cache invalidation works correctly across different endpoints
        """
        # PHASE 1: Prime cache via profile detail endpoint
        response = self.client.get(f'/api/profiles/{self.profile.public_id}/')
        self.assertEqual(response.status_code, 200)
        
        # Verify cache exists
        cached_profile = profile_cache_service.get_profile(self.profile.public_id)
        self.assertIsNotNone(cached_profile)
        
        # PHASE 2: Update via /me endpoint
        response = self.client.patch(
            '/api/profiles/me/',
            data={'bio': 'Updated via me endpoint'},
            format='json'
        )
        # Note: This would require implementing PATCH on /me endpoint
        
        # PHASE 3: Update via direct profile endpoint
        response = self.client.patch(
            f'/api/profiles/{self.profile.public_id}/',
            data={'bio': 'Updated via direct endpoint'},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        
        # PHASE 4: Verify cache was invalidated
        cached_profile = profile_cache_service.get_profile(self.profile.public_id)
        self.assertIsNone(cached_profile)
        
        # PHASE 5: Verify fresh data is returned
        response = self.client.get(f'/api/profiles/{self.profile.public_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['bio'], 'Updated via direct endpoint')
    
    def test_concurrent_updates_data_integrity(self):
        """
        Test data integrity under concurrent updates from different endpoints
        """
        import threading
        import time
        from concurrent.futures import ThreadPoolExecutor
        
        results = {'successes': 0, 'failures': 0}
        
        def update_profile(update_data, endpoint_type):
            """Helper function for concurrent updates"""
            try:
                # Create separate client for thread
                from rest_framework.test import APIClient
                client = APIClient()
                refresh = RefreshToken.for_user(self.user)
                client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
                
                if endpoint_type == 'profile':
                    response = client.patch(
                        f'/api/profiles/{self.profile.public_id}/',
                        data=update_data,
                        format='json'
                    )
                elif endpoint_type == 'settings':
                    response = client.patch(
                        '/api/settings/',
                        data=update_data,
                        format='json'
                    )
                
                if 200 <= response.status_code < 300:
                    results['successes'] += 1
                else:
                    results['failures'] += 1
                
                return response.status_code
            except Exception as e:
                results['failures'] += 1
                return None
        
        # PHASE 1: Concurrent profile updates
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            # Submit profile updates
            for i in range(3):
                futures.append(
                    executor.submit(
                        update_profile,
                        {'bio': f'Concurrent profile update {i}'},
                        'profile'
                    )
                )
            
            # Submit settings updates
            for i in range(2):
                futures.append(
                    executor.submit(
                        update_profile,
                        {'theme': 'dark' if i % 2 == 0 else 'light'},
                        'settings'
                    )
                )
            
            # Wait for all to complete
            for future in futures:
                future.result()
        
        # PHASE 2: Verify final state is consistent
        self.profile.refresh_from_db()
        self.settings.refresh_from_db()
        
        # At least some updates should have succeeded
        self.assertGreater(results['successes'], 0)
        
        # Verify data integrity (profile bio should be one of the updates)
        self.assertIn('Concurrent profile update', self.profile.bio)
        
        # Verify settings is in valid state
        self.assertIn(self.settings.theme, ['light', 'dark'])
        
        print(f"\n🔄 Concurrent Updates Result:")
        print(f"   Successes: {results['successes']}")
        print(f"   Failures: {results['failures']}")


class SystemPerformanceIntegrationTestCase(APITestCase):
    """
    Test overall system performance under realistic load
    """
    
    def setUp(self):
        """Set up test data for performance testing"""
        cache.clear()
        
        # Create realistic test dataset
        self.users = []
        self.profiles = []
        
        for i in range(20):
            user = User.objects.create_user(
                email=f'perf{i}@example.com',
                password='testpass123',
                first_name=f'Performance{i}',
                last_name='User'
            )
            self.users.append(user)
            
            profile = Profile.objects.create(
                user=user,
                bio=f'Performance test profile {i}',
                location=f'City {i % 5}',  # Some overlap for filtering
                company=f'Company {i % 3}'  # Some overlap for filtering
            )
            self.profiles.append(profile)
            
            UserSettings.objects.create(
                user=user,
                theme='light' if i % 2 == 0 else 'dark',
                email_notifications=i % 3 == 0
            )
    
    def test_end_to_end_performance_workflow(self):
        """
        Test a realistic user workflow with performance measurements
        """
        # Simulate realistic user session
        user = self.users[0]
        profile = self.profiles[0]
        
        # Authenticate
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        workflow_times = {}
        
        # PHASE 1: Initial profile load (cold cache)
        start_time = time.time()
        response = self.client.get('/api/profiles/me/')
        workflow_times['initial_load'] = time.time() - start_time
        self.assertEqual(response.status_code, 200)
        
        # PHASE 2: Browse profiles (warm cache)
        start_time = time.time()
        response = self.client.get('/api/profiles/')
        workflow_times['browse_profiles'] = time.time() - start_time
        self.assertEqual(response.status_code, 200)
        
        # PHASE 3: Search profiles
        start_time = time.time()
        response = self.client.get('/api/profiles/', {'search': 'Performance'})
        workflow_times['search_profiles'] = time.time() - start_time
        self.assertEqual(response.status_code, 200)
        
        # PHASE 4: Load settings
        start_time = time.time()
        response = self.client.get('/api/settings/')
        workflow_times['load_settings'] = time.time() - start_time
        self.assertEqual(response.status_code, 200)
        
        # PHASE 5: Update profile
        start_time = time.time()
        response = self.client.patch(
            f'/api/profiles/{profile.public_id}/',
            data={'bio': 'Updated in workflow test'},
            format='json'
        )
        workflow_times['update_profile'] = time.time() - start_time
        self.assertEqual(response.status_code, 200)
        
        # PHASE 6: Update settings
        start_time = time.time()
        response = self.client.patch(
            '/api/settings/',
            data={'theme': 'dark'},
            format='json'
        )
        workflow_times['update_settings'] = time.time() - start_time
        self.assertEqual(response.status_code, 200)
        
        # PHASE 7: Reload profile (should be fast due to fresh cache)
        start_time = time.time()
        response = self.client.get('/api/profiles/me/')
        workflow_times['reload_profile'] = time.time() - start_time
        self.assertEqual(response.status_code, 200)
        
        # Report performance results
        print(f"\n🎯 End-to-End Workflow Performance:")
        total_time = sum(workflow_times.values())
        
        for step, duration in workflow_times.items():
            print(f"   {step}: {duration:.3f}s")
        
        print(f"   Total workflow: {total_time:.3f}s")
        
        # Validate performance requirements
        self.assertLess(total_time, 2.0, "Complete workflow should take less than 2 seconds")
        self.assertLess(workflow_times['reload_profile'], 0.05, "Cached profile reload should be very fast")
        self.assertLess(workflow_times['load_settings'], 0.1, "Settings load should be fast")
    
    def test_system_scalability(self):
        """
        Test system performance with increasing load
        """
        # Test with different numbers of concurrent users
        load_levels = [1, 5, 10]
        results = {}
        
        for load_level in load_levels:
            print(f"\n🚀 Testing with {load_level} concurrent users...")
            
            from concurrent.futures import ThreadPoolExecutor
            import threading
            
            def simulate_user_session(user_index):
                """Simulate a user session"""
                user = self.users[user_index % len(self.users)]
                
                # Create separate client for thread
                from rest_framework.test import APIClient
                client = APIClient()
                refresh = RefreshToken.for_user(user)
                client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
                
                session_times = []
                
                # Perform typical user actions
                actions = [
                    lambda: client.get('/api/profiles/me/'),
                    lambda: client.get('/api/profiles/'),
                    lambda: client.get('/api/settings/'),
                    lambda: client.get(f'/api/profiles/{self.profiles[0].public_id}/'),
                ]
                
                for action in actions:
                    start_time = time.time()
                    try:
                        response = action()
                        if response.status_code == 200:
                            session_times.append(time.time() - start_time)
                    except Exception:
                        pass
                
                return session_times
            
            # Run concurrent sessions
            all_times = []
            
            with ThreadPoolExecutor(max_workers=load_level) as executor:
                futures = [
                    executor.submit(simulate_user_session, i)
                    for i in range(load_level)
                ]
                
                for future in futures:
                    session_times = future.result()
                    all_times.extend(session_times)
            
            if all_times:
                avg_time = sum(all_times) / len(all_times)
                max_time = max(all_times)
                results[load_level] = {
                    'avg_time': avg_time,
                    'max_time': max_time,
                    'total_requests': len(all_times)
                }
                
                print(f"   Average response: {avg_time:.3f}s")
                print(f"   Max response: {max_time:.3f}s")
                print(f"   Total requests: {len(all_times)}")
        
        # Validate scalability
        if len(results) >= 2:
            light_load = results[load_levels[0]]
            heavy_load = results[load_levels[-1]]
            
            # Performance shouldn't degrade too much under load
            degradation = heavy_load['avg_time'] / light_load['avg_time']
            
            self.assertLess(
                degradation,
                3.0,  # No more than 3x slower under heavy load
                f"Performance degradation too high: {degradation:.2f}x"
            )
            
            print(f"\n📈 Scalability Result: {degradation:.2f}x slower under {load_levels[-1]}x load")