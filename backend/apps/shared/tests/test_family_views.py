"""
Test module for Family API endpoints.

Following TDD methodology (Red-Green-Refactor):
Tests for FamilyViewSet CRUD operations.

CRITICAL: All URLs use public_id (UUID), NOT integer id!

Ham Dog & TC building family collaboration APIs! 🚀
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.shared.models import Family
from apps.shared.models import FamilyMember

User = get_user_model()


@pytest.mark.django_db
class TestFamilyCreate:
    """
    Test suite for POST /api/v1/families/ (create family).

    Requirements:
    - Creates family with authenticated user as organizer
    - Returns 201 with family data
    - Validates family name (required)
    - Returns 401 if not authenticated
    """

    def test_creates_family_with_authenticated_user_as_organizer(self):
        """Test that creating a family also creates FamilyMember with organizer role."""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post("/api/v1/families/", {"name": "My Family"})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "My Family"
        assert "public_id" in response.data

        # Verify family was created
        family = Family.objects.get(public_id=response.data["public_id"])
        assert family.name == "My Family"
        assert family.created_by == user

        # Verify user is automatically added as organizer
        membership = FamilyMember.objects.get(family=family, user=user)
        assert membership.role == FamilyMember.Role.ORGANIZER

    def test_returns_201_with_family_data(self):
        """Test that successful creation returns 201 status code."""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post("/api/v1/families/", {"name": "Test Family"})

        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.data
        assert "public_id" in response.data
        assert "name" in response.data
        assert "created_at" in response.data
        assert response.data["name"] == "Test Family"

    def test_validates_family_name_is_required(self):
        """Test that name field is required."""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post("/api/v1/families/", {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    def test_validates_family_name_not_empty(self):
        """Test that name cannot be empty string."""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post("/api/v1/families/", {"name": ""})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    def test_returns_401_if_not_authenticated(self):
        """Test that unauthenticated requests return 401."""
        client = APIClient()

        response = client.post("/api/v1/families/", {"name": "Test Family"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestFamilyList:
    """
    Test suite for GET /api/v1/families/ (list families).

    Requirements:
    - Returns all families user belongs to
    - Includes member count for each family
    - Returns empty list if user has no families
    - Returns 401 if not authenticated
    """

    def test_returns_all_families_user_belongs_to(self):
        """Test that list returns only families where user is a member."""
        user = User.objects.create_user(
            email="member@example.com", password="testpass123"
        )
        other_user = User.objects.create_user(
            email="other@example.com", password="testpass123"
        )

        # Create families for user
        family1 = Family.objects.create(name="User Family 1", created_by=user)
        FamilyMember.objects.create(
            family=family1, user=user, role=FamilyMember.Role.ORGANIZER
        )

        family2 = Family.objects.create(name="User Family 2", created_by=user)
        FamilyMember.objects.create(
            family=family2, user=user, role=FamilyMember.Role.PARENT
        )

        # Create family for other user (should not appear in results)
        other_family = Family.objects.create(name="Other Family", created_by=other_user)
        FamilyMember.objects.create(
            family=other_family, user=other_user, role=FamilyMember.Role.ORGANIZER
        )

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/v1/families/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        family_names = [f["name"] for f in response.data]
        assert "User Family 1" in family_names
        assert "User Family 2" in family_names
        assert "Other Family" not in family_names

    def test_includes_member_count_for_each_family(self):
        """Test that each family includes member_count annotation."""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        other_user = User.objects.create_user(
            email="other@example.com", password="testpass123"
        )

        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )
        FamilyMember.objects.create(
            family=family, user=other_user, role=FamilyMember.Role.PARENT
        )

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/v1/families/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert "member_count" in response.data[0]
        assert response.data[0]["member_count"] == 2

    def test_returns_empty_list_if_user_has_no_families(self):
        """Test that users with no family memberships get empty list."""
        user = User.objects.create_user(
            email="loner@example.com", password="testpass123"
        )

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/v1/families/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_returns_401_if_not_authenticated(self):
        """Test that unauthenticated requests return 401."""
        client = APIClient()

        response = client.get("/api/v1/families/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestFamilyRetrieve:
    """
    Test suite for GET /api/v1/families/{public_id}/ (retrieve family).

    Requirements:
    - Returns family details with members
    - Returns 403 if user not a member
    - Includes member list with roles
    - Uses public_id (UUID) in URL, not integer id
    """

    def test_returns_family_details_with_members(self):
        """Test that retrieve returns detailed family information."""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(f"/api/v1/families/{family.public_id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["public_id"] == str(family.public_id)
        assert response.data["name"] == "Test Family"
        assert "members" in response.data

    def test_includes_member_list_with_roles(self):
        """Test that member list includes user info and roles."""
        user = User.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
        )
        member = User.objects.create_user(
            email="member@example.com",
            password="testpass123",
            first_name="Member",
            last_name="User",
        )

        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )
        FamilyMember.objects.create(
            family=family, user=member, role=FamilyMember.Role.PARENT
        )

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(f"/api/v1/families/{family.public_id}/")

        assert response.status_code == status.HTTP_200_OK
        assert "members" in response.data
        assert len(response.data["members"]) == 2

        # Check that member data includes user info
        members = response.data["members"]
        organizer = next(m for m in members if m["role"] == "organizer")
        assert organizer["user"]["email"] == "admin@example.com"
        assert organizer["user"]["first_name"] == "Admin"

    def test_returns_403_if_user_not_a_member(self):
        """Test that non-members cannot access family details."""
        owner = User.objects.create_user(
            email="owner@example.com", password="testpass123"
        )
        outsider = User.objects.create_user(
            email="outsider@example.com", password="testpass123"
        )

        family = Family.objects.create(name="Private Family", created_by=owner)
        FamilyMember.objects.create(
            family=family, user=owner, role=FamilyMember.Role.ORGANIZER
        )

        client = APIClient()
        client.force_authenticate(user=outsider)

        response = client.get(f"/api/v1/families/{family.public_id}/")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_404_if_family_not_found(self):
        """Test that invalid public_id returns 404."""
        import uuid

        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

        client = APIClient()
        client.force_authenticate(user=user)

        fake_uuid = uuid.uuid4()
        response = client.get(f"/api/v1/families/{fake_uuid}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestFamilyUpdate:
    """
    Test suite for PATCH /api/v1/families/{public_id}/ (update family).

    Requirements:
    - Updates family name (admin only)
    - Returns 403 if user not admin
    - Returns updated family data
    - Allows partial updates
    """

    def test_updates_family_name_as_organizer(self):
        """Test that organizer can update family name."""
        user = User.objects.create_user(
            email="admin@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Old Name", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            f"/api/v1/families/{family.public_id}/", {"name": "New Name"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "New Name"

        # Verify database was updated
        family.refresh_from_db()
        assert family.name == "New Name"
        assert family.updated_by == user

    def test_returns_403_if_user_not_organizer(self):
        """Test that regular members cannot update family."""
        owner = User.objects.create_user(
            email="owner@example.com", password="testpass123"
        )
        member = User.objects.create_user(
            email="member@example.com", password="testpass123"
        )

        family = Family.objects.create(name="Test Family", created_by=owner)
        FamilyMember.objects.create(
            family=family, user=owner, role=FamilyMember.Role.ORGANIZER
        )
        FamilyMember.objects.create(
            family=family, user=member, role=FamilyMember.Role.PARENT
        )

        client = APIClient()
        client.force_authenticate(user=member)

        response = client.patch(
            f"/api/v1/families/{family.public_id}/", {"name": "Hacked Name"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_403_if_user_not_a_member(self):
        """Test that outsiders cannot update family."""
        owner = User.objects.create_user(
            email="owner@example.com", password="testpass123"
        )
        outsider = User.objects.create_user(
            email="outsider@example.com", password="testpass123"
        )

        family = Family.objects.create(name="Test Family", created_by=owner)
        FamilyMember.objects.create(
            family=family, user=owner, role=FamilyMember.Role.ORGANIZER
        )

        client = APIClient()
        client.force_authenticate(user=outsider)

        response = client.patch(
            f"/api/v1/families/{family.public_id}/", {"name": "Hacked Name"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_allows_partial_updates(self):
        """Test that PATCH allows partial updates."""
        user = User.objects.create_user(
            email="admin@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Old Name", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        client = APIClient()
        client.force_authenticate(user=user)

        # Update only name, other fields should remain unchanged
        response = client.patch(
            f"/api/v1/families/{family.public_id}/", {"name": "Partial Update"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Partial Update"


@pytest.mark.django_db
class TestFamilyDelete:
    """
    Test suite for DELETE /api/v1/families/{public_id}/ (soft delete family).

    Requirements:
    - Soft deletes family (admin only)
    - Returns 403 if user not admin
    - Returns 204 No Content
    - Sets is_deleted flag
    """

    def test_soft_deletes_family_as_organizer(self):
        """Test that organizer can soft delete family."""
        user = User.objects.create_user(
            email="admin@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Doomed Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.delete(f"/api/v1/families/{family.public_id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify soft delete (is_deleted flag set)
        family.refresh_from_db()
        assert family.is_deleted is True
        assert family.deleted_at is not None

    def test_returns_403_if_user_not_organizer(self):
        """Test that regular members cannot delete family."""
        owner = User.objects.create_user(
            email="owner@example.com", password="testpass123"
        )
        member = User.objects.create_user(
            email="member@example.com", password="testpass123"
        )

        family = Family.objects.create(name="Test Family", created_by=owner)
        FamilyMember.objects.create(
            family=family, user=owner, role=FamilyMember.Role.ORGANIZER
        )
        FamilyMember.objects.create(
            family=family, user=member, role=FamilyMember.Role.PARENT
        )

        client = APIClient()
        client.force_authenticate(user=member)

        response = client.delete(f"/api/v1/families/{family.public_id}/")

        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Verify family not deleted
        family.refresh_from_db()
        assert family.is_deleted is False

    def test_returns_403_if_user_not_a_member(self):
        """Test that outsiders cannot delete family."""
        owner = User.objects.create_user(
            email="owner@example.com", password="testpass123"
        )
        outsider = User.objects.create_user(
            email="outsider@example.com", password="testpass123"
        )

        family = Family.objects.create(name="Test Family", created_by=owner)
        FamilyMember.objects.create(
            family=family, user=owner, role=FamilyMember.Role.ORGANIZER
        )

        client = APIClient()
        client.force_authenticate(user=outsider)

        response = client.delete(f"/api/v1/families/{family.public_id}/")

        assert response.status_code == status.HTTP_403_FORBIDDEN
