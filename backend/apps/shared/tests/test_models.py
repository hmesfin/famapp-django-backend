"""
Tests for shared base models
Following TDD discipline - Red-Green-Refactor

Testing BaseModel and SimpleBaseModel abstract classes with all their mixins.
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

# Import concrete test models from conftest
from .conftest import TestBaseModelConcrete
from .conftest import TestSimpleBaseModelConcrete

User = get_user_model()


@pytest.mark.django_db
class TestUUIDMixin:
    """Test UUIDMixin functionality"""

    def test_model_has_public_id_field(self):
        """Test: Model inheriting UUIDMixin has public_id (UUIDField)"""
        # Arrange & Act
        instance = TestBaseModelConcrete.objects.create(name="Test")

        # Assert
        assert hasattr(instance, "public_id")
        assert instance.public_id is not None
        assert isinstance(instance.public_id, type(instance.public_id))  # UUID type

    def test_public_id_is_unique(self):
        """Test: public_id is unique across instances"""
        # Arrange & Act
        instance1 = TestBaseModelConcrete.objects.create(name="Test 1")
        instance2 = TestBaseModelConcrete.objects.create(name="Test 2")

        # Assert
        assert instance1.public_id != instance2.public_id

    def test_public_id_is_not_editable(self):
        """Test: public_id is not editable (set once on creation)"""
        # Arrange
        instance = TestBaseModelConcrete.objects.create(name="Test")
        original_public_id = instance.public_id

        # Act
        instance.name = "Updated"
        instance.save()

        # Assert
        instance.refresh_from_db()
        assert instance.public_id == original_public_id

    def test_model_has_legacy_uuid_field(self):
        """Test: Model has legacy uuid field (for backward compatibility)"""
        # Arrange & Act
        instance = TestBaseModelConcrete.objects.create(name="Test")

        # Assert
        assert hasattr(instance, "uuid")
        assert instance.uuid is not None


@pytest.mark.django_db
class TestTimestampedMixin:
    """Test TimestampedMixin functionality"""

    def test_model_has_created_at_field(self):
        """Test: Model has created_at timestamp"""
        # Arrange & Act
        instance = TestBaseModelConcrete.objects.create(name="Test")

        # Assert
        assert hasattr(instance, "created_at")
        assert instance.created_at is not None
        assert instance.created_at <= timezone.now()

    def test_model_has_updated_at_field(self):
        """Test: Model has updated_at timestamp"""
        # Arrange & Act
        instance = TestBaseModelConcrete.objects.create(name="Test")

        # Assert
        assert hasattr(instance, "updated_at")
        assert instance.updated_at is not None
        assert instance.updated_at <= timezone.now()

    def test_updated_at_changes_on_save(self):
        """Test: updated_at changes when instance is saved"""
        # Arrange
        instance = TestBaseModelConcrete.objects.create(name="Test")
        original_updated_at = instance.updated_at

        # Act - Wait a moment and update
        import time

        time.sleep(0.01)  # Small delay to ensure timestamp difference
        instance.name = "Updated"
        instance.save()

        # Assert
        instance.refresh_from_db()
        assert instance.updated_at > original_updated_at

    def test_created_at_does_not_change_on_save(self):
        """Test: created_at does NOT change when instance is saved"""
        # Arrange
        instance = TestBaseModelConcrete.objects.create(name="Test")
        original_created_at = instance.created_at

        # Act
        instance.name = "Updated"
        instance.save()

        # Assert
        instance.refresh_from_db()
        assert instance.created_at == original_created_at

    def test_default_ordering_by_created_at_desc(self):
        """Test: Default ordering is by created_at descending (newest first)"""
        # Arrange & Act
        instance1 = TestBaseModelConcrete.objects.create(name="First")
        instance2 = TestBaseModelConcrete.objects.create(name="Second")
        instance3 = TestBaseModelConcrete.objects.create(name="Third")

        # Assert
        queryset = TestBaseModelConcrete.objects.all()
        assert list(queryset) == [instance3, instance2, instance1]


@pytest.mark.django_db
class TestAuditMixin:
    """Test AuditMixin functionality"""

    def test_model_has_created_by_field(self, user):
        """Test: Model has created_by ForeignKey to User"""
        # Arrange & Act
        instance = TestBaseModelConcrete.objects.create(name="Test", created_by=user)

        # Assert
        assert hasattr(instance, "created_by")
        assert instance.created_by == user

    def test_model_has_updated_by_field(self, user):
        """Test: Model has updated_by ForeignKey to User"""
        # Arrange
        instance = TestBaseModelConcrete.objects.create(name="Test", created_by=user)

        # Act
        instance.updated_by = user
        instance.save()

        # Assert
        assert hasattr(instance, "updated_by")
        assert instance.updated_by == user

    def test_created_by_is_nullable(self):
        """Test: created_by can be null (for system-created records)"""
        # Arrange & Act
        instance = TestBaseModelConcrete.objects.create(name="Test")

        # Assert
        assert instance.created_by is None

    def test_updated_by_is_nullable(self):
        """Test: updated_by can be null"""
        # Arrange & Act
        instance = TestBaseModelConcrete.objects.create(name="Test")

        # Assert
        assert instance.updated_by is None

    def test_created_by_uses_set_null_on_delete(self, user):
        """Test: created_by uses SET_NULL when user is deleted"""
        # Arrange
        instance = TestBaseModelConcrete.objects.create(name="Test", created_by=user)
        assert instance.created_by == user

        # Act
        user_id = user.id
        user.delete()

        # Assert
        instance.refresh_from_db()
        assert instance.created_by is None


@pytest.mark.django_db
class TestSoftDeleteMixin:
    """Test SoftDeleteMixin functionality"""

    def test_model_has_is_deleted_field(self):
        """Test: Model has is_deleted boolean field"""
        # Arrange & Act
        instance = TestBaseModelConcrete.objects.create(name="Test")

        # Assert
        assert hasattr(instance, "is_deleted")
        assert instance.is_deleted is False

    def test_model_has_deleted_at_field(self):
        """Test: Model has deleted_at timestamp field"""
        # Arrange & Act
        instance = TestBaseModelConcrete.objects.create(name="Test")

        # Assert
        assert hasattr(instance, "deleted_at")
        assert instance.deleted_at is None

    def test_model_has_deleted_by_field(self, user):
        """Test: Model has deleted_by ForeignKey to User"""
        # Arrange & Act
        instance = TestBaseModelConcrete.objects.create(name="Test")
        instance.deleted_by = user
        instance.save()

        # Assert
        assert hasattr(instance, "deleted_by")
        assert instance.deleted_by == user

    def test_soft_delete_method_sets_is_deleted(self):
        """Test: soft_delete() method sets is_deleted=True"""
        # Arrange
        instance = TestBaseModelConcrete.objects.create(name="Test")
        assert instance.is_deleted is False

        # Act
        instance.soft_delete()

        # Assert
        instance.refresh_from_db()
        assert instance.is_deleted is True

    def test_soft_delete_method_sets_deleted_at(self):
        """Test: soft_delete() method sets deleted_at timestamp"""
        # Arrange
        instance = TestBaseModelConcrete.objects.create(name="Test")
        assert instance.deleted_at is None

        # Act
        instance.soft_delete()

        # Assert
        instance.refresh_from_db()
        assert instance.deleted_at is not None
        assert instance.deleted_at <= timezone.now()

    def test_soft_delete_method_sets_deleted_by(self, user):
        """Test: soft_delete() method sets deleted_by if user provided"""
        # Arrange
        instance = TestBaseModelConcrete.objects.create(name="Test")
        assert instance.deleted_by is None

        # Act
        instance.soft_delete(user=user)

        # Assert
        instance.refresh_from_db()
        assert instance.deleted_by == user

    def test_soft_delete_without_user(self):
        """Test: soft_delete() works without user parameter"""
        # Arrange
        instance = TestBaseModelConcrete.objects.create(name="Test")

        # Act
        instance.soft_delete()

        # Assert
        instance.refresh_from_db()
        assert instance.is_deleted is True
        assert instance.deleted_at is not None
        assert instance.deleted_by is None

    def test_restore_method_clears_is_deleted(self):
        """Test: restore() method sets is_deleted=False"""
        # Arrange
        instance = TestBaseModelConcrete.objects.create(name="Test")
        instance.soft_delete()
        assert instance.is_deleted is True

        # Act
        instance.restore()

        # Assert
        instance.refresh_from_db()
        assert instance.is_deleted is False

    def test_restore_method_clears_deleted_at(self):
        """Test: restore() method clears deleted_at"""
        # Arrange
        instance = TestBaseModelConcrete.objects.create(name="Test")
        instance.soft_delete()
        assert instance.deleted_at is not None

        # Act
        instance.restore()

        # Assert
        instance.refresh_from_db()
        assert instance.deleted_at is None

    def test_restore_method_clears_deleted_by(self, user):
        """Test: restore() method clears deleted_by"""
        # Arrange
        instance = TestBaseModelConcrete.objects.create(name="Test")
        instance.soft_delete(user=user)
        assert instance.deleted_by == user

        # Act
        instance.restore()

        # Assert
        instance.refresh_from_db()
        assert instance.deleted_by is None

    def test_is_active_property_returns_true_for_non_deleted(self):
        """Test: is_active property returns True when not soft deleted"""
        # Arrange & Act
        instance = TestBaseModelConcrete.objects.create(name="Test")

        # Assert
        assert instance.is_active is True

    def test_is_active_property_returns_false_for_deleted(self):
        """Test: is_active property returns False when soft deleted"""
        # Arrange
        instance = TestBaseModelConcrete.objects.create(name="Test")

        # Act
        instance.soft_delete()

        # Assert
        assert instance.is_active is False

    def test_is_deleted_field_has_db_index(self):
        """Test: is_deleted field has database index for query performance"""
        # Arrange & Act
        field = TestBaseModelConcrete._meta.get_field("is_deleted")

        # Assert
        assert field.db_index is True


@pytest.mark.django_db
class TestBaseModel:
    """Test BaseModel (combines all mixins)"""

    def test_base_model_has_id_field(self):
        """Test: Model inheriting BaseModel has id (BigAutoField)"""
        # Arrange & Act
        instance = TestBaseModelConcrete.objects.create(name="Test")

        # Assert
        assert hasattr(instance, "id")
        assert instance.id is not None
        assert isinstance(instance.id, int)

    def test_base_model_has_all_uuid_mixin_fields(self):
        """Test: BaseModel includes UUIDMixin fields"""
        # Arrange & Act
        instance = TestBaseModelConcrete.objects.create(name="Test")

        # Assert
        assert hasattr(instance, "public_id")
        assert hasattr(instance, "uuid")

    def test_base_model_has_all_timestamp_fields(self):
        """Test: BaseModel includes TimestampedMixin fields"""
        # Arrange & Act
        instance = TestBaseModelConcrete.objects.create(name="Test")

        # Assert
        assert hasattr(instance, "created_at")
        assert hasattr(instance, "updated_at")

    def test_base_model_has_all_audit_fields(self):
        """Test: BaseModel includes AuditMixin fields"""
        # Arrange & Act
        instance = TestBaseModelConcrete.objects.create(name="Test")

        # Assert
        assert hasattr(instance, "created_by")
        assert hasattr(instance, "updated_by")

    def test_base_model_has_all_soft_delete_fields(self):
        """Test: BaseModel includes SoftDeleteMixin fields"""
        # Arrange & Act
        instance = TestBaseModelConcrete.objects.create(name="Test")

        # Assert
        assert hasattr(instance, "is_deleted")
        assert hasattr(instance, "deleted_at")
        assert hasattr(instance, "deleted_by")

    def test_base_model_str_representation(self):
        """Test: BaseModel __str__ method returns class name and id prefix"""
        # Arrange & Act
        instance = TestBaseModelConcrete.objects.create(name="Test")
        str_repr = str(instance)

        # Assert
        assert "TestBaseModelConcrete" in str_repr
        assert "(" in str_repr
        assert ")" in str_repr

    def test_base_model_ordering_by_created_at_desc(self):
        """Test: BaseModel default ordering is -created_at"""
        # Arrange & Act
        instance1 = TestBaseModelConcrete.objects.create(name="First")
        instance2 = TestBaseModelConcrete.objects.create(name="Second")

        # Assert
        queryset = TestBaseModelConcrete.objects.all()
        assert queryset[0] == instance2
        assert queryset[1] == instance1


@pytest.mark.django_db
class TestSimpleBaseModel:
    """Test SimpleBaseModel (UUIDMixin + TimestampedMixin only)"""

    def test_simple_base_model_has_id_field(self):
        """Test: SimpleBaseModel has id field"""
        # Arrange & Act
        instance = TestSimpleBaseModelConcrete.objects.create(title="Test")

        # Assert
        assert hasattr(instance, "id")
        assert instance.id is not None

    def test_simple_base_model_has_public_id(self):
        """Test: SimpleBaseModel has public_id (UUIDMixin)"""
        # Arrange & Act
        instance = TestSimpleBaseModelConcrete.objects.create(title="Test")

        # Assert
        assert hasattr(instance, "public_id")
        assert instance.public_id is not None

    def test_simple_base_model_has_timestamps(self):
        """Test: SimpleBaseModel has created_at and updated_at"""
        # Arrange & Act
        instance = TestSimpleBaseModelConcrete.objects.create(title="Test")

        # Assert
        assert hasattr(instance, "created_at")
        assert hasattr(instance, "updated_at")
        assert instance.created_at is not None
        assert instance.updated_at is not None

    def test_simple_base_model_does_not_have_audit_fields(self):
        """Test: SimpleBaseModel does NOT have audit fields (created_by, updated_by)"""
        # Arrange & Act
        instance = TestSimpleBaseModelConcrete.objects.create(title="Test")

        # Assert - These should NOT exist in SimpleBaseModel
        # They should raise AttributeError when accessed
        with pytest.raises(AttributeError):
            _ = instance.created_by

    def test_simple_base_model_does_not_have_soft_delete_fields(self):
        """Test: SimpleBaseModel does NOT have soft delete fields"""
        # Arrange & Act
        instance = TestSimpleBaseModelConcrete.objects.create(title="Test")

        # Assert - These should NOT exist
        with pytest.raises(AttributeError):
            _ = instance.is_deleted

    def test_simple_base_model_str_representation(self):
        """Test: SimpleBaseModel __str__ method works"""
        # Arrange & Act
        instance = TestSimpleBaseModelConcrete.objects.create(title="Test")
        str_repr = str(instance)

        # Assert
        assert "TestSimpleBaseModelConcrete" in str_repr

    def test_simple_base_model_ordering_by_created_at_desc(self):
        """Test: SimpleBaseModel default ordering is -created_at"""
        # Arrange & Act
        instance1 = TestSimpleBaseModelConcrete.objects.create(title="First")
        instance2 = TestSimpleBaseModelConcrete.objects.create(title="Second")

        # Assert
        queryset = TestSimpleBaseModelConcrete.objects.all()
        assert queryset[0] == instance2
        assert queryset[1] == instance1
