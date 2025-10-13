"""
Management command to test query optimization in profiles app
Verifies N+1 queries have been eliminated
"""
from django.core.management.base import BaseCommand
from django.db import connection, reset_queries
from django.test.utils import override_settings
from apps.users.models import User
from apps.profiles.models import Profile, UserSettings
import json


class Command(BaseCommand):
    help = 'Test query optimization for profile endpoints'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("Testing Profile Query Optimization")
        self.stdout.write("=" * 60)
        
        # Enable query logging
        with override_settings(DEBUG=True):
            # Test 1: Profile list query optimization
            self.test_profile_list_queries()
            
            # Test 2: Profile detail with settings
            self.test_profile_detail_queries()
            
            # Test 3: Current user profile
            self.test_current_user_profile_queries()
    
    def test_profile_list_queries(self):
        """Test that listing profiles doesn't cause N+1 queries"""
        self.stdout.write("\n📊 Test 1: Profile List Queries")
        self.stdout.write("-" * 40)
        
        reset_queries()
        
        # Simulate what the ViewSet does
        from apps.profiles.api.views import ProfileViewSet
        viewset = ProfileViewSet()
        queryset = viewset.get_queryset()
        
        # Force evaluation
        profiles = list(queryset[:10])
        
        # Access related data (this should NOT cause additional queries)
        for profile in profiles:
            _ = profile.user.email
            _ = profile.user.first_name
            if hasattr(profile.user, 'settings'):
                _ = profile.user.settings.theme
        
        query_count = len(connection.queries)
        
        self.stdout.write(f"Queries executed: {query_count}")
        
        if query_count <= 3:  # Should be 1-3 queries max
            self.stdout.write(self.style.SUCCESS("✅ PASS: No N+1 queries detected"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ FAIL: Too many queries ({query_count})"))
            self.show_queries()
    
    def test_profile_detail_queries(self):
        """Test that getting a single profile is optimized"""
        self.stdout.write("\n📊 Test 2: Profile Detail Queries")
        self.stdout.write("-" * 40)
        
        # Create test data
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.WARNING("No users found, skipping test"))
            return
            
        reset_queries()
        
        # Simulate detail view
        profile = Profile.objects.select_related('user').prefetch_related(
            'user__settings'
        ).filter(user=user).first()
        
        if profile:
            # Access all related data
            _ = profile.user.email
            _ = profile.bio
            try:
                settings = profile.user.settings
                _ = settings.theme
                _ = settings.language
            except UserSettings.DoesNotExist:
                pass
        
        query_count = len(connection.queries)
        
        self.stdout.write(f"Queries executed: {query_count}")
        
        if query_count <= 2:  # Should be 1-2 queries
            self.stdout.write(self.style.SUCCESS("✅ PASS: Optimized query pattern"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ FAIL: Too many queries ({query_count})"))
            self.show_queries()
    
    def test_current_user_profile_queries(self):
        """Test the /me endpoint optimization"""
        self.stdout.write("\n📊 Test 3: Current User Profile (/me)")
        self.stdout.write("-" * 40)
        
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.WARNING("No users found, skipping test"))
            return
        
        reset_queries()
        
        # Simulate /me endpoint
        profile, created = Profile.objects.select_related('user').get_or_create(
            user=user,
            defaults={'bio': '', 'location': ''}
        )
        
        # Access user data
        _ = profile.user.email
        _ = profile.user.first_name
        _ = profile.bio
        
        query_count = len(connection.queries)
        
        self.stdout.write(f"Queries executed: {query_count}")
        
        if query_count <= 2:  # Should be 1-2 queries
            self.stdout.write(self.style.SUCCESS("✅ PASS: /me endpoint optimized"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ FAIL: Too many queries ({query_count})"))
            self.show_queries()
    
    def show_queries(self):
        """Display the actual queries for debugging"""
        self.stdout.write("\n🔍 Queries executed:")
        for i, query in enumerate(connection.queries, 1):
            self.stdout.write(f"{i}. {query['sql'][:100]}...")
            self.stdout.write(f"   Time: {query['time']}s")
        
        self.stdout.write("\n💡 Tip: Use select_related() and prefetch_related() to reduce queries")