"""
Test module for Todo serializers.

Following TDD methodology (Red-Green-Refactor):
Tests for TodoCreateSerializer, TodoUpdateSerializer, TodoSerializer, TodoToggleSerializer

Ham Dog & TC making sure todo serialization rocks! 🚀
"""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.shared.models import Family, FamilyMember, Todo

User = get_user_model()


@pytest.mark.django_db
class TestTodoCreateSerializer:
    """Test suite for TodoCreateSerializer."""

    def test_validates_title_is_required(self):
        """Test that title field is required."""
        from apps.shared.serializers import TodoCreateSerializer

        serializer = TodoCreateSerializer(data={})
        assert not serializer.is_valid()
        assert "title" in serializer.errors

    def test_validates_title_not_empty(self):
        """Test that title cannot be empty string."""
        from apps.shared.serializers import TodoCreateSerializer

        serializer = TodoCreateSerializer(data={"title": ""})
        assert not serializer.is_valid()
        assert "title" in serializer.errors

    def test_validates_due_date_in_future(self):
        """Test that due_date must be in the future."""
        from apps.shared.serializers import TodoCreateSerializer

        past_date = timezone.now() - timedelta(days=1)
        serializer = TodoCreateSerializer(
            data={"title": "Test Todo", "due_date": past_date}
        )
        assert not serializer.is_valid()
        assert "due_date" in serializer.errors

    def test_accepts_valid_todo_data(self):
        """Test that valid todo data passes validation."""
        from apps.shared.serializers import TodoCreateSerializer

        # Create a family for the test
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        future_date = timezone.now() + timedelta(days=1)
        serializer = TodoCreateSerializer(
            data={
                "family_public_id": str(family.public_id),
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "priority": "high",
                "due_date": future_date,
            },
            context={"request": type("obj", (object,), {"user": user})},
        )
        assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
class TestTodoUpdateSerializer:
    """Test suite for TodoUpdateSerializer."""

    def test_allows_partial_updates(self):
        """Test that all fields are optional for updates."""
        from apps.shared.serializers import TodoUpdateSerializer

        serializer = TodoUpdateSerializer(data={})
        assert serializer.is_valid(), serializer.errors

    def test_updates_todo_fields(self):
        """Test that todo fields can be updated."""
        from apps.shared.serializers import TodoUpdateSerializer

        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        todo = Todo.objects.create(title="Old Title", family=family, created_by=user)

        serializer = TodoUpdateSerializer(
            instance=todo,
            data={"title": "New Title", "status": "in_progress"},
            partial=True,
        )
        assert serializer.is_valid(), serializer.errors

        updated_todo = serializer.save()
        assert updated_todo.title == "New Title"
        assert updated_todo.status == "in_progress"


@pytest.mark.django_db
class TestTodoSerializer:
    """Test suite for TodoSerializer (read serializer)."""

    def test_includes_all_expected_fields(self):
        """Test that serializer includes all expected fields."""
        from apps.shared.serializers import TodoSerializer

        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        todo = Todo.objects.create(title="Test Todo", family=family, created_by=user)

        serializer = TodoSerializer(instance=todo)
        data = serializer.data

        assert "id" in data
        assert "public_id" in data
        assert "title" in data
        assert "description" in data
        assert "status" in data
        assert "priority" in data
        assert "is_overdue" in data
        assert "created_at" in data

    def test_is_overdue_false_when_no_due_date(self):
        """Test that is_overdue is False when there's no due date."""
        from apps.shared.serializers import TodoSerializer

        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        todo = Todo.objects.create(
            title="Test Todo", family=family, created_by=user, due_date=None
        )

        serializer = TodoSerializer(instance=todo)
        assert serializer.data["is_overdue"] is False

    def test_is_overdue_true_when_past_due(self):
        """Test that is_overdue is True when due date is in the past."""
        from apps.shared.serializers import TodoSerializer

        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        past_date = timezone.now() - timedelta(days=1)
        todo = Todo.objects.create(
            title="Overdue Todo",
            family=family,
            created_by=user,
            due_date=past_date,
            status=Todo.Status.TODO,
        )

        serializer = TodoSerializer(instance=todo)
        assert serializer.data["is_overdue"] is True

    def test_is_overdue_false_when_completed(self):
        """Test that is_overdue is False for completed todos even if past due."""
        from apps.shared.serializers import TodoSerializer

        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        past_date = timezone.now() - timedelta(days=1)
        todo = Todo.objects.create(
            title="Completed Todo",
            family=family,
            created_by=user,
            due_date=past_date,
            status=Todo.Status.DONE,
        )

        serializer = TodoSerializer(instance=todo)
        assert serializer.data["is_overdue"] is False
