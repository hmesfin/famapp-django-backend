"""
URL configuration for profiles API
Ham Dog & TC's RESTful routes!
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.profiles.api.views import ProfileViewSet, UserSettingsViewSet

app_name = 'profiles'

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'settings', UserSettingsViewSet, basename='settings')

urlpatterns = [
    path('', include(router.urls)),
]