"""
Profile caching service using Redis
Ham Dog & TC's performance optimization!

Implements caching for frequently accessed profiles and user settings.
"""
import json
from typing import Optional, List, Dict, Any
from django.core.cache import cache
from django.conf import settings
from apps.profiles.models import Profile, UserSettings


class ProfileCacheService:
    """Service for caching profile and settings data"""
    
    # Cache key patterns
    PROFILE_KEY = "profile:{public_id}"
    USER_SETTINGS_KEY = "user_settings:{user_id}"
    PROFILE_LIST_KEY = "profile_list:{filters_hash}"
    
    # Cache timeouts (in seconds)
    PROFILE_TIMEOUT = 300  # 5 minutes
    SETTINGS_TIMEOUT = 900  # 15 minutes (settings change less frequently)
    LIST_TIMEOUT = 60  # 1 minute for lists
    
    def __init__(self):
        self.cache = cache
    
    def _make_profile_key(self, public_id: str) -> str:
        """Generate cache key for profile"""
        return self.PROFILE_KEY.format(public_id=public_id)
    
    def _make_settings_key(self, user_id: int) -> str:
        """Generate cache key for user settings"""
        return self.USER_SETTINGS_KEY.format(user_id=user_id)
    
    def _make_list_key(self, filters_hash: str) -> str:
        """Generate cache key for profile list"""
        return self.PROFILE_LIST_KEY.format(filters_hash=filters_hash)
    
    def _serialize_profile(self, profile: Profile) -> Dict[str, Any]:
        """Serialize profile for caching"""
        return {
            'public_id': profile.public_id,
            'user_email': profile.user.email,
            'user_full_name': profile.user.get_full_name(),
            'user_first_name': profile.user.first_name,
            'user_last_name': profile.user.last_name,
            'bio': profile.bio,
            'location': profile.location,
            'website': profile.website,
            'company': profile.company,
            'avatar_url': profile.avatar_url,
            'created_at': profile.created_at.isoformat(),
            'updated_at': profile.updated_at.isoformat(),
            # Cache the user ID for settings lookups
            'user_id': profile.user.id,
        }
    
    def _serialize_settings(self, settings: UserSettings) -> Dict[str, Any]:
        """Serialize user settings for caching"""
        return {
            'public_id': settings.public_id,
            'theme': settings.theme,
            'language': settings.language,
            'timezone': settings.timezone,
            'email_notifications': settings.email_notifications,
            'push_notifications': settings.push_notifications,
            'profile_visibility': settings.profile_visibility,
            'show_email': settings.show_email,
            'show_activity': settings.show_activity,
            'metadata': settings.metadata,
            'created_at': settings.created_at.isoformat(),
            'updated_at': settings.updated_at.isoformat(),
        }
    
    # Profile caching methods
    def get_profile(self, public_id: str) -> Optional[Dict[str, Any]]:
        """Get profile from cache"""
        key = self._make_profile_key(public_id)
        return self.cache.get(key)
    
    def set_profile(self, profile: Profile) -> None:
        """Cache a profile"""
        key = self._make_profile_key(profile.public_id)
        data = self._serialize_profile(profile)
        self.cache.set(key, data, timeout=self.PROFILE_TIMEOUT)
    
    def invalidate_profile(self, public_id: str) -> None:
        """Remove profile from cache"""
        key = self._make_profile_key(public_id)
        self.cache.delete(key)
    
    def get_profile_by_user_id(self, user_id: int) -> Optional[Profile]:
        """Get profile by user_id with caching"""
        # Try to get profile from database
        try:
            profile = Profile.objects.select_related('user').get(user_id=user_id)
            # Check if cached
            cached = self.get_profile(profile.public_id)
            if not cached:
                # Cache miss - store it
                self.set_profile(profile)
            return profile
        except Profile.DoesNotExist:
            return None
    
    def invalidate_profile_by_user_id(self, user_id: int) -> None:
        """Invalidate profile cache by user_id"""
        try:
            profile = Profile.objects.get(user_id=user_id)
            self.invalidate_profile(profile.public_id)
        except Profile.DoesNotExist:
            pass
    
    # User settings caching methods
    def get_user_settings(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user settings from cache"""
        key = self._make_settings_key(user_id)
        return self.cache.get(key)
    
    def set_user_settings(self, settings: UserSettings) -> None:
        """Cache user settings"""
        key = self._make_settings_key(settings.user_id)
        data = self._serialize_settings(settings)
        self.cache.set(key, data, timeout=self.SETTINGS_TIMEOUT)
    
    def invalidate_user_settings(self, user_id: int) -> None:
        """Remove user settings from cache"""
        key = self._make_settings_key(user_id)
        self.cache.delete(key)
    
    # Profile list caching methods
    def get_profile_list(self, filters_hash: str) -> Optional[List[Dict[str, Any]]]:
        """Get profile list from cache"""
        key = self._make_list_key(filters_hash)
        return self.cache.get(key)
    
    def set_profile_list(self, filters_hash: str, profiles: List[Profile]) -> None:
        """Cache profile list"""
        key = self._make_list_key(filters_hash)
        data = [self._serialize_profile(profile) for profile in profiles]
        self.cache.set(key, data, timeout=self.LIST_TIMEOUT)
    
    def invalidate_profile_lists(self) -> None:
        """Invalidate all profile lists (called when any profile changes)"""
        # Use pattern-based deletion if available, otherwise this is a no-op
        # In production, you might want to track list keys separately
        pass
    
    # Batch operations
    def warm_profile_cache(self, profiles: List[Profile]) -> None:
        """Warm cache with multiple profiles"""
        for profile in profiles:
            self.set_profile(profile)
    
    def invalidate_user_cache(self, user_id: int, public_id: str) -> None:
        """Invalidate all cache entries for a user"""
        self.invalidate_profile(public_id)
        self.invalidate_user_settings(user_id)
        self.invalidate_profile_lists()


# Global instance
profile_cache_service = ProfileCacheService()