"""
Test module for ScheduleEvent ViewSet API endpoints.

Following TDD methodology (Red-Green-Refactor):
Tests for ScheduleEventViewSet CRUD operations with FamilyAccessMixin.

Ham Dog & TC building calendar APIs! 📅
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.shared.models import Family
from apps.shared.models import FamilyMember
from apps.shared.models import ScheduleEvent

User = get_user_model()


@pytest.mark.django_db
class TestListEvents:
    """Test suite for GET /api/v1/events/ - List events."""

    def test_returns_events_from_user_families_only(self):
        """Test that user only sees events from their families."""
        client = APIClient()

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

        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=2)

        event1 = ScheduleEvent.objects.create(
            family=family1,
            title="Event 1",
            start_time=start_time,
            end_time=end_time,
            created_by=user1,
            updated_by=user1,
        )
        ScheduleEvent.objects.create(
            family=family2,
            title="Event 2",
            start_time=start_time,
            end_time=end_time,
            created_by=user2,
            updated_by=user2,
        )

        client.force_authenticate(user=user1)
        response = client.get("/api/v1/events/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["public_id"] == str(event1.public_id)

    def test_excludes_soft_deleted_events(self):
        """Test that soft-deleted events are excluded."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=2)

        event = ScheduleEvent.objects.create(
            family=family,
            title="Test Event",
            start_time=start_time,
            end_time=end_time,
            created_by=user,
            updated_by=user,
        )

        # Soft delete
        event.is_deleted = True
        event.deleted_at = timezone.now()
        event.save()

        client.force_authenticate(user=user)
        response = client.get("/api/v1/events/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0


@pytest.mark.django_db
class TestCreateEvent:
    """Test suite for POST /api/v1/events/ - Create event."""

    def test_creates_event_with_required_fields(self):
        """Test creating event with required fields."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        start_time = timezone.now() + timezone.timedelta(days=1)
        end_time = start_time + timezone.timedelta(hours=2)

        client.force_authenticate(user=user)
        response = client.post(
            "/api/v1/events/",
            {
                "family_public_id": str(family.public_id),
                "title": "Team Meeting",
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "Team Meeting"
        assert "public_id" in response.data

    def test_creates_event_with_all_fields(self):
        """Test creating event with all optional fields."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        start_time = timezone.now() + timezone.timedelta(days=1)
        end_time = start_time + timezone.timedelta(hours=2)

        client.force_authenticate(user=user)
        response = client.post(
            "/api/v1/events/",
            {
                "family_public_id": str(family.public_id),
                "title": "Doctor Appointment",
                "description": "Annual checkup",
                "location": "123 Main St",
                "event_type": ScheduleEvent.EventType.APPOINTMENT,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "assigned_to_public_id": str(user.public_id),
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "Doctor Appointment"
        assert response.data["event_type"] == ScheduleEvent.EventType.APPOINTMENT

    def test_returns_400_if_start_after_end(self):
        """Test that start_time must be before end_time."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        start_time = timezone.now() + timezone.timedelta(days=1)
        end_time = start_time - timezone.timedelta(hours=2)  # End before start!

        client.force_authenticate(user=user)
        response = client.post(
            "/api/v1/events/",
            {
                "family_public_id": str(family.public_id),
                "title": "Invalid Event",
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestRetrieveEvent:
    """Test suite for GET /api/v1/events/{public_id}/ - Retrieve event."""

    def test_returns_event_details(self):
        """Test retrieving event details."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=2)

        event = ScheduleEvent.objects.create(
            family=family,
            title="Test Event",
            start_time=start_time,
            end_time=end_time,
            created_by=user,
            updated_by=user,
        )

        client.force_authenticate(user=user)
        response = client.get(f"/api/v1/events/{event.public_id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Test Event"

    def test_returns_404_if_event_not_in_user_families(self):
        """Test that user cannot access events from other families."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )
        owner = User.objects.create_user(
            email="owner@example.com", password="testpass123",
        )

        family = Family.objects.create(name="Test Family", created_by=owner)
        FamilyMember.objects.create(
            family=family, user=owner, role=FamilyMember.Role.ORGANIZER,
        )

        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=2)

        event = ScheduleEvent.objects.create(
            family=family,
            title="Test Event",
            start_time=start_time,
            end_time=end_time,
            created_by=owner,
            updated_by=owner,
        )

        client.force_authenticate(user=user)
        response = client.get(f"/api/v1/events/{event.public_id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestUpdateEvent:
    """Test suite for PATCH /api/v1/events/{public_id}/ - Update event."""

    def test_updates_event_fields(self):
        """Test updating event fields."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=2)

        event = ScheduleEvent.objects.create(
            family=family,
            title="Original Title",
            start_time=start_time,
            end_time=end_time,
            created_by=user,
            updated_by=user,
        )

        client.force_authenticate(user=user)
        response = client.patch(
            f"/api/v1/events/{event.public_id}/",
            {
                "title": "Updated Title",
                "location": "New Location",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated Title"
        assert response.data["location"] == "New Location"

    def test_allows_partial_updates(self):
        """Test that partial updates work."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=2)

        event = ScheduleEvent.objects.create(
            family=family,
            title="Original Title",
            description="Original description",
            start_time=start_time,
            end_time=end_time,
            created_by=user,
            updated_by=user,
        )

        client.force_authenticate(user=user)
        response = client.patch(
            f"/api/v1/events/{event.public_id}/",
            {"title": "Updated Title"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated Title"
        assert response.data["description"] == "Original description"


@pytest.mark.django_db
class TestDeleteEvent:
    """Test suite for DELETE /api/v1/events/{public_id}/ - Soft delete event."""

    def test_soft_deletes_event(self):
        """Test that delete soft-deletes the event."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=2)

        event = ScheduleEvent.objects.create(
            family=family,
            title="Test Event",
            start_time=start_time,
            end_time=end_time,
            created_by=user,
            updated_by=user,
        )

        client.force_authenticate(user=user)
        response = client.delete(f"/api/v1/events/{event.public_id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify soft delete
        event.refresh_from_db()
        assert event.is_deleted is True
        assert event.deleted_at is not None

    def test_soft_deleted_event_not_in_list(self):
        """Test that soft-deleted events don't appear in list."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=2)

        event = ScheduleEvent.objects.create(
            family=family,
            title="Test Event",
            start_time=start_time,
            end_time=end_time,
            created_by=user,
            updated_by=user,
        )

        client.force_authenticate(user=user)

        # Delete the event
        response = client.delete(f"/api/v1/events/{event.public_id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # List should be empty
        response = client.get("/api/v1/events/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0
