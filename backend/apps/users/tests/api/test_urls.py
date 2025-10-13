from django.urls import resolve
from django.urls import reverse

from apps.users.models import User


def test_user_detail(user: User):
    """User detail URL uses public_id (UUID), not integer pk."""
    assert (
        reverse("api:user-detail", kwargs={"public_id": user.public_id})
        == f"/api/users/{user.public_id}/"
    )
    assert resolve(f"/api/users/{user.public_id}/").view_name == "api:user-detail"


def test_user_list():
    assert reverse("api:user-list") == "/api/users/"
    assert resolve("/api/users/").view_name == "api:user-list"


def test_user_me():
    assert reverse("api:user-me") == "/api/users/me/"
    assert resolve("/api/users/me/").view_name == "api:user-me"
