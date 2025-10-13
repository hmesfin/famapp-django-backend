"""
URL configuration for FamApp API endpoints.

Uses DRF DefaultRouter to automatically generate CRUD URLs.
All URLs use public_id (UUID), NOT integer id!

Ham Dog & TC wiring up the APIs! 🚀
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.shared.views import FamilyViewSet

# Create DRF router
router = DefaultRouter()

# Register ViewSets
# This creates:
# - GET    /api/v1/families/              -> list
# - POST   /api/v1/families/              -> create
# - GET    /api/v1/families/{public_id}/  -> retrieve
# - PUT    /api/v1/families/{public_id}/  -> update
# - PATCH  /api/v1/families/{public_id}/  -> partial_update
# - DELETE /api/v1/families/{public_id}/  -> destroy
router.register(r"families", FamilyViewSet, basename="family")

urlpatterns = [
    path("", include(router.urls)),
]
