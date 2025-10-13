"""
Test module for Pet ViewSet API endpoints.

Following TDD methodology (Red-Green-Refactor):
Tests for PetViewSet CRUD operations with FamilyAccessMixin,
plus custom actions for PetActivity logging.

Ham Dog & TC building pet care APIs! 🐕🐈
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.shared.models import Family
from apps.shared.models import FamilyMember
from apps.shared.models import Pet
from apps.shared.models import PetActivity

User = get_user_model()


@pytest.mark.django_db
class TestListPets:
    """Test suite for GET /api/v1/pets/ - List pets."""

    def test_returns_pets_from_user_families_only(self):
        """Test that user only sees pets from their families."""
        client = APIClient()

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

        pet1 = Pet.objects.create(
            family=family1,
            name="Buddy",
            species=Pet.Species.DOG,
            created_by=user1,
        )
        Pet.objects.create(
            family=family2,
            name="Whiskers",
            species=Pet.Species.CAT,
            created_by=user2,
        )

        client.force_authenticate(user=user1)
        response = client.get("/api/v1/pets/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["public_id"] == str(pet1.public_id)

    def test_excludes_soft_deleted_pets(self):
        """Test that soft-deleted pets are excluded."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        pet = Pet.objects.create(
            family=family,
            name="Rex",
            species=Pet.Species.DOG,
            created_by=user,
        )

        # Soft delete
        pet.is_deleted = True
        pet.deleted_at = timezone.now()
        pet.save()

        client.force_authenticate(user=user)
        response = client.get("/api/v1/pets/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0


@pytest.mark.django_db
class TestCreatePet:
    """Test suite for POST /api/v1/pets/ - Create pet."""

    def test_creates_pet_with_required_fields(self):
        """Test creating pet with only required fields."""
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
            "/api/v1/pets/",
            {
                "family_public_id": str(family.public_id),
                "name": "Buddy",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Buddy"
        assert "public_id" in response.data
        assert response.data["species"] == Pet.Species.OTHER  # Default

    def test_creates_pet_with_all_fields(self):
        """Test creating pet with all optional fields."""
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
            "/api/v1/pets/",
            {
                "family_public_id": str(family.public_id),
                "name": "Rex",
                "species": Pet.Species.DOG,
                "breed": "Golden Retriever",
                "age": 3,
                "notes": "Very friendly dog",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Rex"
        assert response.data["species"] == Pet.Species.DOG
        assert response.data["breed"] == "Golden Retriever"
        assert response.data["age"] == 3
        assert response.data["notes"] == "Very friendly dog"

    def test_returns_400_if_name_empty(self):
        """Test that name cannot be empty."""
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
            "/api/v1/pets/",
            {
                "family_public_id": str(family.public_id),
                "name": "",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestRetrievePet:
    """Test suite for GET /api/v1/pets/{public_id}/ - Retrieve pet."""

    def test_returns_pet_details(self):
        """Test retrieving pet details."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        pet = Pet.objects.create(
            family=family,
            name="Buddy",
            species=Pet.Species.DOG,
            created_by=user,
        )

        client.force_authenticate(user=user)
        response = client.get(f"/api/v1/pets/{pet.public_id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Buddy"

    def test_returns_404_if_pet_not_in_user_families(self):
        """Test that user cannot access pets from other families."""
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

        pet = Pet.objects.create(
            family=family,
            name="Max",
            species=Pet.Species.DOG,
            created_by=owner,
        )

        client.force_authenticate(user=user)
        response = client.get(f"/api/v1/pets/{pet.public_id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestUpdatePet:
    """Test suite for PATCH /api/v1/pets/{public_id}/ - Update pet."""

    def test_updates_pet_fields(self):
        """Test updating pet fields."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        pet = Pet.objects.create(
            family=family,
            name="Buddy",
            species=Pet.Species.DOG,
            created_by=user,
        )

        client.force_authenticate(user=user)
        response = client.patch(
            f"/api/v1/pets/{pet.public_id}/",
            {
                "name": "Buddy Jr.",
                "age": 5,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Buddy Jr."
        assert response.data["age"] == 5

    def test_allows_partial_updates(self):
        """Test that partial updates work."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        pet = Pet.objects.create(
            family=family,
            name="Rex",
            species=Pet.Species.DOG,
            age=2,
            created_by=user,
        )

        client.force_authenticate(user=user)
        response = client.patch(
            f"/api/v1/pets/{pet.public_id}/",
            {"notes": "Good boy!"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["notes"] == "Good boy!"
        assert response.data["age"] == 2  # Unchanged


@pytest.mark.django_db
class TestDeletePet:
    """Test suite for DELETE /api/v1/pets/{public_id}/ - Soft delete pet."""

    def test_soft_deletes_pet(self):
        """Test that delete soft-deletes the pet."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        pet = Pet.objects.create(
            family=family,
            name="Buddy",
            species=Pet.Species.DOG,
            created_by=user,
        )

        client.force_authenticate(user=user)
        response = client.delete(f"/api/v1/pets/{pet.public_id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify soft delete
        pet.refresh_from_db()
        assert pet.is_deleted is True
        assert pet.deleted_at is not None

    def test_soft_deleted_pet_not_in_list(self):
        """Test that soft-deleted pets don't appear in list."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        pet = Pet.objects.create(
            family=family,
            name="Buddy",
            species=Pet.Species.DOG,
            created_by=user,
        )

        client.force_authenticate(user=user)

        # Delete the pet
        response = client.delete(f"/api/v1/pets/{pet.public_id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # List should be empty
        response = client.get("/api/v1/pets/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0


@pytest.mark.django_db
class TestLogPetActivity:
    """Test suite for POST /api/v1/pets/{public_id}/activities/ - Log activity."""

    def test_logs_feeding_activity(self):
        """Test logging a feeding activity."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        pet = Pet.objects.create(
            family=family,
            name="Buddy",
            species=Pet.Species.DOG,
            created_by=user,
        )

        client.force_authenticate(user=user)
        response = client.post(
            f"/api/v1/pets/{pet.public_id}/activities/",
            {
                "activity_type": PetActivity.ActivityType.FEEDING,
                "scheduled_time": timezone.now().isoformat(),
                "notes": "Fed breakfast",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["activity_type"] == PetActivity.ActivityType.FEEDING
        assert response.data["notes"] == "Fed breakfast"
        assert response.data["is_completed"] is False  # Default

    def test_logs_walking_activity(self):
        """Test logging a walking activity."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        pet = Pet.objects.create(
            family=family,
            name="Rex",
            species=Pet.Species.DOG,
            created_by=user,
        )

        client.force_authenticate(user=user)
        response = client.post(
            f"/api/v1/pets/{pet.public_id}/activities/",
            {
                "activity_type": PetActivity.ActivityType.WALKING,
                "scheduled_time": timezone.now().isoformat(),
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["activity_type"] == PetActivity.ActivityType.WALKING

    def test_sets_completed_by_to_current_user(self):
        """Test that completed_by is set to current user when is_completed=True."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        pet = Pet.objects.create(
            family=family,
            name="Buddy",
            species=Pet.Species.DOG,
            created_by=user,
        )

        client.force_authenticate(user=user)
        response = client.post(
            f"/api/v1/pets/{pet.public_id}/activities/",
            {
                "activity_type": PetActivity.ActivityType.FEEDING,
                "scheduled_time": timezone.now().isoformat(),
                "is_completed": True,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["is_completed"] is True
        assert "completed_by" in response.data

    def test_returns_404_if_pet_not_in_user_families(self):
        """Test that user cannot log activities for other families' pets."""
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

        pet = Pet.objects.create(
            family=family,
            name="Max",
            species=Pet.Species.DOG,
            created_by=owner,
        )

        client.force_authenticate(user=user)
        response = client.post(
            f"/api/v1/pets/{pet.public_id}/activities/",
            {
                "activity_type": PetActivity.ActivityType.FEEDING,
                "scheduled_time": timezone.now().isoformat(),
            },
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestListPetActivities:
    """Test suite for GET /api/v1/pets/{public_id}/activities/ - List activities."""

    def test_returns_activities_for_pet(self):
        """Test retrieving activities for a specific pet."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        pet = Pet.objects.create(
            family=family,
            name="Buddy",
            species=Pet.Species.DOG,
            created_by=user,
        )

        activity1 = PetActivity.objects.create(
            pet=pet,
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=timezone.now(),
            created_by=user,
        )
        activity2 = PetActivity.objects.create(
            pet=pet,
            activity_type=PetActivity.ActivityType.WALKING,
            scheduled_time=timezone.now(),
            created_by=user,
        )

        client.force_authenticate(user=user)
        response = client.get(f"/api/v1/pets/{pet.public_id}/activities/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        activity_ids = [act["public_id"] for act in response.data]
        assert str(activity1.public_id) in activity_ids
        assert str(activity2.public_id) in activity_ids

    def test_filters_by_activity_type(self):
        """Test filtering activities by type (query param)."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        pet = Pet.objects.create(
            family=family,
            name="Buddy",
            species=Pet.Species.DOG,
            created_by=user,
        )

        PetActivity.objects.create(
            pet=pet,
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=timezone.now(),
            created_by=user,
        )
        walking_activity = PetActivity.objects.create(
            pet=pet,
            activity_type=PetActivity.ActivityType.WALKING,
            scheduled_time=timezone.now(),
            created_by=user,
        )

        client.force_authenticate(user=user)
        response = client.get(
            f"/api/v1/pets/{pet.public_id}/activities/?activity_type=WALKING"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["public_id"] == str(walking_activity.public_id)

    def test_limits_to_recent_activities(self):
        """Test limiting activities with ?limit=N query param."""
        client = APIClient()

        user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER
        )

        pet = Pet.objects.create(
            family=family,
            name="Buddy",
            species=Pet.Species.DOG,
            created_by=user,
        )

        # Create 5 activities
        for i in range(5):
            PetActivity.objects.create(
                pet=pet,
                activity_type=PetActivity.ActivityType.FEEDING,
                scheduled_time=timezone.now(),
                created_by=user,
            )

        client.force_authenticate(user=user)
        response = client.get(f"/api/v1/pets/{pet.public_id}/activities/?limit=2")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_returns_404_if_pet_not_in_user_families(self):
        """Test that user cannot list activities for other families' pets."""
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

        pet = Pet.objects.create(
            family=family,
            name="Max",
            species=Pet.Species.DOG,
            created_by=owner,
        )

        client.force_authenticate(user=user)
        response = client.get(f"/api/v1/pets/{pet.public_id}/activities/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
