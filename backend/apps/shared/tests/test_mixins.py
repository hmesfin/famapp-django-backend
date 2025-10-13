"""
Test module for custom DRF mixins.

Following TDD methodology (Red-Green-Refactor):
Tests for FamilyAccessMixin that filters queryset by family membership.

Ham Dog & TC building reusable authorization patterns! 🔒
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory

from apps.shared.models import Family
from apps.shared.models import FamilyMember
from apps.shared.models import Todo

User = get_user_model()


@pytest.mark.django_db
class TestFamilyAccessMixin:
    """
    Test suite for FamilyAccessMixin.

    This mixin ensures that ViewSets automatically filter queryset to only
    resources in families where the request user is a member.
    """

    def test_filters_queryset_to_user_families_only(self):
        """Test that mixin filters queryset to user's families only."""
        from rest_framework import viewsets

        from apps.shared.mixins import FamilyAccessMixin

        # Create two families with different members
        user1 = User.objects.create_user(
            email="user1@example.com", password="testpass123",
        )
        user2 = User.objects.create_user(
            email="user2@example.com", password="testpass123",
        )

        family1 = Family.objects.create(name="Family 1", created_by=user1)
        family2 = Family.objects.create(name="Family 2", created_by=user2)

        FamilyMember.objects.create(
            family=family1, user=user1, role=FamilyMember.Role.ORGANIZER,
        )
        FamilyMember.objects.create(
            family=family2, user=user2, role=FamilyMember.Role.ORGANIZER,
        )

        # Create todos in each family
        todo1 = Todo.objects.create(
            family=family1, title="Todo 1", created_by=user1, updated_by=user1,
        )
        todo2 = Todo.objects.create(
            family=family2, title="Todo 2", created_by=user2, updated_by=user2,
        )

        # Create test ViewSet with mixin
        class TestTodoViewSet(FamilyAccessMixin, viewsets.ModelViewSet):
            queryset = Todo.objects.all()

        # Create mock request with user1
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = user1

        # Create view instance
        view = TestTodoViewSet()
        view.request = request
        view.format_kwarg = None

        # Get filtered queryset
        queryset = view.get_queryset()

        # Should only include todo1 (user1's family)
        assert queryset.count() == 1
        assert todo1 in queryset
        assert todo2 not in queryset

    def test_excludes_soft_deleted_families(self):
        """Test that mixin excludes resources from soft-deleted families."""
        from django.utils import timezone
        from rest_framework import viewsets

        from apps.shared.mixins import FamilyAccessMixin

        # Create user and family
        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        # Create todo
        todo = Todo.objects.create(
            family=family, title="Test Todo", created_by=user, updated_by=user,
        )

        # Create test ViewSet
        class TestTodoViewSet(FamilyAccessMixin, viewsets.ModelViewSet):
            queryset = Todo.objects.all()

        # Create mock request
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = user

        view = TestTodoViewSet()
        view.request = request
        view.format_kwarg = None

        # Should include todo before soft delete
        queryset = view.get_queryset()
        assert queryset.count() == 1
        assert todo in queryset

        # Soft delete the family
        family.is_deleted = True
        family.deleted_at = timezone.now()
        family.save()

        # Should exclude todo after family soft delete
        queryset = view.get_queryset()
        assert queryset.count() == 0
        assert todo not in queryset

    def test_excludes_soft_deleted_resources(self):
        """Test that mixin excludes soft-deleted resources themselves."""
        from django.utils import timezone
        from rest_framework import viewsets

        from apps.shared.mixins import FamilyAccessMixin

        # Create user and family
        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        # Create two todos
        todo1 = Todo.objects.create(
            family=family, title="Todo 1", created_by=user, updated_by=user,
        )
        todo2 = Todo.objects.create(
            family=family, title="Todo 2", created_by=user, updated_by=user,
        )

        # Create test ViewSet
        class TestTodoViewSet(FamilyAccessMixin, viewsets.ModelViewSet):
            queryset = Todo.objects.all()

        # Create mock request
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = user

        view = TestTodoViewSet()
        view.request = request
        view.format_kwarg = None

        # Should include both todos initially
        queryset = view.get_queryset()
        assert queryset.count() == 2

        # Soft delete todo1
        todo1.is_deleted = True
        todo1.deleted_at = timezone.now()
        todo1.save()

        # Should only include todo2
        queryset = view.get_queryset()
        assert queryset.count() == 1
        assert todo1 not in queryset
        assert todo2 in queryset

    def test_returns_empty_queryset_if_user_not_in_any_family(self):
        """Test that mixin returns empty queryset if user has no families."""
        from rest_framework import viewsets

        from apps.shared.mixins import FamilyAccessMixin

        # Create user with no family memberships
        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )

        # Create another user with a family and todo
        owner = User.objects.create_user(
            email="owner@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=owner)
        FamilyMember.objects.create(
            family=family, user=owner, role=FamilyMember.Role.ORGANIZER,
        )
        Todo.objects.create(
            family=family, title="Test Todo", created_by=owner, updated_by=owner,
        )

        # Create test ViewSet
        class TestTodoViewSet(FamilyAccessMixin, viewsets.ModelViewSet):
            queryset = Todo.objects.all()

        # Create mock request with user (no families)
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = user

        view = TestTodoViewSet()
        view.request = request
        view.format_kwarg = None

        # Should return empty queryset
        queryset = view.get_queryset()
        assert queryset.count() == 0

    def test_works_with_multiple_families(self):
        """Test that mixin includes resources from all user's families."""
        from rest_framework import viewsets

        from apps.shared.mixins import FamilyAccessMixin

        # Create user who belongs to multiple families
        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )

        # Create two families with user as member
        family1 = Family.objects.create(name="Family 1", created_by=user)
        family2 = Family.objects.create(name="Family 2", created_by=user)

        FamilyMember.objects.create(
            family=family1, user=user, role=FamilyMember.Role.ORGANIZER,
        )
        FamilyMember.objects.create(
            family=family2, user=user, role=FamilyMember.Role.PARENT,
        )

        # Create todos in both families
        todo1 = Todo.objects.create(
            family=family1, title="Todo 1", created_by=user, updated_by=user,
        )
        todo2 = Todo.objects.create(
            family=family2, title="Todo 2", created_by=user, updated_by=user,
        )

        # Create test ViewSet
        class TestTodoViewSet(FamilyAccessMixin, viewsets.ModelViewSet):
            queryset = Todo.objects.all()

        # Create mock request
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = user

        view = TestTodoViewSet()
        view.request = request
        view.format_kwarg = None

        # Should include todos from both families
        queryset = view.get_queryset()
        assert queryset.count() == 2
        assert todo1 in queryset
        assert todo2 in queryset

    def test_respects_base_queryset_filters(self):
        """Test that mixin preserves additional filters on base queryset."""
        from rest_framework import viewsets

        from apps.shared.mixins import FamilyAccessMixin

        # Create user and family
        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        # Create todos with different statuses
        todo1 = Todo.objects.create(
            family=family,
            title="Todo 1",
            status=Todo.Status.TODO,
            created_by=user,
            updated_by=user,
        )
        todo2 = Todo.objects.create(
            family=family,
            title="Todo 2",
            status=Todo.Status.DONE,
            created_by=user,
            updated_by=user,
        )

        # Create test ViewSet with base queryset filter
        class TestTodoViewSet(FamilyAccessMixin, viewsets.ModelViewSet):
            # Base queryset only includes TODO status
            queryset = Todo.objects.filter(status=Todo.Status.TODO)

        # Create mock request
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = user

        view = TestTodoViewSet()
        view.request = request
        view.format_kwarg = None

        # Should only include todo1 (status=TODO)
        queryset = view.get_queryset()
        assert queryset.count() == 1
        assert todo1 in queryset
        assert todo2 not in queryset
