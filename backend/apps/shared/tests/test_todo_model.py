"""
Tests for Todo model
Following TDD discipline - Red-Green-Refactor

Testing FamApp todo management model.
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone

User = get_user_model()


@pytest.mark.django_db
class TestTodoModel:
    """Test Todo model"""

    def test_create_todo_with_required_fields(self, user):
        """Test: Create todo with title and family"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        todo = Todo.objects.create(title="Buy groceries", family=family)

        # Assert
        assert todo.id is not None
        assert todo.title == "Buy groceries"
        assert todo.family == family
        assert todo.public_id is not None

    def test_todo_title_is_required(self):
        """Test: Todo title is required"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act & Assert
        with pytest.raises(IntegrityError):
            Todo.objects.create(title=None, family=family)

    def test_todo_title_max_length_200(self):
        """Test: Todo title max length is 200 characters"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")
        long_title = "A" * 201

        # Act & Assert
        with pytest.raises(Exception):  # ValidationError or DataError
            Todo.objects.create(title=long_title, family=family)

    def test_todo_family_is_required(self):
        """Test: Todo family is required"""
        from apps.shared.models import Todo

        # Act & Assert
        with pytest.raises(IntegrityError):
            Todo.objects.create(title="Buy groceries", family=None)

    def test_todo_description_is_optional(self):
        """Test: Todo description is optional"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        todo = Todo.objects.create(title="Buy groceries", family=family)

        # Assert
        assert todo.description is None or todo.description == ""

    def test_todo_with_description(self):
        """Test: Todo can have description"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        todo = Todo.objects.create(
            title="Buy groceries",
            description="Get milk, eggs, and bread",
            family=family,
        )

        # Assert
        assert todo.description == "Get milk, eggs, and bread"

    def test_todo_status_enum_values(self):
        """Test: Status enum has correct values (TODO, IN_PROGRESS, DONE)"""
        from apps.shared.models import Todo

        # Assert
        assert hasattr(Todo, "Status")
        assert hasattr(Todo.Status, "TODO")
        assert hasattr(Todo.Status, "IN_PROGRESS")
        assert hasattr(Todo.Status, "DONE")

    def test_todo_default_status_is_todo(self):
        """Test: Default status is TODO"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        todo = Todo.objects.create(title="Buy groceries", family=family)

        # Assert
        assert todo.status == Todo.Status.TODO

    def test_todo_status_can_be_in_progress(self):
        """Test: Can create todo with IN_PROGRESS status"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        todo = Todo.objects.create(
            title="Buy groceries", family=family, status=Todo.Status.IN_PROGRESS
        )

        # Assert
        assert todo.status == Todo.Status.IN_PROGRESS

    def test_todo_status_can_be_done(self):
        """Test: Can create todo with DONE status"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        todo = Todo.objects.create(
            title="Buy groceries", family=family, status=Todo.Status.DONE
        )

        # Assert
        assert todo.status == Todo.Status.DONE

    def test_todo_priority_enum_values(self):
        """Test: Priority enum has correct values (LOW, MEDIUM, HIGH)"""
        from apps.shared.models import Todo

        # Assert
        assert hasattr(Todo, "Priority")
        assert hasattr(Todo.Priority, "LOW")
        assert hasattr(Todo.Priority, "MEDIUM")
        assert hasattr(Todo.Priority, "HIGH")

    def test_todo_default_priority_is_medium(self):
        """Test: Default priority is MEDIUM"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        todo = Todo.objects.create(title="Buy groceries", family=family)

        # Assert
        assert todo.priority == Todo.Priority.MEDIUM

    def test_todo_priority_can_be_low(self):
        """Test: Can create todo with LOW priority"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        todo = Todo.objects.create(
            title="Buy groceries", family=family, priority=Todo.Priority.LOW
        )

        # Assert
        assert todo.priority == Todo.Priority.LOW

    def test_todo_priority_can_be_high(self):
        """Test: Can create todo with HIGH priority"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        todo = Todo.objects.create(
            title="Buy groceries", family=family, priority=Todo.Priority.HIGH
        )

        # Assert
        assert todo.priority == Todo.Priority.HIGH

    def test_todo_due_date_is_optional(self):
        """Test: Todo due_date is optional"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        todo = Todo.objects.create(title="Buy groceries", family=family)

        # Assert
        assert todo.due_date is None

    def test_todo_with_due_date(self):
        """Test: Todo can have due_date"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")
        due_date = timezone.now() + timezone.timedelta(days=7)

        # Act
        todo = Todo.objects.create(
            title="Buy groceries", family=family, due_date=due_date
        )

        # Assert
        assert todo.due_date is not None
        assert todo.due_date == due_date

    def test_todo_assigned_to_is_optional(self):
        """Test: Todo assigned_to is optional"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        todo = Todo.objects.create(title="Buy groceries", family=family)

        # Assert
        assert todo.assigned_to is None

    def test_todo_with_assigned_to(self, user):
        """Test: Todo can be assigned to a user"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        todo = Todo.objects.create(
            title="Buy groceries", family=family, assigned_to=user
        )

        # Assert
        assert todo.assigned_to == user

    def test_todo_assigned_to_uses_set_null_on_delete(self, user):
        """Test: assigned_to uses SET_NULL when user is deleted"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")
        todo = Todo.objects.create(
            title="Buy groceries", family=family, assigned_to=user
        )
        assert todo.assigned_to == user

        # Act
        user_id = user.id
        user.delete()

        # Assert
        todo.refresh_from_db()
        assert todo.assigned_to is None

    def test_todo_has_timestamps(self):
        """Test: Todo has created_at and updated_at (BaseModel)"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        todo = Todo.objects.create(title="Buy groceries", family=family)

        # Assert
        assert todo.created_at is not None
        assert todo.updated_at is not None

    def test_todo_has_audit_fields(self, user):
        """Test: Todo has created_by and updated_by (BaseModel)"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        todo = Todo.objects.create(
            title="Buy groceries", family=family, created_by=user
        )

        # Assert
        assert hasattr(todo, "created_by")
        assert hasattr(todo, "updated_by")
        assert todo.created_by == user

    def test_todo_has_soft_delete_fields(self):
        """Test: Todo has is_deleted, deleted_at, deleted_by (BaseModel)"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        todo = Todo.objects.create(title="Buy groceries", family=family)

        # Assert
        assert hasattr(todo, "is_deleted")
        assert hasattr(todo, "deleted_at")
        assert hasattr(todo, "deleted_by")
        assert todo.is_deleted is False

    def test_todo_can_be_soft_deleted(self, user):
        """Test: Todo can be soft deleted"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")
        todo = Todo.objects.create(title="Buy groceries", family=family)

        # Act
        todo.soft_delete(user=user)

        # Assert
        todo.refresh_from_db()
        assert todo.is_deleted is True
        assert todo.deleted_at is not None
        assert todo.deleted_by == user

    def test_todo_str_representation(self):
        """Test: Todo __str__ returns meaningful representation"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")
        todo = Todo.objects.create(title="Buy groceries", family=family)

        # Act
        str_repr = str(todo)

        # Assert
        assert "Buy groceries" in str_repr

    def test_delete_family_cascades_to_todos(self):
        """Test: Deleting family hard-deletes all related Todos"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")
        todo = Todo.objects.create(title="Buy groceries", family=family)
        todo_id = todo.id

        # Act
        family.delete()

        # Assert
        # Todo should be hard deleted (CASCADE)
        assert not Todo.objects.filter(id=todo_id).exists()

    def test_family_has_reverse_relationship_to_todos(self):
        """Test: Family has reverse relationship to todos"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")
        Todo.objects.create(title="Buy groceries", family=family)
        Todo.objects.create(title="Clean house", family=family)

        # Act
        todos = family.todo_set.all()

        # Assert
        assert todos.count() == 2

    def test_user_has_reverse_relationship_to_assigned_todos(self, user):
        """Test: User has reverse relationship to assigned todos"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")
        Todo.objects.create(title="Buy groceries", family=family, assigned_to=user)
        Todo.objects.create(title="Clean house", family=family, assigned_to=user)

        # Act
        assigned_todos = user.todo_assigned_to.all()

        # Assert
        assert assigned_todos.count() == 2

    def test_todo_status_can_be_updated(self):
        """Test: Todo status can be updated"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")
        todo = Todo.objects.create(title="Buy groceries", family=family)
        assert todo.status == Todo.Status.TODO

        # Act
        todo.status = Todo.Status.IN_PROGRESS
        todo.save()

        # Assert
        todo.refresh_from_db()
        assert todo.status == Todo.Status.IN_PROGRESS

    def test_todo_priority_can_be_updated(self):
        """Test: Todo priority can be updated"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")
        todo = Todo.objects.create(title="Buy groceries", family=family)
        assert todo.priority == Todo.Priority.MEDIUM

        # Act
        todo.priority = Todo.Priority.HIGH
        todo.save()

        # Assert
        todo.refresh_from_db()
        assert todo.priority == Todo.Priority.HIGH

    def test_multiple_todos_per_family(self):
        """Test: Family can have multiple todos"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        Todo.objects.create(title="Buy groceries", family=family)
        Todo.objects.create(title="Clean house", family=family)
        Todo.objects.create(title="Walk dog", family=family)

        # Assert
        assert family.todo_set.count() == 3

    def test_user_can_have_multiple_assigned_todos(self, user):
        """Test: User can be assigned multiple todos"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        Todo.objects.create(title="Buy groceries", family=family, assigned_to=user)
        Todo.objects.create(title="Clean house", family=family, assigned_to=user)

        # Assert
        assert user.todo_assigned_to.count() == 2

    def test_todo_with_all_fields(self, user):
        """Test: Create todo with all fields populated"""
        from apps.shared.models import Family, Todo

        # Arrange
        family = Family.objects.create(name="Smith Family")
        due_date = timezone.now() + timezone.timedelta(days=7)

        # Act
        todo = Todo.objects.create(
            title="Buy groceries",
            description="Get milk, eggs, and bread",
            status=Todo.Status.IN_PROGRESS,
            priority=Todo.Priority.HIGH,
            due_date=due_date,
            assigned_to=user,
            family=family,
            created_by=user,
        )

        # Assert
        assert todo.title == "Buy groceries"
        assert todo.description == "Get milk, eggs, and bread"
        assert todo.status == Todo.Status.IN_PROGRESS
        assert todo.priority == Todo.Priority.HIGH
        assert todo.due_date == due_date
        assert todo.assigned_to == user
        assert todo.family == family
        assert todo.created_by == user
