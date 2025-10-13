from apps.users.api.views import UserViewSet
from django.conf import settings
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)

app_name = "api"
urlpatterns = [
    # Auth endpoints
    path("auth/", include("apps.users.api.auth_urls", namespace="auth")),
    # Router URLs
    *router.urls,
]
