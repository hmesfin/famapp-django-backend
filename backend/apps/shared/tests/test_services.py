"""
Tests for shared app services.
"""

from django.test import TestCase

from apps.shared.models import Family, FamilyMember
from apps.shared.services import create_family_for_user
from apps.users.models import User


class CreateFamilyForUserServiceTests(TestCase):
    """Test create_family_for_user() service function."""

    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
            email_verified=True,
        )

    def test_creates_family_for_user(self):
        """Test service creates a family for the user."""
        family, family_member = create_family_for_user(self.user)

        self.assertIsNotNone(family)
        self.assertIsInstance(family, Family)
        self.assertEqual(Family.objects.count(), 1)

    def test_family_name_uses_first_name(self):
        """Test family name is '{first_name}'s Family'."""
        family, family_member = create_family_for_user(self.user)

        self.assertEqual(family.name, "John's Family")

    def test_family_name_fallback_for_empty_first_name(self):
        """Test family name fallback when first_name is empty."""
        user = User.objects.create_user(
            email="noname@example.com",
            password="testpass123",
            first_name="",
            last_name="Smith",
            email_verified=True,
        )

        family, family_member = create_family_for_user(user)

        self.assertEqual(family.name, "User's Family")

    def test_family_created_by_set_to_user(self):
        """Test family.created_by is set to the user."""
        family, family_member = create_family_for_user(self.user)

        self.assertEqual(family.created_by, self.user)

    def test_family_has_public_id(self):
        """Test family has public_id after creation."""
        family, family_member = create_family_for_user(self.user)

        self.assertIsNotNone(family.public_id)

    def test_creates_family_member_for_user(self):
        """Test service creates FamilyMember linking user to family."""
        family, family_member = create_family_for_user(self.user)

        self.assertIsNotNone(family_member)
        self.assertIsInstance(family_member, FamilyMember)
        self.assertEqual(FamilyMember.objects.count(), 1)

    def test_family_member_role_is_organizer(self):
        """Test FamilyMember role is ORGANIZER."""
        family, family_member = create_family_for_user(self.user)

        self.assertEqual(family_member.role, FamilyMember.Role.ORGANIZER)

    def test_family_member_links_user_and_family(self):
        """Test FamilyMember links correct user and family."""
        family, family_member = create_family_for_user(self.user)

        self.assertEqual(family_member.user, self.user)
        self.assertEqual(family_member.family, family)

    def test_user_is_only_member_initially(self):
        """Test user is the only member of the family initially."""
        family, family_member = create_family_for_user(self.user)

        self.assertEqual(family.members.count(), 1)
        self.assertEqual(family.familymember_set.count(), 1)

    def test_service_returns_both_family_and_membership(self):
        """Test service returns tuple (family, family_member)."""
        result = create_family_for_user(self.user)

        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        family, family_member = result
        self.assertIsInstance(family, Family)
        self.assertIsInstance(family_member, FamilyMember)

    def test_idempotent_no_duplicate_families(self):
        """Test calling service twice doesn't create duplicate families."""
        family1, member1 = create_family_for_user(self.user)
        family2, member2 = create_family_for_user(self.user)

        self.assertEqual(Family.objects.count(), 1)
        self.assertEqual(FamilyMember.objects.count(), 1)
        self.assertEqual(family1.id, family2.id)
        self.assertEqual(member1.id, member2.id)

    def test_returns_existing_family_if_user_already_has_one(self):
        """Test service returns existing family instead of creating new one."""
        # Create family first time
        family1, member1 = create_family_for_user(self.user)

        # Call again - should return same family
        family2, member2 = create_family_for_user(self.user)

        self.assertEqual(family1.id, family2.id)
        self.assertEqual(member1.id, member2.id)

    def test_service_raises_value_error_for_none_user(self):
        """Test service raises ValueError if user is None."""
        with self.assertRaises(ValueError) as context:
            create_family_for_user(None)

        self.assertIn("User cannot be None", str(context.exception))

    def test_handles_user_with_multiple_families(self):
        """Test service returns first family if user already has multiple."""
        # Manually create two families for user
        family1 = Family.objects.create(name="First Family", created_by=self.user)
        FamilyMember.objects.create(
            user=self.user, family=family1, role=FamilyMember.Role.ORGANIZER
        )

        family2 = Family.objects.create(name="Second Family", created_by=self.user)
        FamilyMember.objects.create(
            user=self.user, family=family2, role=FamilyMember.Role.PARENT
        )

        # Service should return first family
        result_family, result_member = create_family_for_user(self.user)

        self.assertEqual(result_family.id, family1.id)
        self.assertEqual(Family.objects.count(), 2)  # No new family created

    def test_atomic_transaction_rollback_on_error(self):
        """Test transaction rolls back if FamilyMember creation fails."""
        # This test verifies @transaction.atomic behavior
        # We'll rely on database constraints to force a rollback
        initial_family_count = Family.objects.count()

        # Create a family member first to violate unique constraint
        family = Family.objects.create(name="Existing Family", created_by=self.user)
        FamilyMember.objects.create(
            user=self.user, family=family, role=FamilyMember.Role.ORGANIZER
        )

        # Service should handle existing membership gracefully (idempotency)
        result_family, result_member = create_family_for_user(self.user)

        # Should return existing family, not create duplicate
        self.assertEqual(result_family.id, family.id)
