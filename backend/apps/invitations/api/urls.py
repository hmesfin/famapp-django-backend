"""
URL configuration for invitations app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.invitations.api.views import InvitationViewSet

app_name = 'invitations'

router = DefaultRouter()
router.register('', InvitationViewSet, basename='invitation')

urlpatterns = [
    path('', include(router.urls)),
]