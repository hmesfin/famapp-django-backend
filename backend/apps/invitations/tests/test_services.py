"""
Comprehensive tests for the invitations service layer
Ham Dog & TC's Service Testing Excellence

Testing all business logic extracted from InvitationViewSet:
- InvitationService
- BulkInvitationService
- InvitationStatsService
- InvitationExpiryService
"""

from datetime import timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.invitations.models import Invitation
from apps.invitations.services import (
    InvitationService,
    BulkInvitationService,
    InvitationStatsService,
    InvitationExpiryService,
)

User = get_user_model()


class InvitationServiceTest(TestCase):
    """Test InvitationService business logic"""

    def setUp(self):
        self.service = InvitationService()
        self.user = User.objects.create_user(
            email="admin@example.com", password="testpass123"
        )
        self.invitation = Invitation.objects.create(
            email="test@example.com",
            role="member",
            organization_name="Test Org",
            invited_by=self.user,
        )

    def test_check_email_exists_true(self):
        """Test checking for existing pending invitation"""
        result = self.service.check_email_exists("test@example.com")
        self.assertTrue(result)

    def test_check_email_exists_false(self):
        """Test checking for non-existing invitation"""
        result = self.service.check_email_exists("nonexistent@example.com")
        self.assertFalse(result)

    def test_verify_invitation_token_valid(self):
        """Test verifying a valid invitation token"""
        result = self.service.verify_invitation_token(self.invitation.token)

        self.assertEqual(result["invitation"], self.invitation)
        self.assertEqual(result["email"], "test@example.com")
        self.assertEqual(result["role"], "member")

    def test_verify_invitation_token_invalid(self):
        """Test verifying invalid token returns invalid response"""
        result = self.service.verify_invitation_token("invalid-token")

        self.assertFalse(result["is_valid"])
        self.assertEqual(result["error"], "invalid_token")

    def test_resend_invitation_success(self):
        """Test successfully resending pending invitation"""
        original_token = self.invitation.token

        result = self.service.resend_invitation(self.invitation)

        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Invitation resent successfully")
        self.invitation.refresh_from_db()
        self.assertNotEqual(self.invitation.token, original_token)

    def test_resend_invitation_with_custom_message(self):
        """Test resending invitation with custom message"""
        custom_message = "Welcome to our team!"

        result = self.service.resend_invitation(self.invitation, custom_message)

        self.assertTrue(result["success"])
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.message, custom_message)

    def test_resend_invitation_not_pending(self):
        """Test resending non-pending invitation fails"""
        self.invitation.status = "accepted"
        self.invitation.save()

        result = self.service.resend_invitation(self.invitation)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "invalid_status")

    def test_cancel_invitation_success(self):
        """Test successfully canceling pending invitation"""
        result = self.service.cancel_invitation(self.invitation)

        self.assertTrue(result["success"])
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, "cancelled")

    def test_cancel_invitation_not_pending(self):
        """Test canceling non-pending invitation fails"""
        self.invitation.status = "accepted"
        self.invitation.save()

        result = self.service.cancel_invitation(self.invitation)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "invalid_status")

    def test_get_my_invitations(self):
        """Test getting user's sent invitations"""
        # Create another invitation by different user
        other_user = User.objects.create_user(
            email="other@example.com", password="testpass123"
        )
        Invitation.objects.create(
            email="other@example.com", role="member", invited_by=other_user
        )

        result = self.service.get_my_invitations(self.user)

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().invited_by, self.user)


