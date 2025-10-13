"""
Test suite for InvitationTokenService
Testing token generation, validation, and regeneration logic

Ham Dog's Testing Commandments:
- Test both happy path and edge cases
- Mock external dependencies
- Use descriptive test names
- Test error conditions thoroughly
"""

from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.invitations.models import Invitation
from apps.invitations.services.invitation_token_service import InvitationTokenService

User = get_user_model()


class InvitationTokenServiceTest(TestCase):
    """Test cases for InvitationTokenService"""

    def setUp(self):
        """Set up test data"""
        self.service = InvitationTokenService()
        self.user = User.objects.create_user(
            email="inviter@example.com",
            password="password123",
            first_name="John",
            last_name="Inviter",
        )

    def test_generate_unique_token_creates_valid_token(self):
        """Test that generated tokens are valid and unique"""
        token = self.service.generate_unique_token()

        # Token should be a string
        self.assertIsInstance(token, str)

        # Token should have reasonable length (URL-safe base64)
        self.assertGreater(len(token), 40)  # Should be longer than 40 chars
        self.assertLess(len(token), 100)  # But not crazy long

        # Token should be URL-safe (no special chars that need encoding)
        import re

        self.assertTrue(re.match(r"^[A-Za-z0-9_-]+$", token))

    def test_generate_unique_token_avoids_duplicates(self):
        """Test that the service avoids generating duplicate tokens"""
        # Create an invitation with a token
        token1 = self.service.generate_unique_token()
        invitation = Invitation.objects.create(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            token=token1,
            expires_at=timezone.now() + timedelta(days=7),
            invited_by=self.user,
        )

        # Generate another token - should be different
        token2 = self.service.generate_unique_token()
        self.assertNotEqual(token1, token2)

    @patch("apps.invitations.services.invitation_token_service.secrets.token_urlsafe")
    def test_generate_unique_token_handles_collision(self, mock_token_urlsafe):
        """Test handling of token collisions"""
        # Create an invitation with a specific token
        existing_token = "existing-token-123"
        invitation = Invitation.objects.create(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            token=existing_token,
            expires_at=timezone.now() + timedelta(days=7),
            invited_by=self.user,
        )

        # Mock token generation to return the existing token first, then a new one
        mock_token_urlsafe.side_effect = [existing_token, "new-unique-token"]

        token = self.service.generate_unique_token()

        # Should return the second token (the unique one)
        self.assertEqual(token, "new-unique-token")
        # Should have called the token generator twice
        self.assertEqual(mock_token_urlsafe.call_count, 2)

    @patch("apps.invitations.services.invitation_token_service.secrets.token_urlsafe")
    def test_generate_unique_token_raises_error_on_max_attempts(
        self, mock_token_urlsafe
    ):
        """Test that service raises error if it can't generate unique token"""
        # Create invitation with a token
        existing_token = "collision-token"
        invitation = Invitation.objects.create(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            token=existing_token,
            expires_at=timezone.now() + timedelta(days=7),
            invited_by=self.user,
        )

        # Mock to always return the same token (simulating impossible collision)
        mock_token_urlsafe.return_value = existing_token

        # Should raise RuntimeError after max attempts
        with self.assertRaises(RuntimeError) as cm:
            self.service.generate_unique_token()

        self.assertIn("Unable to generate unique token", str(cm.exception))

    def test_calculate_expiry_date_default(self):
        """Test default expiry date calculation"""
        before = timezone.now()
        expiry = self.service.calculate_expiry_date()
        after = timezone.now()

        # Should be 7 days from now
        expected_min = before + timedelta(days=7)
        expected_max = after + timedelta(days=7)

        self.assertGreaterEqual(expiry, expected_min)
        self.assertLessEqual(expiry, expected_max)

    def test_calculate_expiry_date_custom_days(self):
        """Test custom expiry date calculation"""
        custom_days = 14
        before = timezone.now()
        expiry = self.service.calculate_expiry_date(custom_days)
        after = timezone.now()

        # Should be 14 days from now
        expected_min = before + timedelta(days=custom_days)
        expected_max = after + timedelta(days=custom_days)

        self.assertGreaterEqual(expiry, expected_min)
        self.assertLessEqual(expiry, expected_max)

    def test_is_token_expired_with_future_date(self):
        """Test that future expiry dates are not expired"""
        future_date = timezone.now() + timedelta(days=1)
        self.assertFalse(self.service.is_token_expired(future_date))

    def test_is_token_expired_with_past_date(self):
        """Test that past expiry dates are expired"""
        past_date = timezone.now() - timedelta(days=1)
        self.assertTrue(self.service.is_token_expired(past_date))

    def test_is_token_expired_with_none(self):
        """Test that None expiry date is not expired"""
        self.assertFalse(self.service.is_token_expired(None))

    def test_validate_token_valid_pending_invitation(self):
        """Test validation of valid pending invitation token"""
        token = self.service.generate_unique_token()
        invitation = Invitation.objects.create(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            token=token,
            expires_at=timezone.now() + timedelta(days=7),
            invited_by=self.user,
            status="pending",
        )

        result = self.service.validate_token(token)

        self.assertTrue(result["is_valid"])
        self.assertEqual(result["invitation"], invitation)
        self.assertFalse(result["is_expired"])
        self.assertTrue(result["is_pending"])

    def test_validate_token_nonexistent_token(self):
        """Test validation of nonexistent token"""
        result = self.service.validate_token("nonexistent-token")

        self.assertFalse(result["is_valid"])
        self.assertEqual(result["error"], "invalid_token")
        self.assertIn("Invalid invitation token", result["message"])
        self.assertIsNone(result["invitation"])

    def test_validate_token_soft_deleted_invitation(self):
        """Test validation of soft-deleted invitation token"""
        token = self.service.generate_unique_token()
        invitation = Invitation.objects.create(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            token=token,
            expires_at=timezone.now() + timedelta(days=7),
            invited_by=self.user,
        )

        # Soft delete the invitation
        invitation.soft_delete()

        result = self.service.validate_token(token)

        self.assertFalse(result["is_valid"])
        self.assertEqual(result["error"], "deleted_invitation")
        self.assertIn("has been deleted", result["message"])

    def test_validate_token_expired_invitation(self):
        """Test validation of expired invitation token"""
        token = self.service.generate_unique_token()
        invitation = Invitation.objects.create(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            token=token,
            expires_at=timezone.now() - timedelta(days=1),  # Expired
            invited_by=self.user,
            status="pending",
        )

        result = self.service.validate_token(token)

        self.assertFalse(result["is_valid"])
        self.assertEqual(result["error"], "expired_token")
        self.assertIn("has expired", result["message"])
        self.assertTrue(result["is_expired"])

    def test_validate_token_accepted_invitation(self):
        """Test validation of already accepted invitation token"""
        token = self.service.generate_unique_token()
        invitation = Invitation.objects.create(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            token=token,
            expires_at=timezone.now() + timedelta(days=7),
            invited_by=self.user,
            status="accepted",
        )

        result = self.service.validate_token(token)

        self.assertFalse(result["is_valid"])
        self.assertEqual(result["error"], "invalid_status")
        self.assertIn("status is accepted", result["message"])
        self.assertFalse(result["is_pending"])

    def test_regenerate_token_success(self):
        """Test successful token regeneration"""
        old_token = self.service.generate_unique_token()
        old_expiry = timezone.now() + timedelta(days=1)

        invitation = Invitation.objects.create(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            token=old_token,
            expires_at=old_expiry,
            invited_by=self.user,
            status="expired",
        )

        result = self.service.regenerate_token(invitation)

        self.assertTrue(result["success"])
        self.assertEqual(result["old_token"], old_token)
        self.assertNotEqual(result["new_token"], old_token)
        self.assertGreater(result["expires_at"], old_expiry)

        # Check invitation was updated
        invitation.refresh_from_db()
        self.assertEqual(invitation.token, result["new_token"])
        self.assertEqual(invitation.expires_at, result["expires_at"])
        self.assertEqual(invitation.status, "pending")

    def test_regenerate_token_soft_deleted_invitation(self):
        """Test regeneration fails for soft-deleted invitation"""
        token = self.service.generate_unique_token()
        invitation = Invitation.objects.create(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            token=token,
            expires_at=timezone.now() + timedelta(days=7),
            invited_by=self.user,
        )

        invitation.soft_delete()

        result = self.service.regenerate_token(invitation)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "deleted_invitation")

    def test_get_token_info_valid_token(self):
        """Test getting comprehensive token information"""
        token = self.service.generate_unique_token()
        expires_at = timezone.now() + timedelta(days=7)

        invitation = Invitation.objects.create(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            token=token,
            expires_at=expires_at,
            invited_by=self.user,
            status="pending",
        )

        result = self.service.get_token_info(token)

        self.assertTrue(result["is_valid"])
        self.assertIn("token_info", result)

        token_info = result["token_info"]
        self.assertEqual(token_info["email"], "test@example.com")
        self.assertEqual(token_info["status"], "pending")
        self.assertEqual(token_info["expires_at"], expires_at)
        self.assertEqual(token_info["invited_by"], "inviter@example.com")
        self.assertIsNotNone(token_info["time_remaining"])

    def test_get_token_info_expired_token(self):
        """Test getting token info for expired token"""
        token = self.service.generate_unique_token()
        expires_at = timezone.now() - timedelta(days=1)

        invitation = Invitation.objects.create(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            token=token,
            expires_at=expires_at,
            invited_by=self.user,
            status="pending",
        )

        result = self.service.get_token_info(token)

        self.assertFalse(result["is_valid"])
        self.assertTrue(result["is_expired"])
        self.assertIn("token_info", result)

        token_info = result["token_info"]
        self.assertIsNone(token_info["time_remaining"])

    def test_get_token_info_invalid_token(self):
        """Test getting info for invalid token"""
        result = self.service.get_token_info("invalid-token")

        self.assertFalse(result["is_valid"])
        self.assertEqual(result["error"], "invalid_token")
        self.assertIsNone(result["invitation"])
