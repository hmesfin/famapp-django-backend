"""
Tests for Pet model
Following TDD discipline - Red-Green-Refactor

Testing FamApp pet management model.
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


@pytest.mark.django_db
class TestPetModel:
    """Test Pet model"""

    def test_create_pet_with_required_fields(self):
        """Test: Create pet with name and family"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        pet = Pet.objects.create(name="Buddy", family=family)

        # Assert
        assert pet.id is not None
        assert pet.name == "Buddy"
        assert pet.family == family
        assert pet.public_id is not None

    def test_pet_name_is_required(self):
        """Test: Pet name is required"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act & Assert
        with pytest.raises(IntegrityError):
            Pet.objects.create(name=None, family=family)

    def test_pet_name_max_length_100(self):
        """Test: Pet name max length is 100 characters"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")
        long_name = "A" * 101

        # Act & Assert
        with pytest.raises(Exception):  # ValidationError or DataError
            Pet.objects.create(name=long_name, family=family)

    def test_pet_family_is_required(self):
        """Test: Pet family is required"""
        from apps.shared.models import Pet

        # Act & Assert
        with pytest.raises(IntegrityError):
            Pet.objects.create(name="Buddy", family=None)

    def test_pet_species_enum_values(self):
        """Test: Species enum has correct values (DOG, CAT, BIRD, FISH, OTHER)"""
        from apps.shared.models import Pet

        # Assert
        assert hasattr(Pet, "Species")
        assert hasattr(Pet.Species, "DOG")
        assert hasattr(Pet.Species, "CAT")
        assert hasattr(Pet.Species, "BIRD")
        assert hasattr(Pet.Species, "FISH")
        assert hasattr(Pet.Species, "OTHER")

    def test_pet_default_species_is_other(self):
        """Test: Default species is OTHER"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        pet = Pet.objects.create(name="Buddy", family=family)

        # Assert
        assert pet.species == Pet.Species.OTHER

    def test_pet_species_can_be_dog(self):
        """Test: Can create pet with DOG species"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        pet = Pet.objects.create(name="Buddy", family=family, species=Pet.Species.DOG)

        # Assert
        assert pet.species == Pet.Species.DOG

    def test_pet_species_can_be_cat(self):
        """Test: Can create pet with CAT species"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        pet = Pet.objects.create(
            name="Whiskers", family=family, species=Pet.Species.CAT
        )

        # Assert
        assert pet.species == Pet.Species.CAT

    def test_pet_species_can_be_bird(self):
        """Test: Can create pet with BIRD species"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        pet = Pet.objects.create(name="Tweety", family=family, species=Pet.Species.BIRD)

        # Assert
        assert pet.species == Pet.Species.BIRD

    def test_pet_species_can_be_fish(self):
        """Test: Can create pet with FISH species"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        pet = Pet.objects.create(name="Nemo", family=family, species=Pet.Species.FISH)

        # Assert
        assert pet.species == Pet.Species.FISH

    def test_pet_breed_is_optional(self):
        """Test: Pet breed is optional"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        pet = Pet.objects.create(name="Buddy", family=family)

        # Assert
        assert pet.breed is None or pet.breed == ""

    def test_pet_with_breed(self):
        """Test: Pet can have breed"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        pet = Pet.objects.create(
            name="Buddy",
            family=family,
            species=Pet.Species.DOG,
            breed="Golden Retriever",
        )

        # Assert
        assert pet.breed == "Golden Retriever"

    def test_pet_breed_max_length_100(self):
        """Test: Pet breed max length is 100 characters"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")
        long_breed = "A" * 101

        # Act & Assert
        with pytest.raises(Exception):  # ValidationError or DataError
            Pet.objects.create(name="Buddy", family=family, breed=long_breed)

    def test_pet_age_is_optional(self):
        """Test: Pet age is optional"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        pet = Pet.objects.create(name="Buddy", family=family)

        # Assert
        assert pet.age is None

    def test_pet_with_age(self):
        """Test: Pet can have age"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        pet = Pet.objects.create(name="Buddy", family=family, age=5)

        # Assert
        assert pet.age == 5

    def test_pet_notes_is_optional(self):
        """Test: Pet notes is optional"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        pet = Pet.objects.create(name="Buddy", family=family)

        # Assert
        assert pet.notes is None or pet.notes == ""

    def test_pet_with_notes(self):
        """Test: Pet can have notes"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        pet = Pet.objects.create(
            name="Buddy", family=family, notes="Allergic to chicken, needs daily walks"
        )

        # Assert
        assert pet.notes == "Allergic to chicken, needs daily walks"

    def test_pet_has_timestamps(self):
        """Test: Pet has created_at and updated_at (BaseModel)"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        pet = Pet.objects.create(name="Buddy", family=family)

        # Assert
        assert pet.created_at is not None
        assert pet.updated_at is not None

    def test_pet_has_audit_fields(self, user):
        """Test: Pet has created_by and updated_by (BaseModel)"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        pet = Pet.objects.create(name="Buddy", family=family, created_by=user)

        # Assert
        assert hasattr(pet, "created_by")
        assert hasattr(pet, "updated_by")
        assert pet.created_by == user

    def test_pet_has_soft_delete_fields(self):
        """Test: Pet has is_deleted, deleted_at, deleted_by (BaseModel)"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        pet = Pet.objects.create(name="Buddy", family=family)

        # Assert
        assert hasattr(pet, "is_deleted")
        assert hasattr(pet, "deleted_at")
        assert hasattr(pet, "deleted_by")
        assert pet.is_deleted is False

    def test_pet_can_be_soft_deleted(self, user):
        """Test: Pet can be soft deleted"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)

        # Act
        pet.soft_delete(user=user)

        # Assert
        pet.refresh_from_db()
        assert pet.is_deleted is True
        assert pet.deleted_at is not None
        assert pet.deleted_by == user

    def test_pet_str_representation(self):
        """Test: Pet __str__ returns meaningful representation"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)

        # Act
        str_repr = str(pet)

        # Assert
        assert "Buddy" in str_repr

    def test_delete_family_cascades_to_pets(self):
        """Test: Deleting family hard-deletes all related Pets"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        pet_id = pet.id

        # Act
        family.delete()

        # Assert
        # Pet should be hard deleted (CASCADE)
        assert not Pet.objects.filter(id=pet_id).exists()

    def test_family_has_reverse_relationship_to_pets(self):
        """Test: Family has reverse relationship to pets"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")
        Pet.objects.create(name="Buddy", family=family, species=Pet.Species.DOG)
        Pet.objects.create(name="Whiskers", family=family, species=Pet.Species.CAT)

        # Act
        pets = family.pet_set.all()

        # Assert
        assert pets.count() == 2

    def test_pet_species_can_be_updated(self):
        """Test: Pet species can be updated"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family)
        assert pet.species == Pet.Species.OTHER

        # Act
        pet.species = Pet.Species.DOG
        pet.save()

        # Assert
        pet.refresh_from_db()
        assert pet.species == Pet.Species.DOG

    def test_pet_age_can_be_updated(self):
        """Test: Pet age can be updated"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")
        pet = Pet.objects.create(name="Buddy", family=family, age=3)
        assert pet.age == 3

        # Act
        pet.age = 4
        pet.save()

        # Assert
        pet.refresh_from_db()
        assert pet.age == 4

    def test_multiple_pets_per_family(self):
        """Test: Family can have multiple pets"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        Pet.objects.create(name="Buddy", family=family, species=Pet.Species.DOG)
        Pet.objects.create(name="Whiskers", family=family, species=Pet.Species.CAT)
        Pet.objects.create(name="Nemo", family=family, species=Pet.Species.FISH)

        # Assert
        assert family.pet_set.count() == 3

    def test_pet_with_all_fields(self, user):
        """Test: Create pet with all fields populated"""
        from apps.shared.models import Family
        from apps.shared.models import Pet

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        pet = Pet.objects.create(
            name="Buddy",
            species=Pet.Species.DOG,
            breed="Golden Retriever",
            age=5,
            notes="Loves to play fetch, needs daily walks",
            family=family,
            created_by=user,
        )

        # Assert
        assert pet.name == "Buddy"
        assert pet.species == Pet.Species.DOG
        assert pet.breed == "Golden Retriever"
        assert pet.age == 5
        assert pet.notes == "Loves to play fetch, needs daily walks"
        assert pet.family == family
        assert pet.created_by == user