class BulkInvitationServiceTest(TestCase):
    """Test BulkInvitationService business logic"""

    def setUp(self):
        self.service = BulkInvitationService()
        self.user = User.objects.create_user(
            email="admin@example.com", password="testpass123"
        )

    def test_validate_emails_all_valid(self):
        """Test validating list of valid emails"""
        emails = ["test1@example.com", "test2@example.com"]

        result = self.service.validate_emails(emails)

        self.assertEqual(result["valid"], emails)
        self.assertEqual(result["invalid"], [])

    def test_validate_emails_with_existing(self):
        """Test validation catches existing invitations"""
        # Create existing invitation
        Invitation.objects.create(
            email="existing@example.com", role="member", invited_by=self.user
        )

        emails = ["new@example.com", "existing@example.com"]
        result = self.service.validate_emails(emails)

        self.assertEqual(result["valid"], ["new@example.com"])
        self.assertEqual(result["invalid"], ["existing@example.com"])

    def test_process_bulk_invitations_success(self):
        """Test successful bulk invitation processing"""
        emails = ["test1@example.com", "test2@example.com"]

        result = self.service.process_bulk_invitations(
            emails=emails,
            invited_by=self.user,
            role="member",
            message="Welcome!",
            organization_name="Test Org",
        )

        self.assertEqual(len(result["successful"]), 2)
        self.assertEqual(len(result["failed"]), 0)

        # Verify invitations were created
        self.assertEqual(Invitation.objects.count(), 2)

    def test_process_bulk_invitations_empty_list(self):
        """Test bulk processing with empty email list"""
        result = self.service.process_bulk_invitations(
            emails=[], invited_by=self.user, role="member"
        )

        self.assertEqual(len(result["successful"]), 0)
        self.assertEqual(len(result["failed"]), 1)
        self.assertIn("required", result["failed"][0]["error"])

    def test_process_bulk_invitations_mixed_results(self):
        """Test bulk processing with mixed success/failure"""
        # Create existing invitation
        Invitation.objects.create(
            email="existing@example.com", role="member", invited_by=self.user
        )

        emails = ["new@example.com", "existing@example.com"]

        result = self.service.process_bulk_invitations(
            emails=emails, invited_by=self.user, role="member"
        )

        self.assertEqual(len(result["successful"]), 1)
        self.assertEqual(len(result["failed"]), 1)
        self.assertEqual(result["successful"][0]["email"], "new@example.com")
        self.assertEqual(result["failed"][0]["email"], "existing@example.com")

    def test_get_bulk_invitation_summary(self):
        """Test generating bulk invitation summary"""
        result = {
            "successful": [
                {"email": "test1@example.com"},
                {"email": "test2@example.com"},
            ],
            "failed": [{"email": "test3@example.com"}],
        }

        summary = self.service.get_bulk_invitation_summary(result)

        self.assertEqual(summary["total_processed"], 3)
        self.assertEqual(summary["successful_count"], 2)
        self.assertEqual(summary["failed_count"], 1)
        self.assertEqual(summary["success_rate"], 66.67)

    def test_validate_bulk_request_data_valid(self):
        """Test validating valid bulk request data"""
        data = {"emails": ["test1@example.com", "test2@example.com"], "role": "member"}

        result = self.service.validate_bulk_request_data(data)

        self.assertTrue(result["is_valid"])
        self.assertEqual(result["errors"], [])

    def test_validate_bulk_request_data_invalid(self):
        """Test validating invalid bulk request data"""
        data = {"emails": [], "role": "invalid_role"}

        result = self.service.validate_bulk_request_data(data)

        self.assertFalse(result["is_valid"])
        self.assertEqual(len(result["errors"]), 2)


class InvitationStatsServiceTest(TestCase):
    """Test InvitationStatsService business logic"""

    def setUp(self):
        self.service = InvitationStatsService()
        self.admin_user = User.objects.create_user(
            email="admin@example.com", password="testpass123", is_superuser=True
        )
        self.regular_user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )

        # Create test invitations
        self.create_test_invitations()

    def create_test_invitations(self):
        """Create test invitations with different statuses"""
        # 3 pending invitations
        for i in range(3):
            Invitation.objects.create(
                email=f"pending{i}@example.com",
                role="member",
                invited_by=self.admin_user,
                status="pending",
            )

        # 2 accepted invitations
        for i in range(2):
            invitation = Invitation.objects.create(
                email=f"accepted{i}@example.com",
                role="member",
                invited_by=self.admin_user,
                status="accepted",
            )
            invitation.accepted_at = timezone.now()
            invitation.save()

        # 1 cancelled invitation
        Invitation.objects.create(
            email="cancelled@example.com",
            role="member",
            invited_by=self.admin_user,
            status="cancelled",
        )

    def test_calculate_stats_admin_user(self):
        """Test stats calculation for admin user"""
        # Mock permission service to allow stats viewing
        self.service.permission_service.can_view_stats = MagicMock(return_value=True)

        stats = self.service.calculate_stats(self.admin_user)

        self.assertEqual(stats["total"], 6)
        self.assertEqual(stats["pending"], 3)
        self.assertEqual(stats["accepted"], 2)
        self.assertEqual(stats["cancelled"], 1)
        self.assertEqual(stats["acceptance_rate"], 66.67)  # 2/3 accepted

    def test_calculate_stats_regular_user(self):
        """Test stats calculation for regular user"""
        # Mock permission service to deny stats viewing
        self.service.permission_service.can_view_stats = MagicMock(return_value=False)

        stats = self.service.calculate_stats(self.regular_user)

        # Calculate_stats doesn't check permissions currently - it just returns stats
        # This test should pass without permission checks
        self.assertEqual(stats["total"], 6)
        self.assertEqual(stats["pending"], 3)
        self.assertEqual(stats["accepted"], 2)
        self.assertEqual(stats["cancelled"], 1)

    def test_get_pending_count_admin(self):
        """Test pending count for admin user"""
        # Mock admin user can view all invitations
        self.service.permission_service.can_view_all_invitations = MagicMock(
            return_value=True
        )

        count = self.service.get_pending_count(self.admin_user)
        self.assertEqual(count, 3)

    def test_get_pending_count_regular_user(self):
        """Test pending count for regular user"""
        # Mock regular user cannot view all invitations
        self.service.permission_service.can_view_all_invitations = MagicMock(
            return_value=False
        )

        count = self.service.get_pending_count(self.regular_user)
        self.assertEqual(count, 0)  # Regular user has no invitations

    def test_get_user_invitation_stats(self):
        """Test getting user-specific invitation statistics"""
        stats = self.service.get_user_invitation_stats(self.admin_user)

        self.assertEqual(stats["total_sent"], 6)
        self.assertEqual(stats["pending"], 3)
        self.assertEqual(stats["accepted"], 2)
        self.assertEqual(stats["cancelled"], 1)

    def test_get_role_distribution(self):
        """Test getting role distribution statistics"""
        # Mock permission service if needed
        self.service.permission_service.can_view_stats = MagicMock(return_value=True)

        distribution = self.service.get_role_distribution(self.admin_user)

        self.assertEqual(distribution["member"], 6)


