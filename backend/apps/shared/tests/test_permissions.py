"""
Test module for custom DRF permissions.

Following TDD methodology (Red-Green-Refactor):
Tests for IsFamilyMember and IsFamilyAdmin permission classes.

Ham Dog & TC building bulletproof authorization! 🔒
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from unittest.mock import Mock

from apps.shared.models import Family, FamilyMember

User = get_user_model()


@pytest.mark.django_db
class TestIsFamilyMemberPermission:
    """
    Test suite for IsFamilyMember permission class.

    This permission ensures that only family members can access family resources.
    """

    def test_allows_access_if_user_is_family_member(self):
        """Test that permission grants access if user is a family member."""
        from apps.shared.permissions import IsFamilyMember

        # Create family and users
        user = User.objects.create_user(
            email="member@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.PARENT
        )

        # Create mock request with family in view kwargs
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = user

        # Create mock view with family lookup
        view = Mock()
        view.kwargs = {"family_public_id": str(family.public_id)}

        # Test permission
        permission = IsFamilyMember()
        assert permission.has_permission(request, view) is True

    def test_denies_access_if_user_not_a_member(self):
        """Test that permission returns False if user is not a member."""
        from apps.shared.permissions import IsFamilyMember

        # Create family and users
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

        # Create mock request with outsider user
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = outsider

        # Create mock view with family lookup
        view = Mock()
        view.kwargs = {"family_public_id": str(family.public_id)}

        # Test permission
        permission = IsFamilyMember()
        assert permission.has_permission(request, view) is False

    def test_denies_access_if_family_not_found(self):
        """Test that permission returns False if family doesn't exist."""
        from apps.shared.permissions import IsFamilyMember
        import uuid

        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

        # Create mock request with non-existent family
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = user

        # Create mock view with invalid family_public_id
        view = Mock()
        view.kwargs = {"family_public_id": str(uuid.uuid4())}

        # Test permission
        permission = IsFamilyMember()
        assert permission.has_permission(request, view) is False

    def test_works_with_object_permission_check(self):
        """Test that has_object_permission also works correctly."""
        from apps.shared.permissions import IsFamilyMember

        # Create family and users
        user = User.objects.create_user(
            email="member@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.PARENT
        )

        # Create mock request
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = user

        # Create mock view
        view = Mock()

        # Test object-level permission
        permission = IsFamilyMember()
        assert permission.has_object_permission(request, view, family) is True

    def test_object_permission_denies_non_member(self):
        """Test that has_object_permission denies access to non-members."""
        from apps.shared.permissions import IsFamilyMember

        # Create family and users
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

        # Create mock request with outsider
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = outsider

        # Create mock view
        view = Mock()

        # Test object-level permission
        permission = IsFamilyMember()
        assert permission.has_object_permission(request, view, family) is False


@pytest.mark.django_db
class TestIsFamilyAdminPermission:
    """
    Test suite for IsFamilyAdmin permission class.

    This permission ensures that only family admins (organizers) can perform
    administrative actions.
    """

    def test_allows_access_if_user_is_organizer(self):
        """Test that permission grants access if user is organizer."""
        from apps.shared.permissions import IsFamilyAdmin

        # Create family with organizer
        user = User.objects.create_user(
            email="admin@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        # Create mock request
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = user

        # Create mock view with family lookup
        view = Mock()
        view.kwargs = {"family_public_id": str(family.public_id)}

        # Test permission
        permission = IsFamilyAdmin()
        assert permission.has_permission(request, view) is True

    def test_denies_access_if_user_is_parent(self):
        """Test that permission denies access if user is regular parent."""
        from apps.shared.permissions import IsFamilyAdmin

        # Create family with parent (not organizer)
        owner = User.objects.create_user(
            email="owner@example.com", password="testpass123"
        )
        parent = User.objects.create_user(
            email="parent@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=owner)
        FamilyMember.objects.create(
            family=family, user=owner, role=FamilyMember.Role.ORGANIZER
        )
        FamilyMember.objects.create(
            family=family, user=parent, role=FamilyMember.Role.PARENT
        )

        # Create mock request with parent user
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = parent

        # Create mock view with family lookup
        view = Mock()
        view.kwargs = {"family_public_id": str(family.public_id)}

        # Test permission
        permission = IsFamilyAdmin()
        assert permission.has_permission(request, view) is False

    def test_denies_access_if_user_not_a_member(self):
        """Test that permission denies access if user is not a member at all."""
        from apps.shared.permissions import IsFamilyAdmin

        # Create family and outsider
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

        # Create mock request with outsider
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = outsider

        # Create mock view with family lookup
        view = Mock()
        view.kwargs = {"family_public_id": str(family.public_id)}

        # Test permission
        permission = IsFamilyAdmin()
        assert permission.has_permission(request, view) is False

    def test_object_permission_allows_organizer(self):
        """Test that has_object_permission grants access to organizers."""
        from apps.shared.permissions import IsFamilyAdmin

        # Create family with organizer
        user = User.objects.create_user(
            email="admin@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        # Create mock request
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = user

        # Create mock view
        view = Mock()

        # Test object-level permission
        permission = IsFamilyAdmin()
        assert permission.has_object_permission(request, view, family) is True

    def test_object_permission_denies_non_organizer(self):
        """Test that has_object_permission denies non-organizers."""
        from apps.shared.permissions import IsFamilyAdmin

        # Create family with parent (not organizer)
        owner = User.objects.create_user(
            email="owner@example.com", password="testpass123"
        )
        parent = User.objects.create_user(
            email="parent@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=owner)
        FamilyMember.objects.create(
            family=family, user=owner, role=FamilyMember.Role.ORGANIZER
        )
        FamilyMember.objects.create(
            family=family, user=parent, role=FamilyMember.Role.PARENT
        )

        # Create mock request with parent
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = parent

        # Create mock view
        view = Mock()

        # Test object-level permission
        permission = IsFamilyAdmin()
        assert permission.has_object_permission(request, view, family) is False
