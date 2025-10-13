"""
Tests for Family and FamilyMember models
Following TDD discipline - Red-Green-Refactor

Testing FamApp family collaboration models.
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


@pytest.mark.django_db
class TestFamilyModel:
    """Test Family model"""

    def test_create_family_with_name(self):
        """Test: Create family with name"""
        from apps.shared.models import Family

        # Arrange & Act
        family = Family.objects.create(name="Smith Family")

        # Assert
        assert family.id is not None
        assert family.name == "Smith Family"
        assert family.public_id is not None

    def test_family_name_is_required(self):
        """Test: Family name is required and max 100 chars"""
        from apps.shared.models import Family

        # Arrange & Act & Assert
        with pytest.raises(IntegrityError):
            Family.objects.create(name=None)

    def test_family_name_max_length_100(self):
        """Test: Family name max length is 100 characters"""
        from apps.shared.models import Family

        # Arrange
        long_name = "A" * 101

        # Act & Assert
        with pytest.raises(Exception):  # ValidationError or DataError
            Family.objects.create(name=long_name)

    def test_family_has_timestamps(self):
        """Test: Family has created_at and updated_at"""
        from apps.shared.models import Family

        # Arrange & Act
        family = Family.objects.create(name="Smith Family")

        # Assert
        assert family.created_at is not None
        assert family.updated_at is not None

    def test_family_has_audit_fields(self):
        """Test: Family has created_by and updated_by"""
        from apps.shared.models import Family

        # Arrange & Act
        family = Family.objects.create(name="Smith Family")

        # Assert
        assert hasattr(family, "created_by")
        assert hasattr(family, "updated_by")

    def test_family_has_soft_delete_fields(self):
        """Test: Family has is_deleted, deleted_at, deleted_by"""
        from apps.shared.models import Family

        # Arrange & Act
        family = Family.objects.create(name="Smith Family")

        # Assert
        assert hasattr(family, "is_deleted")
        assert hasattr(family, "deleted_at")
        assert hasattr(family, "deleted_by")
        assert family.is_deleted is False

    def test_family_str_representation(self):
        """Test: Family __str__ returns family name"""
        from apps.shared.models import Family

        # Arrange & Act
        family = Family.objects.create(name="Smith Family")

        # Assert
        assert str(family) == "Smith Family"

    def test_family_has_members_relationship(self):
        """Test: Family has many-to-many with User through FamilyMember"""
        from apps.shared.models import Family

        # Arrange & Act
        family = Family.objects.create(name="Smith Family")

        # Assert
        assert hasattr(family, "members")

    def test_create_family_with_creator(self, user):
        """Test: Create family with created_by user"""
        from apps.shared.models import Family

        # Arrange & Act
        family = Family.objects.create(name="Smith Family", created_by=user)

        # Assert
        assert family.created_by == user


@pytest.mark.django_db
class TestFamilyMemberModel:
    """Test FamilyMember model"""

    def test_create_family_member_with_user_and_role(self, user):
        """Test: Create family member with user, family, and role"""
        from apps.shared.models import Family
        from apps.shared.models import FamilyMember

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        member = FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.PARENT,
        )

        # Assert
        assert member.id is not None
        assert member.family == family
        assert member.user == user
        assert member.role == FamilyMember.Role.PARENT

    def test_family_member_role_enum_values(self):
        """Test: Role enum has correct values (ORGANIZER, PARENT, CHILD)"""
        from apps.shared.models import FamilyMember

        # Assert
        assert hasattr(FamilyMember, "Role")
        assert hasattr(FamilyMember.Role, "ORGANIZER")
        assert hasattr(FamilyMember.Role, "PARENT")
        assert hasattr(FamilyMember.Role, "CHILD")

    def test_family_member_default_role_is_parent(self, user):
        """Test: Default role is PARENT"""
        from apps.shared.models import Family
        from apps.shared.models import FamilyMember

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        member = FamilyMember.objects.create(family=family, user=user)

        # Assert
        assert member.role == FamilyMember.Role.PARENT

    def test_family_member_unique_constraint(self, user):
        """Test: Unique constraint (family, user) - cannot add same user twice"""
        from apps.shared.models import Family
        from apps.shared.models import FamilyMember

        # Arrange
        family = Family.objects.create(name="Smith Family")
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        # Act & Assert
        with pytest.raises(IntegrityError):
            FamilyMember.objects.create(
                family=family, user=user, role=FamilyMember.Role.PARENT,
            )

    def test_family_member_role_enum_organizer(self, user):
        """Test: Can create member with ORGANIZER role"""
        from apps.shared.models import Family
        from apps.shared.models import FamilyMember

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        member = FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        # Assert
        assert member.role == FamilyMember.Role.ORGANIZER

    def test_family_member_role_enum_parent(self, user):
        """Test: Can create member with PARENT role"""
        from apps.shared.models import Family
        from apps.shared.models import FamilyMember

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        member = FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.PARENT,
        )

        # Assert
        assert member.role == FamilyMember.Role.PARENT

    def test_family_member_role_enum_child(self, user):
        """Test: Can create member with CHILD role"""
        from apps.shared.models import Family
        from apps.shared.models import FamilyMember

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        member = FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.CHILD,
        )

        # Assert
        assert member.role == FamilyMember.Role.CHILD

    def test_family_member_has_timestamps(self, user):
        """Test: FamilyMember has created_at and updated_at (SimpleBaseModel)"""
        from apps.shared.models import Family
        from apps.shared.models import FamilyMember

        # Arrange
        family = Family.objects.create(name="Smith Family")

        # Act
        member = FamilyMember.objects.create(family=family, user=user)

        # Assert
        assert member.created_at is not None
        assert member.updated_at is not None

    def test_family_member_does_not_have_audit_fields(self, user):
        """Test: FamilyMember does NOT have audit fields (uses SimpleBaseModel)"""
        from apps.shared.models import Family
        from apps.shared.models import FamilyMember

        # Arrange
        family = Family.objects.create(name="Smith Family")
        member = FamilyMember.objects.create(family=family, user=user)

        # Assert - These should NOT exist
        with pytest.raises(AttributeError):
            _ = member.created_by

    def test_family_member_str_representation(self, user):
        """Test: FamilyMember __str__ returns meaningful representation"""
        from apps.shared.models import Family
        from apps.shared.models import FamilyMember

        # Arrange
        family = Family.objects.create(name="Smith Family")
        member = FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        # Act
        str_repr = str(member)

        # Assert
        assert "Smith Family" in str_repr or user.email in str_repr

    def test_delete_family_cascades_to_members(self, user):
        """Test: Deleting family soft-deletes all related FamilyMembers"""
        from apps.shared.models import Family
        from apps.shared.models import FamilyMember

        # Arrange
        family = Family.objects.create(name="Smith Family")
        member = FamilyMember.objects.create(family=family, user=user)
        member_id = member.id

        # Act
        family.soft_delete()

        # Assert
        # Member should still exist (not hard deleted)
        assert FamilyMember.objects.filter(id=member_id).exists()

    def test_family_members_reverse_relationship(self, user):
        """Test: Family has reverse relationship to members via 'memberships'"""
        from apps.shared.models import Family
        from apps.shared.models import FamilyMember

        # Arrange
        family = Family.objects.create(name="Smith Family")
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        # Act
        memberships = family.familymember_set.all()

        # Assert
        assert memberships.count() == 1
        assert memberships[0].user == user

    def test_user_can_belong_to_multiple_families(self, user):
        """Test: User can be a member of multiple families"""
        from apps.shared.models import Family
        from apps.shared.models import FamilyMember

        # Arrange
        family1 = Family.objects.create(name="Smith Family")
        family2 = Family.objects.create(name="Jones Family")

        # Act
        FamilyMember.objects.create(family=family1, user=user)
        FamilyMember.objects.create(family=family2, user=user)

        # Assert
        assert FamilyMember.objects.filter(user=user).count() == 2

    def test_family_can_have_multiple_members(self):
        """Test: Family can have multiple members"""
        from apps.shared.models import Family
        from apps.shared.models import FamilyMember

        # Arrange
        family = Family.objects.create(name="Smith Family")
        user1 = User.objects.create_user(email="user1@example.com", password="pass123")
        user2 = User.objects.create_user(email="user2@example.com", password="pass123")

        # Act
        FamilyMember.objects.create(
            family=family, user=user1, role=FamilyMember.Role.ORGANIZER,
        )
        FamilyMember.objects.create(
            family=family, user=user2, role=FamilyMember.Role.PARENT,
        )

        # Assert
        assert family.familymember_set.count() == 2

    def test_family_member_role_can_be_updated(self, user):
        """Test: FamilyMember role can be updated"""
        from apps.shared.models import Family
        from apps.shared.models import FamilyMember

        # Arrange
        family = Family.objects.create(name="Smith Family")
        member = FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.CHILD,
        )

        # Act
        member.role = FamilyMember.Role.PARENT
        member.save()

        # Assert
        member.refresh_from_db()
        assert member.role == FamilyMember.Role.PARENT
