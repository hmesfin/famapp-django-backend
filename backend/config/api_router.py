from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from apps.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)

app_name = "api"
urlpatterns = [
    # Auth endpoints
    path("auth/", include("apps.users.api.auth_urls", namespace="auth")),
    # Projects endpoints - Ham Dog & TC's project management!
    path("projects/", include("apps.projects.api.urls", namespace="projects")),
    # Invitations endpoints - TDD-driven invitation system!
    path("invitations/", include("apps.invitations.api.urls", namespace="invitations")),
    # Profiles endpoints - TDD blessed user profiles & settings!
    path("", include("apps.profiles.api.urls", namespace="profiles")),
    # Router URLs
    *router.urls,
]
