"""
Test module for Celery tasks.

Tests verify that tasks can be discovered, executed, and produce correct results.
Note: These are unit tests for task logic, not integration tests for Celery infrastructure.

Ham Dog & TC testing async tasks! 🔮
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.shared.models import Family
from apps.shared.models import FamilyMember
from apps.shared.models import Pet
from apps.shared.models import PetActivity
from apps.shared.models import ScheduleEvent
from apps.shared.models import Todo
from apps.shared.tasks import cleanup_old_soft_deleted_records
from apps.shared.tasks import send_event_reminders
from apps.shared.tasks import send_pet_feeding_reminders
from apps.shared.tasks import send_pet_walking_reminders
from apps.shared.tasks import send_todo_reminders

User = get_user_model()


@pytest.mark.django_db
class TestTodoReminderTask:
    """Test suite for send_todo_reminders task."""

    def test_finds_upcoming_todos(self):
        """Test that task finds todos due within lead time."""
        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        # Create todo due in 30 minutes
        due_soon = timezone.now() + timezone.timedelta(minutes=30)
        Todo.objects.create(
            family=family,
            title="Urgent task",
            due_date=due_soon,
            status=Todo.Status.TODO,
            created_by=user,
        )

        # Execute task
        result = send_todo_reminders(lead_time_hours=1)

        assert result["reminders_sent"] == 1
        assert result["lead_time_hours"] == 1

    def test_ignores_completed_todos(self):
        """Test that task ignores completed todos."""
        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        # Create completed todo
        due_soon = timezone.now() + timezone.timedelta(minutes=30)
        Todo.objects.create(
            family=family,
            title="Done task",
            due_date=due_soon,
            status=Todo.Status.DONE,
            created_by=user,
        )

        # Execute task
        result = send_todo_reminders(lead_time_hours=1)

        assert result["reminders_sent"] == 0


@pytest.mark.django_db
class TestEventReminderTask:
    """Test suite for send_event_reminders task."""

    def test_finds_upcoming_events(self):
        """Test that task finds events starting soon."""
        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        # Create event starting in 10 minutes
        start_soon = timezone.now() + timezone.timedelta(minutes=10)
        end_time = start_soon + timezone.timedelta(hours=1)
        ScheduleEvent.objects.create(
            family=family,
            title="Meeting",
            start_time=start_soon,
            end_time=end_time,
            created_by=user,
        )

        # Execute task
        result = send_event_reminders(lead_time_minutes=15)

        assert result["reminders_sent"] == 1
        assert result["lead_time_minutes"] == 15


@pytest.mark.django_db
class TestPetFeedingReminderTask:
    """Test suite for send_pet_feeding_reminders task."""

    def test_finds_unfed_pets(self):
        """Test that task finds pets that haven't been fed today."""
        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        # Create pet without feeding activity today
        Pet.objects.create(
            family=family,
            name="Buddy",
            species=Pet.Species.DOG,
            created_by=user,
        )

        # Execute task
        result = send_pet_feeding_reminders()

        assert result["reminders_sent"] == 1

    def test_ignores_already_fed_pets(self):
        """Test that task ignores pets already fed today."""
        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        # Create pet
        pet = Pet.objects.create(
            family=family,
            name="Buddy",
            species=Pet.Species.DOG,
            created_by=user,
        )

        # Log feeding activity today
        PetActivity.objects.create(
            pet=pet,
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=timezone.now(),
            is_completed=True,
            completed_at=timezone.now(),
            completed_by=user,
            created_by=user,
        )

        # Execute task
        result = send_pet_feeding_reminders()

        assert result["reminders_sent"] == 0


@pytest.mark.django_db
class TestPetWalkingReminderTask:
    """Test suite for send_pet_walking_reminders task."""

    def test_finds_unwalked_dogs(self):
        """Test that task finds dogs that haven't been walked today."""
        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        # Create dog without walking activity today
        Pet.objects.create(
            family=family,
            name="Rex",
            species=Pet.Species.DOG,
            created_by=user,
        )

        # Execute task
        result = send_pet_walking_reminders()

        assert result["reminders_sent"] == 1

    def test_ignores_non_dogs(self):
        """Test that task only checks dogs (not cats, birds, etc)."""
        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        # Create cat (should be ignored)
        Pet.objects.create(
            family=family,
            name="Whiskers",
            species=Pet.Species.CAT,
            created_by=user,
        )

        # Execute task
        result = send_pet_walking_reminders()

        assert result["reminders_sent"] == 0


@pytest.mark.django_db
class TestCleanupTask:
    """Test suite for cleanup_old_soft_deleted_records task."""

    def test_deletes_old_soft_deleted_todos(self):
        """Test that task hard deletes old soft-deleted todos."""
        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        # Create todo and soft delete it 31 days ago
        old_delete_date = timezone.now() - timezone.timedelta(days=31)
        todo = Todo.objects.create(
            family=family,
            title="Old task",
            is_deleted=True,
            deleted_at=old_delete_date,
            created_by=user,
        )

        # Execute cleanup task
        result = cleanup_old_soft_deleted_records(days_old=30)

        assert result["todos"] >= 1

        # Verify todo is gone
        assert not Todo.objects.filter(id=todo.id).exists()

    def test_keeps_recent_soft_deleted_records(self):
        """Test that task keeps recently soft-deleted records."""
        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        # Create todo and soft delete it 10 days ago
        recent_delete_date = timezone.now() - timezone.timedelta(days=10)
        todo = Todo.objects.create(
            family=family,
            title="Recent task",
            is_deleted=True,
            deleted_at=recent_delete_date,
            created_by=user,
        )

        # Execute cleanup task
        cleanup_old_soft_deleted_records(days_old=30)

        # Verify todo still exists
        assert Todo.objects.filter(id=todo.id).exists()