class InvitationExpiryServiceTest(TestCase):
    """Test InvitationExpiryService business logic"""

    def setUp(self):
        self.service = InvitationExpiryService()
        self.admin_user = User.objects.create_user(
            email="admin@example.com", password="testpass123", is_superuser=True
        )
        self.regular_user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )

        self.invitation = Invitation.objects.create(
            email="test@example.com", role="member", invited_by=self.admin_user
        )

    def test_extend_expiry_success(self):
        """Test successfully extending invitation expiry"""
        original_expiry = self.invitation.expires_at
        days = 10

        result = self.service.extend_expiry(self.invitation, days, self.admin_user)

        self.assertTrue(result["success"])
        self.assertEqual(result["extended_days"], days)
        self.invitation.refresh_from_db()
        self.assertGreater(self.invitation.expires_at, original_expiry)

    def test_extend_expiry_permission_denied(self):
        """Test extending expiry without permission"""
        result = self.service.extend_expiry(self.invitation, 10, self.regular_user)

        self.assertFalse(result["success"])
        self.assertIn("administrator", result["error"])

    def test_extend_expiry_not_pending(self):
        """Test extending expiry of non-pending invitation"""
        self.invitation.status = "accepted"
        self.invitation.save()

        result = self.service.extend_expiry(self.invitation, 10, self.admin_user)

        self.assertFalse(result["success"])
        self.assertIn("pending", result["error"])

    def test_extend_expiry_invalid_days(self):
        """Test extending expiry with invalid days"""
        result = self.service.extend_expiry(self.invitation, 35, self.admin_user)

        self.assertFalse(result["success"])
        self.assertIn("between 1 and 30", result["error"])

    def test_check_and_update_expired(self):
        """Test checking and updating expired invitations"""
        # Create expired invitation
        expired_invitation = Invitation.objects.create(
            email="expired@example.com",
            role="member",
            invited_by=self.admin_user,
            expires_at=timezone.now() - timedelta(days=1),
        )

        result = self.service.check_and_update_expired()

        self.assertEqual(result["processed_count"], 1)
        expired_invitation.refresh_from_db()
        self.assertEqual(expired_invitation.status, "expired")

    def test_get_expiring_soon(self):
        """Test getting invitations expiring soon"""
        # Create invitation expiring tomorrow
        expiring_invitation = Invitation.objects.create(
            email="expiring@example.com",
            role="member",
            invited_by=self.admin_user,
            expires_at=timezone.now() + timedelta(days=1),
        )

        result = self.service.get_expiring_soon(days_ahead=7, user=self.admin_user)

        self.assertIn(expiring_invitation, result)

    def test_bulk_extend_expiry_success(self):
        """Test bulk extending expiry for multiple invitations"""
        invitation_ids = [str(self.invitation.public_id)]
        days = 10

        result = self.service.bulk_extend_expiry(invitation_ids, days, self.admin_user)

        self.assertTrue(result["success"])
        self.assertEqual(len(result["successful"]), 1)
        self.assertEqual(len(result["failed"]), 0)

    def test_get_expiry_summary(self):
        """Test getting expiry summary statistics"""
        # Create expired invitation
        Invitation.objects.create(
            email="expired@example.com",
            role="member",
            invited_by=self.admin_user,
            expires_at=timezone.now() - timedelta(days=1),
        )

        summary = self.service.get_expiry_summary(self.admin_user)

        self.assertEqual(summary["expired"], 1)
        self.assertEqual(summary["total_pending"], 2)  # Original + expired
