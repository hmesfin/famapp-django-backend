"""
Test module for Family and FamilyMember serializers.

Following TDD methodology (Red-Green-Refactor):
- Write tests FIRST
- Watch them FAIL (Red)
- Implement the minimum code to pass (Green)
- Refactor for quality (Refactor)

Ham Dog & TC making sure our serializers work correctly! 🚀
"""

import pytest
from django.contrib.auth import get_user_model

from apps.shared.models import Family
from apps.shared.models import FamilyMember

User = get_user_model()


@pytest.mark.django_db
class TestFamilyCreateSerializer:
    """
    Test suite for FamilyCreateSerializer.

    This serializer is used when creating a new family.
    It should validate the name field (required, 1-100 chars).
    """

    def test_validates_name_is_required(self):
        """Test that name field is required."""
        from apps.shared.serializers import FamilyCreateSerializer

        serializer = FamilyCreateSerializer(data={})
        assert not serializer.is_valid()
        assert "name" in serializer.errors
        assert serializer.errors["name"][0].code == "required"

    def test_validates_name_minimum_length(self):
        """Test that name must be at least 1 character."""
        from apps.shared.serializers import FamilyCreateSerializer

        serializer = FamilyCreateSerializer(data={"name": ""})
        assert not serializer.is_valid()
        assert "name" in serializer.errors
        # Empty string should fail validation

    def test_validates_name_maximum_length(self):
        """Test that name cannot exceed 100 characters."""
        from apps.shared.serializers import FamilyCreateSerializer

        serializer = FamilyCreateSerializer(data={"name": "A" * 101})
        assert not serializer.is_valid()
        assert "name" in serializer.errors
        # Check that error mentions 100 characters limit
        assert "100" in str(serializer.errors["name"][0])

    def test_accepts_valid_family_name(self):
        """Test that valid family name passes validation."""
        from apps.shared.serializers import FamilyCreateSerializer

        serializer = FamilyCreateSerializer(data={"name": "The Smith Family"})
        assert serializer.is_valid(), serializer.errors

    def test_saves_family_with_valid_data(self):
        """Test that serializer can save a family."""
        from apps.shared.serializers import FamilyCreateSerializer

        user = User.objects.create_user(
            email="test@example.com", password="testpass123",
        )
        serializer = FamilyCreateSerializer(data={"name": "Test Family"})
        assert serializer.is_valid()

        # Save with created_by user
        family = serializer.save(created_by=user)
        assert family.name == "Test Family"
        assert family.created_by == user
        assert Family.objects.filter(id=family.id).exists()


@pytest.mark.django_db
class TestFamilyUpdateSerializer:
    """
    Test suite for FamilyUpdateSerializer.

    This serializer is used when updating an existing family.
    All fields should be optional (partial updates).
    """

    def test_allows_partial_updates(self):
        """Test that all fields are optional for updates."""
        from apps.shared.serializers import FamilyUpdateSerializer

        serializer = FamilyUpdateSerializer(data={})
        # An empty update should be valid (no required fields)
        assert serializer.is_valid(), serializer.errors

    def test_updates_family_name(self):
        """Test that family name can be updated."""
        from apps.shared.serializers import FamilyUpdateSerializer

        user = User.objects.create_user(
            email="test@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Old Name", created_by=user)

        serializer = FamilyUpdateSerializer(
            instance=family, data={"name": "New Name"}, partial=True,
        )
        assert serializer.is_valid(), serializer.errors

        updated_family = serializer.save(updated_by=user)
        assert updated_family.name == "New Name"
        assert updated_family.updated_by == user

    def test_validates_name_length_on_update(self):
        """Test that name length validation applies to updates."""
        from apps.shared.serializers import FamilyUpdateSerializer

        user = User.objects.create_user(
            email="test@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Original Name", created_by=user)

        serializer = FamilyUpdateSerializer(
            instance=family, data={"name": "A" * 101}, partial=True,
        )
        assert not serializer.is_valid()
        assert "name" in serializer.errors


@pytest.mark.django_db
class TestFamilySerializer:
    """
    Test suite for FamilySerializer.

    This is the main read serializer for Family objects.
    Should include all fields with proper read-only settings.
    """

    def test_includes_all_expected_fields(self):
        """Test that serializer includes all expected fields."""
        from apps.shared.serializers import FamilySerializer

        user = User.objects.create_user(
            email="test@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user)

        serializer = FamilySerializer(instance=family)
        data = serializer.data

        # Check for essential fields
        assert "id" in data
        assert "public_id" in data
        assert "name" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_public_id_is_read_only(self):
        """Test that public_id cannot be set via serializer."""
        import uuid

        from apps.shared.serializers import FamilySerializer

        fake_uuid = uuid.uuid4()

        serializer = FamilySerializer(data={"name": "Test", "public_id": fake_uuid})
        if serializer.is_valid():
            family = serializer.save()
            # public_id should be auto-generated, not the one we provided
            assert family.public_id != fake_uuid

    def test_timestamps_are_read_only(self):
        """Test that timestamps are included but read-only."""
        from apps.shared.serializers import FamilySerializer

        user = User.objects.create_user(
            email="test@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user)

        serializer = FamilySerializer(instance=family)
        data = serializer.data

        assert data["created_at"] is not None
        assert data["updated_at"] is not None


@pytest.mark.django_db
class TestFamilyDetailSerializer:
    """
    Test suite for FamilyDetailSerializer.

    This serializer extends FamilySerializer to include nested member information.
    Should show all family members with their roles and user details.
    """

    def test_includes_member_list(self):
        """Test that serializer includes nested members."""
        from apps.shared.serializers import FamilyDetailSerializer

        # Create family with members
        user1 = User.objects.create_user(
            email="admin@example.com", password="testpass123",
        )
        user2 = User.objects.create_user(
            email="member@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Test Family", created_by=user1)
        FamilyMember.objects.create(
            family=family, user=user1, role=FamilyMember.Role.ORGANIZER,
        )
        FamilyMember.objects.create(
            family=family, user=user2, role=FamilyMember.Role.PARENT,
        )

        serializer = FamilyDetailSerializer(instance=family)
        data = serializer.data

        assert "members" in data
        assert len(data["members"]) == 2

    def test_member_data_includes_role_and_user_info(self):
        """Test that each member includes role and user information."""
        from apps.shared.serializers import FamilyDetailSerializer

        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        family = Family.objects.create(name="Test Family", created_by=user)
        FamilyMember.objects.create(
            family=family, user=user, role=FamilyMember.Role.ORGANIZER,
        )

        serializer = FamilyDetailSerializer(instance=family)
        data = serializer.data

        member_data = data["members"][0]
        assert "role" in member_data
        assert member_data["role"] == "organizer"
        assert "user" in member_data
        # User should have at least email
        assert "email" in member_data["user"]

    def test_empty_family_has_empty_member_list(self):
        """Test that family with no members has empty list."""
        from apps.shared.serializers import FamilyDetailSerializer

        user = User.objects.create_user(
            email="test@example.com", password="testpass123",
        )
        family = Family.objects.create(name="Empty Family", created_by=user)

        serializer = FamilyDetailSerializer(instance=family)
        data = serializer.data

        assert "members" in data
        assert len(data["members"]) == 0
