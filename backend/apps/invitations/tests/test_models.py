"""
Model tests for the invitations app
TDD approach - these tests drove our model implementation!
"""

import time
from datetime import timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.invitations.models import Invitation

User = get_user_model()


class InvitationModelTests(TestCase):
    """Test suite for the Invitation model"""

    def setUp(self):
        """Set up test fixtures"""
        self.inviter = User.objects.create_user(
            email="inviter@example.com", password="testpass123"
        )

    def test_invitation_creation(self):
        """Test creating a basic invitation"""
        invitation = Invitation.objects.create(
            email="newuser@example.com",
            invited_by=self.inviter,
            role="member",
            organization_name="Test Company",
        )

        self.assertEqual(invitation.email, "newuser@example.com")
        self.assertEqual(invitation.invited_by, self.inviter)
        self.assertEqual(invitation.status, "pending")
        self.assertIsNotNone(invitation.token)
        self.assertIsNotNone(invitation.expires_at)

    def test_invitation_token_uniqueness(self):
        """Test that invitation tokens are unique"""
        invitation1 = Invitation.objects.create(
            email="user1@example.com", invited_by=self.inviter
        )
        invitation2 = Invitation.objects.create(
            email="user2@example.com", invited_by=self.inviter
        )

        self.assertNotEqual(invitation1.token, invitation2.token)

    def test_invitation_expiry_default(self):
        """Test that invitations expire after 7 days by default"""
        invitation = Invitation.objects.create(
            email="newuser@example.com", invited_by=self.inviter
        )

        expected_expiry = timezone.now() + timedelta(days=7)
        # Allow 1 minute tolerance for test execution time
        delta = abs((invitation.expires_at - expected_expiry).total_seconds())
        self.assertLess(delta, 60)

    def test_invitation_is_expired_property(self):
        """Test the is_expired property"""
        invitation = Invitation.objects.create(
            email="newuser@example.com", invited_by=self.inviter
        )

        # Fresh invitation should not be expired
        self.assertFalse(invitation.is_expired)

        # Manually set expiry to past
        invitation.expires_at = timezone.now() - timedelta(days=1)
        invitation.save()
        self.assertTrue(invitation.is_expired)

    def test_invitation_accept(self):
        """Test accepting an invitation"""
        invitation = Invitation.objects.create(
            email="newuser@example.com", invited_by=self.inviter
        )

        user = User.objects.create_user(
            email="newuser@example.com", password="newpass123"
        )

        invitation.accept(user)

        self.assertEqual(invitation.status, "accepted")
        self.assertEqual(invitation.accepted_by, user)
        self.assertIsNotNone(invitation.accepted_at)

    def test_cannot_accept_expired_invitation(self):
        """Test that expired invitations cannot be accepted"""
        invitation = Invitation.objects.create(
            email="newuser@example.com", invited_by=self.inviter
        )

        # Expire the invitation
        invitation.expires_at = timezone.now() - timedelta(days=1)
        invitation.save()

        user = User.objects.create_user(
            email="newuser@example.com", password="newpass123"
        )

        with self.assertRaises(ValidationError) as context:
            invitation.accept(user)

        self.assertIn("expired", str(context.exception).lower())

    def test_cannot_accept_already_accepted_invitation(self):
        """Test that already accepted invitations cannot be re-accepted"""
        invitation = Invitation.objects.create(
            email="newuser@example.com", invited_by=self.inviter
        )

        user = User.objects.create_user(
            email="newuser@example.com", password="newpass123"
        )

        invitation.accept(user)

        # Try to accept again
        with self.assertRaises(ValidationError) as context:
            invitation.accept(user)

        self.assertIn("already", str(context.exception).lower())

    def test_resend_invitation(self):
        """Test resending an invitation generates new token and extends expiry"""
        invitation = Invitation.objects.create(
            email="newuser@example.com", invited_by=self.inviter
        )

        original_token = invitation.token
        original_expiry = invitation.expires_at

        # Wait a moment to ensure timestamps differ
        time.sleep(0.1)

        invitation.resend()

        self.assertNotEqual(invitation.token, original_token)
        self.assertGreater(invitation.expires_at, original_expiry)
        self.assertEqual(invitation.status, "pending")

    def test_soft_delete_invitation(self):
        """Test that invitations use soft delete from BaseModel"""
        invitation = Invitation.objects.create(
            email="newuser@example.com", invited_by=self.inviter
        )

        invitation_id = invitation.id
        invitation.delete()

        # Should be soft deleted, not actually removed
        self.assertTrue(Invitation.objects.filter(id=invitation_id).exists())
        self.assertIsNotNone(Invitation.objects.get(id=invitation_id).deleted_at)

        # Should not appear in default queryset
        self.assertFalse(Invitation.objects.active().filter(id=invitation_id).exists())

    def test_cancel_invitation(self):
        """Test canceling an invitation"""
        invitation = Invitation.objects.create(
            email="newuser@example.com", invited_by=self.inviter
        )

        invitation.cancel()

        self.assertEqual(invitation.status, "cancelled")

    def test_invitation_str_representation(self):
        """Test the string representation of an invitation"""
        invitation = Invitation.objects.create(
            email="test@example.com", invited_by=self.inviter
        )

        self.assertEqual(str(invitation), "Invitation to test@example.com (pending)")

    def test_invitation_manager_active_method(self):
        """Test the custom manager's active() method"""
        # Create active and deleted invitations
        active_invitation = Invitation.objects.create(
            email="active@example.com", invited_by=self.inviter
        )

        deleted_invitation = Invitation.objects.create(
            email="deleted@example.com", invited_by=self.inviter
        )
        deleted_invitation.soft_delete()

        # Check active() returns only non-deleted
        active_invitations = Invitation.objects.active()
        self.assertIn(active_invitation, active_invitations)
        self.assertNotIn(deleted_invitation, active_invitations)
