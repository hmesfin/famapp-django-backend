from apps.users.models import User


def test_user_get_absolute_url(user: User):
    """User absolute URL uses api:user-detail with public_id."""
    assert user.get_absolute_url() == f"/api/users/{user.public_id}/"
