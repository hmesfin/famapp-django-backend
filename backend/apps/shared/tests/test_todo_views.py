"""
Test module for Todo ViewSet API endpoints.

Following TDD methodology (Red-Green-Refactor):
Tests for TodoViewSet CRUD operations with FamilyAccessMixin.

Ham Dog & TC building task management APIs! 📝
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.shared.models import Family
from apps.shared.models import FamilyMember
from apps.shared.models import Todo

User = get_user_model()


@pytest.mark.django_db
class TestListTodos:
    """
    Test suite for GET /api/v1/todos/ - List todos.

    Tests the FamilyAccessMixin in action!
    """

    def test_returns_todos_from_user_families_only(self):
        """Test that user only sees todos from their families."""
        client = APIClient()

        # Create two users with separate families
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

        # Create todos in each family
        todo1 = Todo.objects.create(
            family=family1, title="Todo 1", created_by=user1, updated_by=user1
        )
        Todo.objects.create(
            family=family2, title="Todo 2", created_by=user2, updated_by=user2
        )

        # User1 should only see todo1
        client.force_authenticate(user=user1)
        response = client.get("/api/v1/todos/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["public_id"] == str(todo1.public_id)
        assert response.data[0]["title"] == "Todo 1"

    def test_returns_todos_from_all_user_families(self):
        """Test that user sees todos from ALL their families."""
        client = APIClient()

        # Create user who belongs to multiple families
        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )

        family1 = Family.objects.create(name="Family 1", created_by=user)
        family2 = Family.objects.create(name="Family 2", created_by=user)

        FamilyMember.objects.create(
            family=family1, user=user, role=FamilyMember.Role.ORGANIZER
        )
        FamilyMember.objects.create(
            family=family2, user=user, role=FamilyMember.Role.PARENT
        )

        # Create todos in both families
        todo1 = Todo.objects.create(
            family=family1, title="Todo 1", created_by=user, updated_by=user
        )
        todo2 = Todo.objects.create(
            family=family2, title="Todo 2", created_by=user, updated_by=user
        )

        # User should see both todos
        client.force_authenticate(user=user)
        response = client.get("/api/v1/todos/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        titles = [todo["title"] for todo in response.data]
        assert "Todo 1" in titles
        assert "Todo 2" in titles

    def test_excludes_soft_deleted_todos(self):
        """Test that soft-deleted todos are excluded."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        # Create two todos
        todo1 = Todo.objects.create(
            family=family, title="Active Todo", created_by=user, updated_by=user
        )
        todo2 = Todo.objects.create(
            family=family, title="Deleted Todo", created_by=user, updated_by=user
        )

        # Soft delete todo2
        todo2.is_deleted = True
        todo2.deleted_at = timezone.now()
        todo2.save()

        # Should only see todo1
        client.force_authenticate(user=user)
        response = client.get("/api/v1/todos/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["title"] == "Active Todo"

    def test_excludes_todos_from_soft_deleted_families(self):
        """Test that todos from soft-deleted families are excluded."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        Todo.objects.create(
            family=family, title="Test Todo", created_by=user, updated_by=user
        )

        # Soft delete the family
        family.is_deleted = True
        family.deleted_at = timezone.now()
        family.save()

        # Should return empty list
        client.force_authenticate(user=user)
        response = client.get("/api/v1/todos/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_returns_empty_list_if_no_families(self):
        """Test that user with no families gets empty list."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )

        # Create another family with a todo (user not a member)
        owner = User.objects.create_user(
            email="owner@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=owner)
        FamilyMember.objects.create(
            family=family, user=owner, role=FamilyMember.Role.ORGANIZER
        )
        Todo.objects.create(
            family=family, title="Test Todo", created_by=owner, updated_by=owner
        )

        # User should get empty list
        client.force_authenticate(user=user)
        response = client.get("/api/v1/todos/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_returns_401_if_not_authenticated(self):
        """Test that unauthenticated requests return 401."""
        client = APIClient()
        response = client.get("/api/v1/todos/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCreateTodo:
    """
    Test suite for POST /api/v1/todos/ - Create todo.
    """

    def test_creates_todo_with_required_fields_only(self):
        """Test creating todo with just family and title."""
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
            "/api/v1/todos/",
            {"family_public_id": str(family.public_id), "title": "New Todo"},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "New Todo"
        assert response.data["status"] == Todo.Status.TODO
        assert response.data["priority"] == Todo.Priority.MEDIUM
        assert "public_id" in response.data
        assert "created_at" in response.data

    def test_creates_todo_with_all_fields(self):
        """Test creating todo with all optional fields."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        due_date = timezone.now() + timezone.timedelta(days=7)

        client.force_authenticate(user=user)
        response = client.post(
            "/api/v1/todos/",
            {
                "family_public_id": str(family.public_id),
                "title": "Complete Todo",
                "description": "This is a detailed description",
                "status": Todo.Status.IN_PROGRESS,
                "priority": Todo.Priority.HIGH,
                "due_date": due_date.isoformat(),
                "assigned_to_public_id": str(user.public_id),
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "Complete Todo"
        assert response.data["description"] == "This is a detailed description"
        assert response.data["status"] == Todo.Status.IN_PROGRESS
        assert response.data["priority"] == Todo.Priority.HIGH

    def test_sets_created_by_to_current_user(self):
        """Test that created_by is automatically set."""
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
            "/api/v1/todos/",
            {"family_public_id": str(family.public_id), "title": "New Todo"},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        # Verify in database
        todo = Todo.objects.get(public_id=response.data["public_id"])
        assert todo.created_by == user
        assert todo.updated_by == user

    def test_returns_400_if_title_missing(self):
        """Test that title is required."""
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
            "/api/v1/todos/",
            {"family_public_id": str(family.public_id)},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "title" in response.data

    def test_returns_400_if_family_not_found(self):
        """Test that invalid family returns 400."""
        import uuid

        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )

        client.force_authenticate(user=user)
        response = client.post(
            "/api/v1/todos/",
            {"family_public_id": str(uuid.uuid4()), "title": "New Todo"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_returns_400_if_user_not_family_member(self):
        """Test that non-members cannot create todos (validation error)."""
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

        client.force_authenticate(user=user)
        response = client.post(
            "/api/v1/todos/",
            {"family_public_id": str(family.public_id), "title": "New Todo"},
            format="json",
        )

        # Returns 400 because serializer validates family membership
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "family_public_id" in response.data


@pytest.mark.django_db
class TestRetrieveTodo:
    """
    Test suite for GET /api/v1/todos/{public_id}/ - Retrieve todo.
    """

    def test_returns_todo_details(self):
        """Test retrieving todo details."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        todo = Todo.objects.create(
            family=family,
            title="Test Todo",
            description="Test description",
            created_by=user,
            updated_by=user,
        )

        client.force_authenticate(user=user)
        response = client.get(f"/api/v1/todos/{todo.public_id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["public_id"] == str(todo.public_id)
        assert response.data["title"] == "Test Todo"
        assert response.data["description"] == "Test description"

    def test_returns_404_if_todo_not_found(self):
        """Test that non-existent todo returns 404."""
        import uuid

        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )

        client.force_authenticate(user=user)
        response = client.get(f"/api/v1/todos/{uuid.uuid4()}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_returns_404_if_todo_not_in_user_families(self):
        """Test that user cannot access todos from other families."""
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

        todo = Todo.objects.create(
            family=family, title="Test Todo", created_by=owner, updated_by=owner
        )

        # User (not a member) should get 404
        client.force_authenticate(user=user)
        response = client.get(f"/api/v1/todos/{todo.public_id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestUpdateTodo:
    """
    Test suite for PATCH /api/v1/todos/{public_id}/ - Update todo.
    """

    def test_updates_todo_fields(self):
        """Test updating todo fields."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        todo = Todo.objects.create(
            family=family, title="Original Title", created_by=user, updated_by=user
        )

        client.force_authenticate(user=user)
        response = client.patch(
            f"/api/v1/todos/{todo.public_id}/",
            {
                "title": "Updated Title",
                "description": "New description",
                "priority": Todo.Priority.HIGH,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated Title"
        assert response.data["description"] == "New description"
        assert response.data["priority"] == Todo.Priority.HIGH

    def test_allows_partial_updates(self):
        """Test that partial updates work (only title)."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        todo = Todo.objects.create(
            family=family,
            title="Original Title",
            description="Original description",
            created_by=user,
            updated_by=user,
        )

        client.force_authenticate(user=user)
        response = client.patch(
            f"/api/v1/todos/{todo.public_id}/",
            {"title": "Updated Title"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated Title"
        assert response.data["description"] == "Original description"

    def test_updates_updated_by_field(self):
        """Test that updated_by is set to current user."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        todo = Todo.objects.create(
            family=family, title="Test Todo", created_by=user, updated_by=user
        )

        client.force_authenticate(user=user)
        response = client.patch(
            f"/api/v1/todos/{todo.public_id}/",
            {"title": "Updated Title"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify in database
        todo.refresh_from_db()
        assert todo.updated_by == user

    def test_returns_404_if_todo_not_in_user_families(self):
        """Test that user cannot update todos from other families."""
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

        todo = Todo.objects.create(
            family=family, title="Test Todo", created_by=owner, updated_by=owner
        )

        # User (not a member) should get 404
        client.force_authenticate(user=user)
        response = client.patch(
            f"/api/v1/todos/{todo.public_id}/",
            {"title": "Hacked Title"},
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestToggleTodoCompletion:
    """
    Test suite for PATCH /api/v1/todos/{public_id}/toggle/ - Toggle completion.
    """

    def test_marks_incomplete_todo_as_complete(self):
        """Test marking incomplete todo as complete."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        todo = Todo.objects.create(
            family=family,
            title="Test Todo",
            status=Todo.Status.TODO,
            created_by=user,
            updated_by=user,
        )

        client.force_authenticate(user=user)
        response = client.patch(f"/api/v1/todos/{todo.public_id}/toggle/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == Todo.Status.DONE

        # Verify in database
        todo.refresh_from_db()
        assert todo.status == Todo.Status.DONE

    def test_marks_complete_todo_as_incomplete(self):
        """Test marking complete todo as incomplete."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        todo = Todo.objects.create(
            family=family,
            title="Test Todo",
            status=Todo.Status.DONE,
            created_by=user,
            updated_by=user,
        )

        client.force_authenticate(user=user)
        response = client.patch(f"/api/v1/todos/{todo.public_id}/toggle/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == Todo.Status.TODO

        # Verify in database
        todo.refresh_from_db()
        assert todo.status == Todo.Status.TODO

    def test_returns_404_if_todo_not_in_user_families(self):
        """Test that user cannot toggle todos from other families."""
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

        todo = Todo.objects.create(
            family=family, title="Test Todo", created_by=owner, updated_by=owner
        )

        # User (not a member) should get 404
        client.force_authenticate(user=user)
        response = client.patch(f"/api/v1/todos/{todo.public_id}/toggle/")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDeleteTodo:
    """
    Test suite for DELETE /api/v1/todos/{public_id}/ - Soft delete todo.
    """

    def test_soft_deletes_todo(self):
        """Test that delete soft-deletes the todo."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        todo = Todo.objects.create(
            family=family, title="Test Todo", created_by=user, updated_by=user
        )

        client.force_authenticate(user=user)
        response = client.delete(f"/api/v1/todos/{todo.public_id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify soft delete in database
        todo.refresh_from_db()
        assert todo.is_deleted is True
        assert todo.deleted_at is not None

    def test_soft_deleted_todo_not_in_list(self):
        """Test that soft-deleted todos don't appear in list."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        todo = Todo.objects.create(
            family=family, title="Test Todo", created_by=user, updated_by=user
        )

        client.force_authenticate(user=user)

        # Delete the todo
        response = client.delete(f"/api/v1/todos/{todo.public_id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # List should be empty
        response = client.get("/api/v1/todos/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_returns_404_if_todo_not_in_user_families(self):
        """Test that user cannot delete todos from other families."""
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

        todo = Todo.objects.create(
            family=family, title="Test Todo", created_by=owner, updated_by=owner
        )

        # User (not a member) should get 404
        client.force_authenticate(user=user)
        response = client.delete(f"/api/v1/todos/{todo.public_id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
