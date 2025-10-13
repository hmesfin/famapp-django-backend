"""
Tests for ScheduleEvent model
Following TDD discipline - Red-Green-Refactor

Testing FamApp schedule/calendar event management model.
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone

User = get_user_model()


@pytest.mark.django_db
class TestScheduleEventModel:
    """Test ScheduleEvent model"""

    def test_create_schedule_event_with_required_fields(self):
        """Test: Create schedule event with title, start_time, end_time, and family"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)

        # Act
        event = ScheduleEvent.objects.create(
            title="Doctor Appointment", family=family, start_time=start_time, end_time=end_time
        )

        # Assert
        assert event.id is not None
        assert event.title == "Doctor Appointment"
        assert event.family == family
        assert event.start_time == start_time
        assert event.end_time == end_time
        assert event.public_id is not None

    def test_schedule_event_title_is_required(self):
        """Test: ScheduleEvent title is required"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)

        # Act & Assert
        with pytest.raises(IntegrityError):
            ScheduleEvent.objects.create(
                title=None, family=family, start_time=start_time, end_time=end_time
            )

    def test_schedule_event_title_max_length_200(self):
        """Test: ScheduleEvent title max length is 200 characters"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        long_title = "A" * 201
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)

        # Act & Assert
        with pytest.raises(Exception):  # ValidationError or DataError
            ScheduleEvent.objects.create(
                title=long_title, family=family, start_time=start_time, end_time=end_time
            )

    def test_schedule_event_family_is_required(self):
        """Test: ScheduleEvent family is required"""
        from apps.shared.models import ScheduleEvent

        # Arrange
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)

        # Act & Assert
        with pytest.raises(IntegrityError):
            ScheduleEvent.objects.create(
                title="Doctor Appointment", family=None, start_time=start_time, end_time=end_time
            )

    def test_schedule_event_start_time_is_required(self):
        """Test: ScheduleEvent start_time is required"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        end_time = timezone.now()

        # Act & Assert
        with pytest.raises(IntegrityError):
            ScheduleEvent.objects.create(
                title="Doctor Appointment", family=family, start_time=None, end_time=end_time
            )

    def test_schedule_event_end_time_is_required(self):
        """Test: ScheduleEvent end_time is required"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()

        # Act & Assert
        with pytest.raises(IntegrityError):
            ScheduleEvent.objects.create(
                title="Doctor Appointment", family=family, start_time=start_time, end_time=None
            )

    def test_schedule_event_description_is_optional(self):
        """Test: ScheduleEvent description is optional"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)

        # Act
        event = ScheduleEvent.objects.create(
            title="Doctor Appointment", family=family, start_time=start_time, end_time=end_time
        )

        # Assert
        assert event.description is None or event.description == ""

    def test_schedule_event_with_description(self):
        """Test: ScheduleEvent can have description"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)

        # Act
        event = ScheduleEvent.objects.create(
            title="Doctor Appointment",
            description="Annual checkup at Dr. Smith's office",
            family=family,
            start_time=start_time,
            end_time=end_time,
        )

        # Assert
        assert event.description == "Annual checkup at Dr. Smith's office"

    def test_schedule_event_type_enum_values(self):
        """Test: EventType enum has correct values (APPOINTMENT, MEETING, REMINDER, OTHER)"""
        from apps.shared.models import ScheduleEvent

        # Assert
        assert hasattr(ScheduleEvent, "EventType")
        assert hasattr(ScheduleEvent.EventType, "APPOINTMENT")
        assert hasattr(ScheduleEvent.EventType, "MEETING")
        assert hasattr(ScheduleEvent.EventType, "REMINDER")
        assert hasattr(ScheduleEvent.EventType, "OTHER")

    def test_schedule_event_default_type_is_other(self):
        """Test: Default event_type is OTHER"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)

        # Act
        event = ScheduleEvent.objects.create(
            title="Doctor Appointment", family=family, start_time=start_time, end_time=end_time
        )

        # Assert
        assert event.event_type == ScheduleEvent.EventType.OTHER

    def test_schedule_event_type_can_be_appointment(self):
        """Test: Can create event with APPOINTMENT type"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)

        # Act
        event = ScheduleEvent.objects.create(
            title="Doctor Appointment",
            family=family,
            start_time=start_time,
            end_time=end_time,
            event_type=ScheduleEvent.EventType.APPOINTMENT,
        )

        # Assert
        assert event.event_type == ScheduleEvent.EventType.APPOINTMENT

    def test_schedule_event_type_can_be_meeting(self):
        """Test: Can create event with MEETING type"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)

        # Act
        event = ScheduleEvent.objects.create(
            title="Team Meeting",
            family=family,
            start_time=start_time,
            end_time=end_time,
            event_type=ScheduleEvent.EventType.MEETING,
        )

        # Assert
        assert event.event_type == ScheduleEvent.EventType.MEETING

    def test_schedule_event_type_can_be_reminder(self):
        """Test: Can create event with REMINDER type"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)

        # Act
        event = ScheduleEvent.objects.create(
            title="Take Medication",
            family=family,
            start_time=start_time,
            end_time=end_time,
            event_type=ScheduleEvent.EventType.REMINDER,
        )

        # Assert
        assert event.event_type == ScheduleEvent.EventType.REMINDER

    def test_schedule_event_location_is_optional(self):
        """Test: ScheduleEvent location is optional"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)

        # Act
        event = ScheduleEvent.objects.create(
            title="Doctor Appointment", family=family, start_time=start_time, end_time=end_time
        )

        # Assert
        assert event.location is None or event.location == ""

    def test_schedule_event_with_location(self):
        """Test: ScheduleEvent can have location"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)

        # Act
        event = ScheduleEvent.objects.create(
            title="Doctor Appointment",
            location="123 Main St, Suite 200",
            family=family,
            start_time=start_time,
            end_time=end_time,
        )

        # Assert
        assert event.location == "123 Main St, Suite 200"

    def test_schedule_event_location_max_length_255(self):
        """Test: ScheduleEvent location max length is 255 characters"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        long_location = "A" * 256
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)

        # Act & Assert
        with pytest.raises(Exception):  # ValidationError or DataError
            ScheduleEvent.objects.create(
                title="Doctor Appointment",
                location=long_location,
                family=family,
                start_time=start_time,
                end_time=end_time,
            )

    def test_schedule_event_assigned_to_is_optional(self):
        """Test: ScheduleEvent assigned_to is optional"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)

        # Act
        event = ScheduleEvent.objects.create(
            title="Doctor Appointment", family=family, start_time=start_time, end_time=end_time
        )

        # Assert
        assert event.assigned_to is None

    def test_schedule_event_with_assigned_to(self, user):
        """Test: ScheduleEvent can be assigned to a user"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)

        # Act
        event = ScheduleEvent.objects.create(
            title="Doctor Appointment",
            family=family,
            start_time=start_time,
            end_time=end_time,
            assigned_to=user,
        )

        # Assert
        assert event.assigned_to == user

    def test_schedule_event_assigned_to_uses_set_null_on_delete(self, user):
        """Test: assigned_to uses SET_NULL when user is deleted"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)
        event = ScheduleEvent.objects.create(
            title="Doctor Appointment",
            family=family,
            start_time=start_time,
            end_time=end_time,
            assigned_to=user,
        )
        assert event.assigned_to == user

        # Act
        user_id = user.id
        user.delete()

        # Assert
        event.refresh_from_db()
        assert event.assigned_to is None

    def test_schedule_event_has_timestamps(self):
        """Test: ScheduleEvent has created_at and updated_at (BaseModel)"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)

        # Act
        event = ScheduleEvent.objects.create(
            title="Doctor Appointment", family=family, start_time=start_time, end_time=end_time
        )

        # Assert
        assert event.created_at is not None
        assert event.updated_at is not None

    def test_schedule_event_has_audit_fields(self, user):
        """Test: ScheduleEvent has created_by and updated_by (BaseModel)"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)

        # Act
        event = ScheduleEvent.objects.create(
            title="Doctor Appointment",
            family=family,
            start_time=start_time,
            end_time=end_time,
            created_by=user,
        )

        # Assert
        assert hasattr(event, "created_by")
        assert hasattr(event, "updated_by")
        assert event.created_by == user

    def test_schedule_event_has_soft_delete_fields(self):
        """Test: ScheduleEvent has is_deleted, deleted_at, deleted_by (BaseModel)"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)

        # Act
        event = ScheduleEvent.objects.create(
            title="Doctor Appointment", family=family, start_time=start_time, end_time=end_time
        )

        # Assert
        assert hasattr(event, "is_deleted")
        assert hasattr(event, "deleted_at")
        assert hasattr(event, "deleted_by")
        assert event.is_deleted is False

    def test_schedule_event_can_be_soft_deleted(self, user):
        """Test: ScheduleEvent can be soft deleted"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)
        event = ScheduleEvent.objects.create(
            title="Doctor Appointment", family=family, start_time=start_time, end_time=end_time
        )

        # Act
        event.soft_delete(user=user)

        # Assert
        event.refresh_from_db()
        assert event.is_deleted is True
        assert event.deleted_at is not None
        assert event.deleted_by == user

    def test_schedule_event_str_representation(self):
        """Test: ScheduleEvent __str__ returns meaningful representation"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)
        event = ScheduleEvent.objects.create(
            title="Doctor Appointment", family=family, start_time=start_time, end_time=end_time
        )

        # Act
        str_repr = str(event)

        # Assert
        assert "Doctor Appointment" in str_repr

    def test_delete_family_cascades_to_schedule_events(self):
        """Test: Deleting family hard-deletes all related ScheduleEvents"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)
        event = ScheduleEvent.objects.create(
            title="Doctor Appointment", family=family, start_time=start_time, end_time=end_time
        )
        event_id = event.id

        # Act
        family.delete()

        # Assert
        # Event should be hard deleted (CASCADE)
        assert not ScheduleEvent.objects.filter(id=event_id).exists()

    def test_family_has_reverse_relationship_to_schedule_events(self):
        """Test: Family has reverse relationship to schedule events"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)
        ScheduleEvent.objects.create(
            title="Doctor Appointment", family=family, start_time=start_time, end_time=end_time
        )
        ScheduleEvent.objects.create(
            title="Dentist Appointment",
            family=family,
            start_time=start_time + timezone.timedelta(days=1),
            end_time=end_time + timezone.timedelta(days=1),
        )

        # Act
        events = family.scheduleevent_set.all()

        # Assert
        assert events.count() == 2

    def test_user_has_reverse_relationship_to_assigned_schedule_events(self, user):
        """Test: User has reverse relationship to assigned schedule events"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)
        ScheduleEvent.objects.create(
            title="Doctor Appointment",
            family=family,
            start_time=start_time,
            end_time=end_time,
            assigned_to=user,
        )
        ScheduleEvent.objects.create(
            title="Dentist Appointment",
            family=family,
            start_time=start_time + timezone.timedelta(days=1),
            end_time=end_time + timezone.timedelta(days=1),
            assigned_to=user,
        )

        # Act
        assigned_events = user.scheduleevent_assigned_to.all()

        # Assert
        assert assigned_events.count() == 2

    def test_schedule_event_event_type_can_be_updated(self):
        """Test: ScheduleEvent event_type can be updated"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)
        event = ScheduleEvent.objects.create(
            title="Doctor Appointment", family=family, start_time=start_time, end_time=end_time
        )
        assert event.event_type == ScheduleEvent.EventType.OTHER

        # Act
        event.event_type = ScheduleEvent.EventType.APPOINTMENT
        event.save()

        # Assert
        event.refresh_from_db()
        assert event.event_type == ScheduleEvent.EventType.APPOINTMENT

    def test_schedule_event_times_can_be_updated(self):
        """Test: ScheduleEvent start_time and end_time can be updated"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)
        event = ScheduleEvent.objects.create(
            title="Doctor Appointment", family=family, start_time=start_time, end_time=end_time
        )
        original_start = event.start_time
        original_end = event.end_time

        # Act
        new_start = start_time + timezone.timedelta(days=1)
        new_end = end_time + timezone.timedelta(days=1)
        event.start_time = new_start
        event.end_time = new_end
        event.save()

        # Assert
        event.refresh_from_db()
        assert event.start_time == new_start
        assert event.end_time == new_end
        assert event.start_time != original_start
        assert event.end_time != original_end

    def test_multiple_schedule_events_per_family(self):
        """Test: Family can have multiple schedule events"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)

        # Act
        ScheduleEvent.objects.create(
            title="Doctor Appointment", family=family, start_time=start_time, end_time=end_time
        )
        ScheduleEvent.objects.create(
            title="Dentist Appointment",
            family=family,
            start_time=start_time + timezone.timedelta(days=1),
            end_time=end_time + timezone.timedelta(days=1),
        )
        ScheduleEvent.objects.create(
            title="School Meeting",
            family=family,
            start_time=start_time + timezone.timedelta(days=2),
            end_time=end_time + timezone.timedelta(days=2),
        )

        # Assert
        assert family.scheduleevent_set.count() == 3

    def test_user_can_have_multiple_assigned_schedule_events(self, user):
        """Test: User can be assigned multiple schedule events"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)

        # Act
        ScheduleEvent.objects.create(
            title="Doctor Appointment",
            family=family,
            start_time=start_time,
            end_time=end_time,
            assigned_to=user,
        )
        ScheduleEvent.objects.create(
            title="Dentist Appointment",
            family=family,
            start_time=start_time + timezone.timedelta(days=1),
            end_time=end_time + timezone.timedelta(days=1),
            assigned_to=user,
        )

        # Assert
        assert user.scheduleevent_assigned_to.count() == 2

    def test_schedule_event_with_all_fields(self, user):
        """Test: Create schedule event with all fields populated"""
        from apps.shared.models import Family, ScheduleEvent

        # Arrange
        family = Family.objects.create(name="Smith Family")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=1)

        # Act
        event = ScheduleEvent.objects.create(
            title="Doctor Appointment",
            description="Annual checkup at Dr. Smith's office",
            event_type=ScheduleEvent.EventType.APPOINTMENT,
            start_time=start_time,
            end_time=end_time,
            location="123 Main St, Suite 200",
            assigned_to=user,
            family=family,
            created_by=user,
        )

        # Assert
        assert event.title == "Doctor Appointment"
        assert event.description == "Annual checkup at Dr. Smith's office"
        assert event.event_type == ScheduleEvent.EventType.APPOINTMENT
        assert event.start_time == start_time
        assert event.end_time == end_time
        assert event.location == "123 Main St, Suite 200"
        assert event.assigned_to == user
        assert event.family == family
        assert event.created_by == user
