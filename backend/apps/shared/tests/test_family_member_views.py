"""
Test module for Family Member API endpoints.

Following TDD methodology (Red-Green-Refactor):
Tests for Family Member management (invite, list, update role, remove).

CRITICAL: All URLs use public_id (UUID), NOT integer id!

Ham Dog & TC building family member management! 🚀
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.shared.models import Family, FamilyMember

User = get_user_model()


@pytest.mark.django_db
class TestInviteMember:
    """
    Test suite for POST /api/v1/families/{public_id}/members/ (invite member).

    Requirements:
    - Invites user by email (admin only)
    - Creates FamilyMember with specified role (default: PARENT)
    - Returns 400 if user already a member
    - Returns 404 if user doesn't exist
    - Returns 403 if not admin
    """

    def test_invites_user_by_email_as_organizer(self):
        """Test that organizer can invite a user by email."""
        admin = User.objects.create_user(
            email="admin@example.com", password="testpass123"
        )
        invitee = User.objects.create_user(
            email="invitee@example.com", password="testpass123"
        )

        family = Family.objects.create(name="Test Family", created_by=admin)
        FamilyMember.objects.create(
            family=family, user=admin, role=FamilyMember.Role.ORGANIZER
        )

        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.post(
            f"/api/v1/families/{family.public_id}/members/",
            {"email": "invitee@example.com", "role": "parent"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert "user" in response.data
        assert response.data["user"]["email"] == "invitee@example.com"
        assert response.data["role"] == "parent"

        # Verify membership was created
        membership = FamilyMember.objects.get(family=family, user=invitee)
        assert membership.role == FamilyMember.Role.PARENT

    def test_creates_member_with_default_role_parent(self):
        """Test that role defaults to PARENT if not specified."""
        admin = User.objects.create_user(
            email="admin@example.com", password="testpass123"
        )
        invitee = User.objects.create_user(
            email="invitee@example.com", password="testpass123"
        )

        family = Family.objects.create(name="Test Family", created_by=admin)
        FamilyMember.objects.create(
            family=family, user=admin, role=FamilyMember.Role.ORGANIZER
        )

        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.post(
            f"/api/v1/families/{family.public_id}/members/",
            {"email": "invitee@example.com"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["role"] == "parent"

    def test_can_invite_with_organizer_role(self):
        """Test that organizer can invite another organizer."""
        admin = User.objects.create_user(
            email="admin@example.com", password="testpass123"
        )
        invitee = User.objects.create_user(
            email="invitee@example.com", password="testpass123"
        )

        family = Family.objects.create(name="Test Family", created_by=admin)
        FamilyMember.objects.create(
            family=family, user=admin, role=FamilyMember.Role.ORGANIZER
        )

        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.post(
            f"/api/v1/families/{family.public_id}/members/",
            {"email": "invitee@example.com", "role": "organizer"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["role"] == "organizer"

    def test_returns_400_if_user_already_a_member(self):
        """Test that inviting existing member returns 400."""
        admin = User.objects.create_user(
            email="admin@example.com", password="testpass123"
        )
        existing_member = User.objects.create_user(
            email="existing@example.com", password="testpass123"
        )

        family = Family.objects.create(name="Test Family", created_by=admin)
        FamilyMember.objects.create(
            family=family, user=admin, role=FamilyMember.Role.ORGANIZER
        )
        FamilyMember.objects.create(
            family=family, user=existing_member, role=FamilyMember.Role.PARENT
        )

        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.post(
            f"/api/v1/families/{family.public_id}/members/",
            {"email": "existing@example.com"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already a member" in str(response.data).lower()

    def test_returns_400_if_user_not_found(self):
        """Test that inviting non-existent user returns 400."""
        admin = User.objects.create_user(
            email="admin@example.com", password="testpass123"
        )

        family = Family.objects.create(name="Test Family", created_by=admin)
        FamilyMember.objects.create(
            family=family, user=admin, role=FamilyMember.Role.ORGANIZER
        )

        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.post(
            f"/api/v1/families/{family.public_id}/members/",
            {"email": "nonexistent@example.com"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_returns_403_if_user_not_organizer(self):
        """Test that regular members cannot invite."""
        owner = User.objects.create_user(
            email="owner@example.com", password="testpass123"
        )
        member = User.objects.create_user(
            email="member@example.com", password="testpass123"
        )
        invitee = User.objects.create_user(
            email="invitee@example.com", password="testpass123"
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

        response = client.post(
            f"/api/v1/families/{family.public_id}/members/",
            {"email": "invitee@example.com"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestListMembers:
    """
    Test suite for GET /api/v1/families/{public_id}/members/ (list members).

    Requirements:
    - Returns all family members (any member can view)
    - Includes user info (name, email) and role
    - Returns 403 if user not a member
    """

    def test_returns_all_family_members(self):
        """Test that members list includes all family members."""
        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        other1 = User.objects.create_user(
            email="other1@example.com",
            password="testpass123",
            first_name="Other",
            last_name="One",
        )
        other2 = User.objects.create_user(
            email="other2@example.com",
            password="testpass123",
            first_name="Other",
            last_name="Two",
        )

        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )
        FamilyMember.objects.create(
            family=family, user=other1, role=FamilyMember.Role.PARENT
        )
        FamilyMember.objects.create(
            family=family, user=other2, role=FamilyMember.Role.CHILD
        )

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(f"/api/v1/families/{family.public_id}/members/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

        emails = [m["user"]["email"] for m in response.data]
        assert "user@example.com" in emails
        assert "other1@example.com" in emails
        assert "other2@example.com" in emails

    def test_includes_user_info_and_role(self):
        """Test that each member includes user details and role."""
        admin = User.objects.create_user(
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

        family = Family.objects.create(name="Test Family", created_by=admin)
        FamilyMember.objects.create(
            family=family, user=admin, role=FamilyMember.Role.ORGANIZER
        )
        FamilyMember.objects.create(
            family=family, user=member, role=FamilyMember.Role.PARENT
        )

        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.get(f"/api/v1/families/{family.public_id}/members/")

        assert response.status_code == status.HTTP_200_OK

        # Check organizer data
        organizer_data = next(m for m in response.data if m["role"] == "organizer")
        assert organizer_data["user"]["email"] == "admin@example.com"
        assert organizer_data["user"]["first_name"] == "Admin"
        assert "public_id" in organizer_data

    def test_regular_member_can_view_members(self):
        """Test that regular (non-admin) members can view member list."""
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

        response = client.get(f"/api/v1/families/{family.public_id}/members/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_returns_403_if_user_not_a_member(self):
        """Test that outsiders cannot view member list."""
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

        response = client.get(f"/api/v1/families/{family.public_id}/members/")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestUpdateMemberRole:
    """
    Test suite for PATCH /api/v1/families/{public_id}/members/{user_public_id}/ (update role).

    Requirements:
    - Updates member role (admin only)
    - Returns 403 if user not admin
    - Validates role enum
    - Returns updated member data
    """

    def test_updates_member_role_as_organizer(self):
        """Test that organizer can update member role."""
        admin = User.objects.create_user(
            email="admin@example.com", password="testpass123"
        )
        member = User.objects.create_user(
            email="member@example.com", password="testpass123"
        )

        family = Family.objects.create(name="Test Family", created_by=admin)
        FamilyMember.objects.create(
            family=family, user=admin, role=FamilyMember.Role.ORGANIZER
        )
        FamilyMember.objects.create(
            family=family, user=member, role=FamilyMember.Role.PARENT
        )

        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.patch(
            f"/api/v1/families/{family.public_id}/members/{member.public_id}/",
            {"role": "child"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["role"] == "child"

        # Verify database was updated
        membership = FamilyMember.objects.get(family=family, user=member)
        assert membership.role == FamilyMember.Role.CHILD

    def test_can_promote_member_to_organizer(self):
        """Test that organizer can promote member to organizer."""
        admin = User.objects.create_user(
            email="admin@example.com", password="testpass123"
        )
        member = User.objects.create_user(
            email="member@example.com", password="testpass123"
        )

        family = Family.objects.create(name="Test Family", created_by=admin)
        FamilyMember.objects.create(
            family=family, user=admin, role=FamilyMember.Role.ORGANIZER
        )
        FamilyMember.objects.create(
            family=family, user=member, role=FamilyMember.Role.PARENT
        )

        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.patch(
            f"/api/v1/families/{family.public_id}/members/{member.public_id}/",
            {"role": "organizer"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["role"] == "organizer"

    def test_returns_403_if_user_not_organizer(self):
        """Test that regular members cannot update roles."""
        owner = User.objects.create_user(
            email="owner@example.com", password="testpass123"
        )
        member = User.objects.create_user(
            email="member@example.com", password="testpass123"
        )
        other_member = User.objects.create_user(
            email="other@example.com", password="testpass123"
        )

        family = Family.objects.create(name="Test Family", created_by=owner)
        FamilyMember.objects.create(
            family=family, user=owner, role=FamilyMember.Role.ORGANIZER
        )
        FamilyMember.objects.create(
            family=family, user=member, role=FamilyMember.Role.PARENT
        )
        FamilyMember.objects.create(
            family=family, user=other_member, role=FamilyMember.Role.PARENT
        )

        client = APIClient()
        client.force_authenticate(user=member)

        response = client.patch(
            f"/api/v1/families/{family.public_id}/members/{other_member.public_id}/",
            {"role": "child"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_404_if_user_not_in_family(self):
        """Test that updating non-member returns 404."""
        admin = User.objects.create_user(
            email="admin@example.com", password="testpass123"
        )
        outsider = User.objects.create_user(
            email="outsider@example.com", password="testpass123"
        )

        family = Family.objects.create(name="Test Family", created_by=admin)
        FamilyMember.objects.create(
            family=family, user=admin, role=FamilyMember.Role.ORGANIZER
        )

        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.patch(
            f"/api/v1/families/{family.public_id}/members/{outsider.public_id}/",
            {"role": "parent"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestRemoveMember:
    """
    Test suite for DELETE /api/v1/families/{public_id}/members/{user_public_id}/ (remove member).

    Requirements:
    - Admin can remove any member
    - Member can remove themselves
    - Returns 403 if member tries to remove others
    - Returns 204 No Content on success
    """

    def test_admin_can_remove_any_member(self):
        """Test that organizer can remove any member."""
        admin = User.objects.create_user(
            email="admin@example.com", password="testpass123"
        )
        member = User.objects.create_user(
            email="member@example.com", password="testpass123"
        )

        family = Family.objects.create(name="Test Family", created_by=admin)
        FamilyMember.objects.create(
            family=family, user=admin, role=FamilyMember.Role.ORGANIZER
        )
        FamilyMember.objects.create(
            family=family, user=member, role=FamilyMember.Role.PARENT
        )

        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.delete(
            f"/api/v1/families/{family.public_id}/members/{member.public_id}/"
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify membership was deleted
        assert not FamilyMember.objects.filter(family=family, user=member).exists()

    def test_member_can_remove_themselves(self):
        """Test that member can leave the family (self-removal)."""
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

        response = client.delete(
            f"/api/v1/families/{family.public_id}/members/{member.public_id}/"
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify membership was deleted
        assert not FamilyMember.objects.filter(family=family, user=member).exists()

    def test_returns_403_if_member_tries_to_remove_others(self):
        """Test that regular members cannot remove other members."""
        owner = User.objects.create_user(
            email="owner@example.com", password="testpass123"
        )
        member = User.objects.create_user(
            email="member@example.com", password="testpass123"
        )
        other_member = User.objects.create_user(
            email="other@example.com", password="testpass123"
        )

        family = Family.objects.create(name="Test Family", created_by=owner)
        FamilyMember.objects.create(
            family=family, user=owner, role=FamilyMember.Role.ORGANIZER
        )
        FamilyMember.objects.create(
            family=family, user=member, role=FamilyMember.Role.PARENT
        )
        FamilyMember.objects.create(
            family=family, user=other_member, role=FamilyMember.Role.PARENT
        )

        client = APIClient()
        client.force_authenticate(user=member)

        response = client.delete(
            f"/api/v1/families/{family.public_id}/members/{other_member.public_id}/"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Verify membership still exists
        assert FamilyMember.objects.filter(family=family, user=other_member).exists()

    def test_returns_404_if_user_not_in_family(self):
        """Test that removing non-member returns 404."""
        admin = User.objects.create_user(
            email="admin@example.com", password="testpass123"
        )
        outsider = User.objects.create_user(
            email="outsider@example.com", password="testpass123"
        )

        family = Family.objects.create(name="Test Family", created_by=admin)
        FamilyMember.objects.create(
            family=family, user=admin, role=FamilyMember.Role.ORGANIZER
        )

        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.delete(
            f"/api/v1/families/{family.public_id}/members/{outsider.public_id}/"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
