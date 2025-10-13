"""
Tests for PetActivity model
Following TDD discipline - Red-Green-Refactor

Testing FamApp pet activity tracking model.
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone

User = get_user_model()


@pytest.mark.django_db
class TestPetActivityModel:
    """Test PetActivity model"""

    def test_create_pet_activity_with_required_fields(self):
        """Test: Create pet activity with activity_type, scheduled_time, and pet"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()

        # Act
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=scheduled_time,
            pet=pet,
        )

        # Assert
        assert activity.id is not None
        assert activity.activity_type == PetActivity.ActivityType.FEEDING
        assert activity.scheduled_time == scheduled_time
        assert activity.pet == pet
        assert activity.public_id is not None

    def test_pet_activity_type_is_required(self):
        """Test: PetActivity activity_type is required"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()

        # Act & Assert
        with pytest.raises(IntegrityError):
            PetActivity.objects.create(
                activity_type=None, scheduled_time=scheduled_time, pet=pet,
            )

    def test_pet_activity_scheduled_time_is_required(self):
        """Test: PetActivity scheduled_time is required"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)

        # Act & Assert
        with pytest.raises(IntegrityError):
            PetActivity.objects.create(
                activity_type=PetActivity.ActivityType.FEEDING,
                scheduled_time=None,
                pet=pet,
            )

    def test_pet_activity_pet_is_required(self):
        """Test: PetActivity pet is required"""
        from apps.shared.models import PetActivity

        # Arrange
        scheduled_time = timezone.now()

        # Act & Assert
        with pytest.raises(IntegrityError):
            PetActivity.objects.create(
                activity_type=PetActivity.ActivityType.FEEDING,
                scheduled_time=scheduled_time,
                pet=None,
            )

    def test_pet_activity_type_enum_values(self):
        """Test: ActivityType enum has correct values"""
        from apps.shared.models import PetActivity

        # Assert
        assert hasattr(PetActivity, "ActivityType")
        assert hasattr(PetActivity.ActivityType, "FEEDING")
        assert hasattr(PetActivity.ActivityType, "WALKING")
        assert hasattr(PetActivity.ActivityType, "GROOMING")
        assert hasattr(PetActivity.ActivityType, "VET_VISIT")
        assert hasattr(PetActivity.ActivityType, "MEDICATION")
        assert hasattr(PetActivity.ActivityType, "PLAYTIME")
        assert hasattr(PetActivity.ActivityType, "OTHER")

    def test_pet_activity_type_feeding(self):
        """Test: Can create activity with FEEDING type"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()

        # Act
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=scheduled_time,
            pet=pet,
        )

        # Assert
        assert activity.activity_type == PetActivity.ActivityType.FEEDING

    def test_pet_activity_type_walking(self):
        """Test: Can create activity with WALKING type"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()

        # Act
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.WALKING,
            scheduled_time=scheduled_time,
            pet=pet,
        )

        # Assert
        assert activity.activity_type == PetActivity.ActivityType.WALKING

    def test_pet_activity_type_grooming(self):
        """Test: Can create activity with GROOMING type"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()

        # Act
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.GROOMING,
            scheduled_time=scheduled_time,
            pet=pet,
        )

        # Assert
        assert activity.activity_type == PetActivity.ActivityType.GROOMING

    def test_pet_activity_type_vet_visit(self):
        """Test: Can create activity with VET_VISIT type"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()

        # Act
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.VET_VISIT,
            scheduled_time=scheduled_time,
            pet=pet,
        )

        # Assert
        assert activity.activity_type == PetActivity.ActivityType.VET_VISIT

    def test_pet_activity_type_medication(self):
        """Test: Can create activity with MEDICATION type"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()

        # Act
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.MEDICATION,
            scheduled_time=scheduled_time,
            pet=pet,
        )

        # Assert
        assert activity.activity_type == PetActivity.ActivityType.MEDICATION

    def test_pet_activity_type_playtime(self):
        """Test: Can create activity with PLAYTIME type"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()

        # Act
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.PLAYTIME,
            scheduled_time=scheduled_time,
            pet=pet,
        )

        # Assert
        assert activity.activity_type == PetActivity.ActivityType.PLAYTIME

    def test_pet_activity_type_other(self):
        """Test: Can create activity with OTHER type"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()

        # Act
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.OTHER,
            scheduled_time=scheduled_time,
            pet=pet,
        )

        # Assert
        assert activity.activity_type == PetActivity.ActivityType.OTHER

    def test_pet_activity_notes_is_optional(self):
        """Test: PetActivity notes is optional"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()

        # Act
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=scheduled_time,
            pet=pet,
        )

        # Assert
        assert activity.notes is None or activity.notes == ""

    def test_pet_activity_with_notes(self):
        """Test: PetActivity can have notes"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()

        # Act
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.MEDICATION,
            scheduled_time=scheduled_time,
            pet=pet,
            notes="Give 1 pill with food",
        )

        # Assert
        assert activity.notes == "Give 1 pill with food"

    def test_pet_activity_is_completed_default_is_false(self):
        """Test: Default is_completed is False"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()

        # Act
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=scheduled_time,
            pet=pet,
        )

        # Assert
        assert activity.is_completed is False

    def test_pet_activity_can_be_marked_as_completed(self):
        """Test: PetActivity can be marked as completed"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()

        # Act
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=scheduled_time,
            pet=pet,
            is_completed=True,
        )

        # Assert
        assert activity.is_completed is True

    def test_pet_activity_completed_at_is_optional(self):
        """Test: PetActivity completed_at is optional"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()

        # Act
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=scheduled_time,
            pet=pet,
        )

        # Assert
        assert activity.completed_at is None

    def test_pet_activity_with_completed_at(self):
        """Test: PetActivity can have completed_at"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()
        completed_at = timezone.now()

        # Act
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=scheduled_time,
            pet=pet,
            is_completed=True,
            completed_at=completed_at,
        )

        # Assert
        assert activity.completed_at == completed_at

    def test_pet_activity_completed_by_is_optional(self):
        """Test: PetActivity completed_by is optional"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()

        # Act
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=scheduled_time,
            pet=pet,
        )

        # Assert
        assert activity.completed_by is None

    def test_pet_activity_with_completed_by(self, user):
        """Test: PetActivity can have completed_by user"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()

        # Act
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=scheduled_time,
            pet=pet,
            completed_by=user,
        )

        # Assert
        assert activity.completed_by == user

    def test_pet_activity_completed_by_uses_set_null_on_delete(self, user):
        """Test: completed_by uses SET_NULL when user is deleted"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=scheduled_time,
            pet=pet,
            completed_by=user,
        )
        assert activity.completed_by == user

        # Act
        user_id = user.id
        user.delete()

        # Assert
        activity.refresh_from_db()
        assert activity.completed_by is None

    def test_pet_activity_has_timestamps(self):
        """Test: PetActivity has created_at and updated_at (BaseModel)"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()

        # Act
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=scheduled_time,
            pet=pet,
        )

        # Assert
        assert activity.created_at is not None
        assert activity.updated_at is not None

    def test_pet_activity_has_audit_fields(self, user):
        """Test: PetActivity has created_by and updated_by (BaseModel)"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()

        # Act
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=scheduled_time,
            pet=pet,
            created_by=user,
        )

        # Assert
        assert hasattr(activity, "created_by")
        assert hasattr(activity, "updated_by")
        assert activity.created_by == user

    def test_pet_activity_has_soft_delete_fields(self):
        """Test: PetActivity has is_deleted, deleted_at, deleted_by (BaseModel)"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()

        # Act
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=scheduled_time,
            pet=pet,
        )

        # Assert
        assert hasattr(activity, "is_deleted")
        assert hasattr(activity, "deleted_at")
        assert hasattr(activity, "deleted_by")
        assert activity.is_deleted is False

    def test_pet_activity_can_be_soft_deleted(self, user):
        """Test: PetActivity can be soft deleted"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=scheduled_time,
            pet=pet,
        )

        # Act
        activity.soft_delete(user=user)

        # Assert
        activity.refresh_from_db()
        assert activity.is_deleted is True
        assert activity.deleted_at is not None
        assert activity.deleted_by == user

    def test_pet_activity_str_representation(self):
        """Test: PetActivity __str__ returns meaningful representation"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=scheduled_time,
            pet=pet,
        )

        # Act
        str_repr = str(activity)

        # Assert
        assert "Buddy" in str_repr or "Feeding" in str_repr

    def test_delete_pet_cascades_to_activities(self):
        """Test: Deleting pet hard-deletes all related PetActivities"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=scheduled_time,
            pet=pet,
        )
        activity_id = activity.id

        # Act
        pet.delete()

        # Assert
        # Activity should be hard deleted (CASCADE)
        assert not PetActivity.objects.filter(id=activity_id).exists()

    def test_pet_has_reverse_relationship_to_activities(self):
        """Test: Pet has reverse relationship to activities"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()
        PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=scheduled_time,
            pet=pet,
        )
        PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.WALKING,
            scheduled_time=scheduled_time + timezone.timedelta(hours=4),
            pet=pet,
        )

        # Act
        activities = pet.petactivity_set.all()

        # Assert
        assert activities.count() == 2

    def test_user_has_reverse_relationship_to_completed_activities(self, user):
        """Test: User has reverse relationship to completed activities"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()
        PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=scheduled_time,
            pet=pet,
            completed_by=user,
        )
        PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.WALKING,
            scheduled_time=scheduled_time + timezone.timedelta(hours=4),
            pet=pet,
            completed_by=user,
        )

        # Act
        completed_activities = user.petactivity_completed_by.all()

        # Assert
        assert completed_activities.count() == 2

    def test_pet_activity_is_completed_can_be_toggled(self):
        """Test: PetActivity is_completed can be toggled"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=scheduled_time,
            pet=pet,
        )
        assert activity.is_completed is False

        # Act
        activity.is_completed = True
        activity.save()

        # Assert
        activity.refresh_from_db()
        assert activity.is_completed is True

    def test_pet_activity_scheduled_time_can_be_updated(self):
        """Test: PetActivity scheduled_time can be updated"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=scheduled_time,
            pet=pet,
        )
        original_time = activity.scheduled_time

        # Act
        new_time = scheduled_time + timezone.timedelta(hours=2)
        activity.scheduled_time = new_time
        activity.save()

        # Assert
        activity.refresh_from_db()
        assert activity.scheduled_time == new_time
        assert activity.scheduled_time != original_time

    def test_multiple_activities_per_pet(self):
        """Test: Pet can have multiple activities"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()

        # Act
        PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.FEEDING,
            scheduled_time=scheduled_time,
            pet=pet,
        )
        PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.WALKING,
            scheduled_time=scheduled_time + timezone.timedelta(hours=4),
            pet=pet,
        )
        PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.MEDICATION,
            scheduled_time=scheduled_time + timezone.timedelta(hours=8),
            pet=pet,
        )

        # Assert
        assert pet.petactivity_set.count() == 3

    def test_pet_activity_with_all_fields(self, user):
        """Test: Create pet activity with all fields populated"""
        from apps.shared.models import Family
        from apps.shared.models import Pet
        from apps.shared.models import PetActivity

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        scheduled_time = timezone.now()
        completed_at = timezone.now()

        # Act
        activity = PetActivity.objects.create(
            activity_type=PetActivity.ActivityType.MEDICATION,
            scheduled_time=scheduled_time,
            notes="Give 1 pill with food",
            is_completed=True,
            completed_at=completed_at,
            completed_by=user,
            pet=pet,
            created_by=user,
        )

        # Assert
        assert activity.activity_type == PetActivity.ActivityType.MEDICATION
        assert activity.scheduled_time == scheduled_time
        assert activity.notes == "Give 1 pill with food"
        assert activity.is_completed is True
        assert activity.completed_at == completed_at
        assert activity.completed_by == user
        assert activity.pet == pet
        assert activity.created_by == user
