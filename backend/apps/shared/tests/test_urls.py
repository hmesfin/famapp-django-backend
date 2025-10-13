"""
Test URL routing for FamApp API endpoints.

Tests URL resolution, routing patterns, and public_id usage.
Ham Dog & TC ensuring routes are rock solid! 🚀
"""

import pytest
from django.urls import resolve
from django.urls import reverse


@pytest.mark.django_db
class TestFamilyURLs:
  """Test Family ViewSet URL routing"""

  def test_family_list_url_resolves(self):
    """Family list URL resolves to correct view"""
    url = reverse("api:family-list")
    assert url == "/api/v1/families/"
    resolver = resolve(url)
    assert resolver.view_name == "api:family-list"

  def test_family_detail_url_uses_public_id(self, family):
    """Family detail URL uses public_id (UUID), not integer id"""
    url = reverse("api:family-detail", kwargs={"public_id": family.public_id})
    assert str(family.public_id) in url
    assert f"/api/v1/families/{family.public_id}/" == url
    # Ensure integer id does NOT work
    assert str(family.id) not in url

  def test_family_members_custom_action_url(self, family):
    """Family members custom action URL resolves correctly"""
    url = reverse("api:family-members", kwargs={"public_id": family.public_id})
    assert url == f"/api/v1/families/{family.public_id}/members/"


@pytest.mark.django_db
class TestTodoURLs:
  """Test Todo ViewSet URL routing"""

  def test_todo_list_url_resolves(self):
    """Todo list URL resolves correctly"""
    url = reverse("api:todo-list")
    assert url == "/api/v1/todos/"

  def test_todo_detail_url_uses_public_id(self, todo):
    """Todo detail URL uses public_id (UUID)"""
    url = reverse("api:todo-detail", kwargs={"public_id": todo.public_id})
    assert str(todo.public_id) in url
    assert f"/api/v1/todos/{todo.public_id}/" == url

  def test_todo_toggle_custom_action_url(self, todo):
    """Todo toggle completion action URL resolves correctly"""
    url = reverse("api:todo-toggle", kwargs={"public_id": todo.public_id})
    assert url == f"/api/v1/todos/{todo.public_id}/toggle/"


@pytest.mark.django_db
class TestScheduleEventURLs:
  """Test ScheduleEvent ViewSet URL routing"""

  def test_event_list_url_resolves(self):
    """ScheduleEvent list URL resolves correctly"""
    url = reverse("api:event-list")
    assert url == "/api/v1/events/"

  def test_event_detail_url_uses_public_id(self, schedule_event):
    """ScheduleEvent detail URL uses public_id (UUID)"""
    url = reverse("api:event-detail", kwargs={"public_id": schedule_event.public_id})
    assert str(schedule_event.public_id) in url
    assert f"/api/v1/events/{schedule_event.public_id}/" == url


@pytest.mark.django_db
class TestGroceryItemURLs:
  """Test GroceryItem ViewSet URL routing"""

  def test_grocery_list_url_resolves(self):
    """GroceryItem list URL resolves correctly"""
    url = reverse("api:grocery-list")
    assert url == "/api/v1/groceries/"

  def test_grocery_detail_url_uses_public_id(self, grocery_item):
    """GroceryItem detail URL uses public_id (UUID)"""
    url = reverse("api:grocery-detail", kwargs={"public_id": grocery_item.public_id})
    assert str(grocery_item.public_id) in url
    assert f"/api/v1/groceries/{grocery_item.public_id}/" == url

  def test_grocery_toggle_custom_action_url(self, grocery_item):
    """GroceryItem toggle purchased action URL resolves correctly"""
    url = reverse("api:grocery-toggle", kwargs={"public_id": grocery_item.public_id})
    assert url == f"/api/v1/groceries/{grocery_item.public_id}/toggle/"


@pytest.mark.django_db
class TestPetURLs:
  """Test Pet ViewSet URL routing"""

  def test_pet_list_url_resolves(self):
    """Pet list URL resolves correctly"""
    url = reverse("api:pet-list")
    assert url == "/api/v1/pets/"

  def test_pet_detail_url_uses_public_id(self, pet):
    """Pet detail URL uses public_id (UUID)"""
    url = reverse("api:pet-detail", kwargs={"public_id": pet.public_id})
    assert str(pet.public_id) in url
    assert f"/api/v1/pets/{pet.public_id}/" == url

  def test_pet_activities_custom_action_url(self, pet):
    """Pet activities custom action URL resolves correctly"""
    url = reverse("api:pet-activities", kwargs={"public_id": pet.public_id})
    assert url == f"/api/v1/pets/{pet.public_id}/activities/"


@pytest.mark.django_db
class TestURLNamespacing:
  """Test URL namespacing and router configuration"""

  def test_all_famapp_urls_use_api_namespace(self):
    """All FamApp URLs are properly namespaced under 'api'"""
    # All ViewSet URLs should use 'api:' namespace
    namespaced_urls = [
      "api:family-list",
      "api:todo-list",
      "api:event-list",
      "api:grocery-list",
      "api:pet-list",
    ]
    for url_name in namespaced_urls:
      url = reverse(url_name)
      assert url.startswith("/api/v1/"), f"{url_name} should start with /api/v1/"

  def test_url_router_uses_default_router_format(self):
    """DRF DefaultRouter format is used (trailing slashes)"""
    # DefaultRouter adds trailing slashes by default
    url = reverse("api:family-list")
    assert url.endswith("/"), "DefaultRouter URLs should have trailing slashes"


@pytest.mark.django_db
class TestURLSecurity:
  """Test URL security patterns"""

  def test_urls_do_not_expose_integer_ids(self, family, todo, pet):
    """URLs never expose integer database IDs"""
    # Check family URL
    family_url = reverse("api:family-detail", kwargs={"public_id": family.public_id})
    assert str(family.id) not in family_url
    assert str(family.public_id) in family_url

    # Check todo URL
    todo_url = reverse("api:todo-detail", kwargs={"public_id": todo.public_id})
    assert str(todo.id) not in todo_url
    assert str(todo.public_id) in todo_url

    # Check pet URL
    pet_url = reverse("api:pet-detail", kwargs={"public_id": pet.public_id})
    assert str(pet.id) not in pet_url
    assert str(pet.public_id) in pet_url

  def test_all_viewset_urls_require_authentication(self):
    """All FamApp ViewSet URLs are protected by authentication"""
    # This is tested indirectly via ViewSet tests
    # Just verify settings are configured correctly
    from django.conf import settings

    assert "rest_framework_simplejwt.authentication.JWTAuthentication" in str(
      settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"],
    )
    assert "rest_framework.permissions.IsAuthenticated" in str(
      settings.REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"],
    )
