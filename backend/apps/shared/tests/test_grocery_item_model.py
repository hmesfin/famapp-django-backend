"""
Tests for GroceryItem model
Following TDD discipline - Red-Green-Refactor

Testing FamApp grocery list management model.
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


@pytest.mark.django_db
class TestGroceryItemModel:
    """Test GroceryItem model"""

    def test_create_grocery_item_with_required_fields(self):
        """Test: Create grocery item with name and family"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        item = GroceryItem.objects.create(name="Milk", family=family)

        # Assert
        assert item.id is not None
        assert item.name == "Milk"
        assert item.family == family
        assert item.public_id is not None

    def test_grocery_item_name_is_required(self):
        """Test: GroceryItem name is required"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act & Assert
        with pytest.raises(IntegrityError):
            GroceryItem.objects.create(name=None, family=family)

    def test_grocery_item_name_max_length_200(self):
        """Test: GroceryItem name max length is 200 characters"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")
        long_name = "A" * 201

        # Act & Assert
        with pytest.raises(Exception):  # ValidationError or DataError
            GroceryItem.objects.create(name=long_name, family=family)

    def test_grocery_item_family_is_required(self):
        """Test: GroceryItem family is required"""
        from apps.shared.models import GroceryItem

        # Act & Assert
        with pytest.raises(IntegrityError):
            GroceryItem.objects.create(name="Milk", family=None)

    def test_grocery_item_quantity_default_is_one(self):
        """Test: Default quantity is 1"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        item = GroceryItem.objects.create(name="Milk", family=family)

        # Assert
        assert item.quantity == 1

    def test_grocery_item_with_custom_quantity(self):
        """Test: GroceryItem can have custom quantity"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        item = GroceryItem.objects.create(name="Milk", family=family, quantity=3)

        # Assert
        assert item.quantity == 3

    def test_grocery_item_unit_is_optional(self):
        """Test: GroceryItem unit is optional"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        item = GroceryItem.objects.create(name="Milk", family=family)

        # Assert
        assert item.unit is None or item.unit == ""

    def test_grocery_item_with_unit(self):
        """Test: GroceryItem can have unit"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        item = GroceryItem.objects.create(
            name="Milk", family=family, quantity=2, unit="gallons"
        )

        # Assert
        assert item.unit == "gallons"

    def test_grocery_item_unit_max_length_50(self):
        """Test: GroceryItem unit max length is 50 characters"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")
        long_unit = "A" * 51

        # Act & Assert
        with pytest.raises(Exception):  # ValidationError or DataError
            GroceryItem.objects.create(name="Milk", family=family, unit=long_unit)

    def test_grocery_item_category_enum_values(self):
        """Test: Category enum has correct values"""
        from apps.shared.models import GroceryItem

        # Assert
        assert hasattr(GroceryItem, "Category")
        assert hasattr(GroceryItem.Category, "PRODUCE")
        assert hasattr(GroceryItem.Category, "DAIRY")
        assert hasattr(GroceryItem.Category, "MEAT")
        assert hasattr(GroceryItem.Category, "BAKERY")
        assert hasattr(GroceryItem.Category, "PANTRY")
        assert hasattr(GroceryItem.Category, "FROZEN")
        assert hasattr(GroceryItem.Category, "OTHER")

    def test_grocery_item_default_category_is_other(self):
        """Test: Default category is OTHER"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        item = GroceryItem.objects.create(name="Milk", family=family)

        # Assert
        assert item.category == GroceryItem.Category.OTHER

    def test_grocery_item_category_can_be_produce(self):
        """Test: Can create item with PRODUCE category"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        item = GroceryItem.objects.create(
            name="Apples", family=family, category=GroceryItem.Category.PRODUCE
        )

        # Assert
        assert item.category == GroceryItem.Category.PRODUCE

    def test_grocery_item_category_can_be_dairy(self):
        """Test: Can create item with DAIRY category"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        item = GroceryItem.objects.create(
            name="Milk", family=family, category=GroceryItem.Category.DAIRY
        )

        # Assert
        assert item.category == GroceryItem.Category.DAIRY

    def test_grocery_item_category_can_be_meat(self):
        """Test: Can create item with MEAT category"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        item = GroceryItem.objects.create(
            name="Chicken", family=family, category=GroceryItem.Category.MEAT
        )

        # Assert
        assert item.category == GroceryItem.Category.MEAT

    def test_grocery_item_category_can_be_bakery(self):
        """Test: Can create item with BAKERY category"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        item = GroceryItem.objects.create(
            name="Bread", family=family, category=GroceryItem.Category.BAKERY
        )

        # Assert
        assert item.category == GroceryItem.Category.BAKERY

    def test_grocery_item_category_can_be_pantry(self):
        """Test: Can create item with PANTRY category"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        item = GroceryItem.objects.create(
            name="Rice", family=family, category=GroceryItem.Category.PANTRY
        )

        # Assert
        assert item.category == GroceryItem.Category.PANTRY

    def test_grocery_item_category_can_be_frozen(self):
        """Test: Can create item with FROZEN category"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        item = GroceryItem.objects.create(
            name="Ice Cream", family=family, category=GroceryItem.Category.FROZEN
        )

        # Assert
        assert item.category == GroceryItem.Category.FROZEN

    def test_grocery_item_is_purchased_default_is_false(self):
        """Test: Default is_purchased is False"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        item = GroceryItem.objects.create(name="Milk", family=family)

        # Assert
        assert item.is_purchased is False

    def test_grocery_item_can_be_marked_as_purchased(self):
        """Test: GroceryItem can be marked as purchased"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        item = GroceryItem.objects.create(name="Milk", family=family, is_purchased=True)

        # Assert
        assert item.is_purchased is True

    def test_grocery_item_added_by_is_optional(self):
        """Test: GroceryItem added_by is optional"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        item = GroceryItem.objects.create(name="Milk", family=family)

        # Assert
        assert item.added_by is None

    def test_grocery_item_with_added_by(self, user):
        """Test: GroceryItem can have added_by user"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        item = GroceryItem.objects.create(name="Milk", family=family, added_by=user)

        # Assert
        assert item.added_by == user

    def test_grocery_item_added_by_uses_set_null_on_delete(self, user):
        """Test: added_by uses SET_NULL when user is deleted"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")
        item = GroceryItem.objects.create(name="Milk", family=family, added_by=user)
        assert item.added_by == user

        # Act
        user_id = user.id
        user.delete()

        # Assert
        item.refresh_from_db()
        assert item.added_by is None

    def test_grocery_item_has_timestamps(self):
        """Test: GroceryItem has created_at and updated_at (BaseModel)"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        item = GroceryItem.objects.create(name="Milk", family=family)

        # Assert
        assert item.created_at is not None
        assert item.updated_at is not None

    def test_grocery_item_has_audit_fields(self, user):
        """Test: GroceryItem has created_by and updated_by (BaseModel)"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        item = GroceryItem.objects.create(name="Milk", family=family, created_by=user)

        # Assert
        assert hasattr(item, "created_by")
        assert hasattr(item, "updated_by")
        assert item.created_by == user

    def test_grocery_item_has_soft_delete_fields(self):
        """Test: GroceryItem has is_deleted, deleted_at, deleted_by (BaseModel)"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        item = GroceryItem.objects.create(name="Milk", family=family)

        # Assert
        assert hasattr(item, "is_deleted")
        assert hasattr(item, "deleted_at")
        assert hasattr(item, "deleted_by")
        assert item.is_deleted is False

    def test_grocery_item_can_be_soft_deleted(self, user):
        """Test: GroceryItem can be soft deleted"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")
        item = GroceryItem.objects.create(name="Milk", family=family)

        # Act
        item.soft_delete(user=user)

        # Assert
        item.refresh_from_db()
        assert item.is_deleted is True
        assert item.deleted_at is not None
        assert item.deleted_by == user

    def test_grocery_item_str_representation(self):
        """Test: GroceryItem __str__ returns meaningful representation"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")
        item = GroceryItem.objects.create(name="Milk", family=family)

        # Act
        str_repr = str(item)

        # Assert
        assert "Milk" in str_repr

    def test_delete_family_cascades_to_grocery_items(self):
        """Test: Deleting family hard-deletes all related GroceryItems"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")
        item = GroceryItem.objects.create(name="Milk", family=family)
        item_id = item.id

        # Act
        family.delete()

        # Assert
        # Item should be hard deleted (CASCADE)
        assert not GroceryItem.objects.filter(id=item_id).exists()

    def test_family_has_reverse_relationship_to_grocery_items(self):
        """Test: Family has reverse relationship to grocery items"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")
        GroceryItem.objects.create(name="Milk", family=family)
        GroceryItem.objects.create(name="Eggs", family=family)

        # Act
        items = family.groceryitem_set.all()

        # Assert
        assert items.count() == 2

    def test_user_has_reverse_relationship_to_added_grocery_items(self, user):
        """Test: User has reverse relationship to added grocery items"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")
        GroceryItem.objects.create(name="Milk", family=family, added_by=user)
        GroceryItem.objects.create(name="Eggs", family=family, added_by=user)

        # Act
        added_items = user.groceryitem_added_by.all()

        # Assert
        assert added_items.count() == 2

    def test_grocery_item_category_can_be_updated(self):
        """Test: GroceryItem category can be updated"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")
        item = GroceryItem.objects.create(name="Milk", family=family)
        assert item.category == GroceryItem.Category.OTHER

        # Act
        item.category = GroceryItem.Category.DAIRY
        item.save()

        # Assert
        item.refresh_from_db()
        assert item.category == GroceryItem.Category.DAIRY

    def test_grocery_item_is_purchased_can_be_toggled(self):
        """Test: GroceryItem is_purchased can be toggled"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")
        item = GroceryItem.objects.create(name="Milk", family=family)
        assert item.is_purchased is False

        # Act
        item.is_purchased = True
        item.save()

        # Assert
        item.refresh_from_db()
        assert item.is_purchased is True

        # Act again - toggle back
        item.is_purchased = False
        item.save()

        # Assert
        item.refresh_from_db()
        assert item.is_purchased is False

    def test_grocery_item_quantity_can_be_updated(self):
        """Test: GroceryItem quantity can be updated"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")
        item = GroceryItem.objects.create(name="Milk", family=family, quantity=1)
        assert item.quantity == 1

        # Act
        item.quantity = 5
        item.save()

        # Assert
        item.refresh_from_db()
        assert item.quantity == 5

    def test_multiple_grocery_items_per_family(self):
        """Test: Family can have multiple grocery items"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        GroceryItem.objects.create(name="Milk", family=family)
        GroceryItem.objects.create(name="Eggs", family=family)
        GroceryItem.objects.create(name="Bread", family=family)

        # Assert
        assert family.groceryitem_set.count() == 3

    def test_user_can_add_multiple_grocery_items(self, user):
        """Test: User can add multiple grocery items"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        GroceryItem.objects.create(name="Milk", family=family, added_by=user)
        GroceryItem.objects.create(name="Eggs", family=family, added_by=user)

        # Assert
        assert user.groceryitem_added_by.count() == 2

    def test_grocery_item_with_all_fields(self, user):
        """Test: Create grocery item with all fields populated"""
        from apps.shared.models import Family
        from apps.shared.models import GroceryItem

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        item = GroceryItem.objects.create(
            name="Milk",
            quantity=2,
            unit="gallons",
            category=GroceryItem.Category.DAIRY,
            is_purchased=False,
            added_by=user,
            family=family,
            created_by=user,
        )

        # Assert
        assert item.name == "Milk"
        assert item.quantity == 2
        assert item.unit == "gallons"
        assert item.category == GroceryItem.Category.DAIRY
        assert item.is_purchased is False
        assert item.added_by == user
        assert item.family == family
        assert item.created_by == user
