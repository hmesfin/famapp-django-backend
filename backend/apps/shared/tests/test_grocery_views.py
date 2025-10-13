"""
Test module for GroceryItem ViewSet API endpoints.

Following TDD methodology (Red-Green-Refactor):
Tests for GroceryItemViewSet CRUD operations with FamilyAccessMixin.

Ham Dog & TC building grocery list APIs! 🛒
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.shared.models import Family
from apps.shared.models import FamilyMember
from apps.shared.models import GroceryItem

User = get_user_model()


@pytest.mark.django_db
class TestListGroceryItems:
    """Test suite for GET /api/v1/groceries/ - List grocery items."""

    def test_returns_items_from_user_families_only(self):
        """Test that user only sees grocery items from their families."""
        client = APIClient()

        user1 = User.objects.create_user(
            email="user1@example.com", password="testpass123"
        )
        user2 = User.objects.create_user(
            email="user2@example.com", password="testpass123"
        )

        family1 = Family.objects.create(name="Family 1", created_by=user1)
        family2 = Family.objects.create(name="Family 2", created_by=user2)

        FamilyMember.objects.create(
            family=family1, user=user1, role=FamilyMember.Role.ORGANIZER
        )
        FamilyMember.objects.create(
            family=family2, user=user2, role=FamilyMember.Role.ORGANIZER
        )

        item1 = GroceryItem.objects.create(
            family=family1,
            name="Milk",
            added_by=user1,
        )
        GroceryItem.objects.create(
            family=family2,
            name="Eggs",
            added_by=user2,
        )

        client.force_authenticate(user=user1)
        response = client.get("/api/v1/groceries/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["public_id"] == str(item1.public_id)

    def test_excludes_soft_deleted_items(self):
        """Test that soft-deleted grocery items are excluded."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        item = GroceryItem.objects.create(
            family=family,
            name="Bread",
            added_by=user,
        )

        # Soft delete
        from django.utils import timezone

        item.is_deleted = True
        item.deleted_at = timezone.now()
        item.save()

        client.force_authenticate(user=user)
        response = client.get("/api/v1/groceries/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0


@pytest.mark.django_db
class TestCreateGroceryItem:
    """Test suite for POST /api/v1/groceries/ - Create grocery item."""

    def test_creates_item_with_required_fields(self):
        """Test creating grocery item with only required fields."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        client.force_authenticate(user=user)
        response = client.post(
            "/api/v1/groceries/",
            {
                "family_public_id": str(family.public_id),
                "name": "Milk",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Milk"
        assert "public_id" in response.data

    def test_creates_item_with_all_fields(self):
        """Test creating grocery item with all optional fields."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        client.force_authenticate(user=user)
        response = client.post(
            "/api/v1/groceries/",
            {
                "family_public_id": str(family.public_id),
                "name": "Organic Milk",
                "quantity": 2,
                "unit": "gallon",
                "category": GroceryItem.Category.DAIRY,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Organic Milk"
        assert response.data["quantity"] == 2
        assert response.data["category"] == GroceryItem.Category.DAIRY

    def test_returns_400_if_name_empty(self):
        """Test that name cannot be empty."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        client.force_authenticate(user=user)
        response = client.post(
            "/api/v1/groceries/",
            {
                "family_public_id": str(family.public_id),
                "name": "",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestRetrieveGroceryItem:
    """Test suite for GET /api/v1/groceries/{public_id}/ - Retrieve item."""

    def test_returns_item_details(self):
        """Test retrieving grocery item details."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        item = GroceryItem.objects.create(
            family=family,
            name="Bread",
            added_by=user,
        )

        client.force_authenticate(user=user)
        response = client.get(f"/api/v1/groceries/{item.public_id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Bread"

    def test_returns_404_if_item_not_in_user_families(self):
        """Test that user cannot access items from other families."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        owner = User.objects.create_user(
            email="owner@example.com", password="testpass123"
        )

        family = Family.objects.create(name="Test Family", created_by=owner)
        FamilyMember.objects.create(
            family=family, user=owner, role=FamilyMember.Role.ORGANIZER
        )

        item = GroceryItem.objects.create(
            family=family,
            name="Eggs",
            added_by=owner,
        )

        client.force_authenticate(user=user)
        response = client.get(f"/api/v1/groceries/{item.public_id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestUpdateGroceryItem:
    """Test suite for PATCH /api/v1/groceries/{public_id}/ - Update item."""

    def test_updates_item_fields(self):
        """Test updating grocery item fields."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        item = GroceryItem.objects.create(
            family=family,
            name="Milk",
            added_by=user,
        )

        client.force_authenticate(user=user)
        response = client.patch(
            f"/api/v1/groceries/{item.public_id}/",
            {
                "name": "Organic Milk",
                "quantity": 3,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Organic Milk"
        assert response.data["quantity"] == 3

    def test_allows_partial_updates(self):
        """Test that partial updates work."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        item = GroceryItem.objects.create(
            family=family,
            name="Milk",
            quantity=2,
            added_by=user,
        )

        client.force_authenticate(user=user)
        response = client.patch(
            f"/api/v1/groceries/{item.public_id}/",
            {"name": "Almond Milk"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Almond Milk"
        assert response.data["quantity"] == 2  # Unchanged


@pytest.mark.django_db
class TestTogglePurchased:
    """Test suite for PATCH /api/v1/groceries/{public_id}/toggle/ - Toggle purchased."""

    def test_toggles_purchased_status(self):
        """Test toggling purchased status."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        item = GroceryItem.objects.create(
            family=family,
            name="Milk",
            is_purchased=False,
            added_by=user,
        )

        client.force_authenticate(user=user)
        response = client.patch(f"/api/v1/groceries/{item.public_id}/toggle/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_purchased"] is True

        # Toggle back
        response = client.patch(f"/api/v1/groceries/{item.public_id}/toggle/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_purchased"] is False


@pytest.mark.django_db
class TestDeleteGroceryItem:
    """Test suite for DELETE /api/v1/groceries/{public_id}/ - Soft delete item."""

    def test_soft_deletes_item(self):
        """Test that delete soft-deletes the item."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        item = GroceryItem.objects.create(
            family=family,
            name="Milk",
            added_by=user,
        )

        client.force_authenticate(user=user)
        response = client.delete(f"/api/v1/groceries/{item.public_id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify soft delete
        item.refresh_from_db()
        assert item.is_deleted is True
        assert item.deleted_at is not None

    def test_soft_deleted_item_not_in_list(self):
        """Test that soft-deleted items don't appear in list."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        item = GroceryItem.objects.create(
            family=family,
            name="Milk",
            added_by=user,
        )

        client.force_authenticate(user=user)

        # Delete the item
        response = client.delete(f"/api/v1/groceries/{item.public_id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # List should be empty
        response = client.get("/api/v1/groceries/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0
