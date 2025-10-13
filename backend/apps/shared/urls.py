"""
URL configuration for FamApp API endpoints.

Uses DRF DefaultRouter to automatically generate CRUD URLs.
All URLs use public_id (UUID), NOT integer id!

Ham Dog & TC wiring up the APIs! 🚀
"""

from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.shared.views import FamilyViewSet
from apps.shared.views import GroceryItemViewSet
from apps.shared.views import PetViewSet
from apps.shared.views import ScheduleEventViewSet
from apps.shared.views import TodoViewSet

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

# Todo endpoints
# This creates:
# - GET    /api/v1/todos/                 -> list
# - POST   /api/v1/todos/                 -> create
# - GET    /api/v1/todos/{public_id}/     -> retrieve
# - PATCH  /api/v1/todos/{public_id}/     -> partial_update
# - DELETE /api/v1/todos/{public_id}/     -> destroy
# - PATCH  /api/v1/todos/{public_id}/toggle/ -> toggle completion
router.register(r"todos", TodoViewSet, basename="todo")

# ScheduleEvent endpoints
# This creates:
# - GET    /api/v1/events/                -> list
# - POST   /api/v1/events/                -> create
# - GET    /api/v1/events/{public_id}/    -> retrieve
# - PATCH  /api/v1/events/{public_id}/    -> partial_update
# - DELETE /api/v1/events/{public_id}/    -> destroy
router.register(r"events", ScheduleEventViewSet, basename="event")

# GroceryItem endpoints
# This creates:
# - GET    /api/v1/groceries/             -> list
# - POST   /api/v1/groceries/             -> create
# - GET    /api/v1/groceries/{public_id}/ -> retrieve
# - PATCH  /api/v1/groceries/{public_id}/ -> partial_update
# - DELETE /api/v1/groceries/{public_id}/ -> destroy
# - PATCH  /api/v1/groceries/{public_id}/toggle/ -> toggle purchased
router.register(r"groceries", GroceryItemViewSet, basename="grocery")

# Pet endpoints
# This creates:
# - GET    /api/v1/pets/                  -> list
# - POST   /api/v1/pets/                  -> create
# - GET    /api/v1/pets/{public_id}/      -> retrieve
# - PATCH  /api/v1/pets/{public_id}/      -> partial_update
# - DELETE /api/v1/pets/{public_id}/      -> destroy
# - POST   /api/v1/pets/{public_id}/activities/ -> log activity
# - GET    /api/v1/pets/{public_id}/activities/ -> list activities
router.register(r"pets", PetViewSet, basename="pet")

urlpatterns = [
    path("", include(router.urls)),
]
