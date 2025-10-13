"""
Test suite for InvitationStatusService
Testing status transitions and validation logic

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
from apps.invitations.services.invitation_status_service import InvitationStatusService

User = get_user_model()


class InvitationStatusServiceTest(TestCase):
    """Test cases for InvitationStatusService"""

    def setUp(self):
        """Set up test data"""
        self.service = InvitationStatusService()
        self.inviter = User.objects.create_user(
            email='inviter@example.com',
            password='password123',
            first_name='John',
            last_name='Inviter'
        )
        self.accepter = User.objects.create_user(
            email='accepter@example.com',
            password='password123',
            first_name='Accept',
            last_name='User'
        )

    def test_validate_status_transition_valid(self):
        """Test valid status transitions"""
        valid_transitions = [
            ('pending', 'accepted'),
            ('pending', 'expired'),
            ('pending', 'cancelled'),
            ('expired', 'pending'),
            ('cancelled', 'pending'),
        ]
        
        for from_status, to_status in valid_transitions:
            with self.subTest(from_status=from_status, to_status=to_status):
                result = self.service.validate_status_transition(from_status, to_status)
                self.assertTrue(result['is_valid'])
                self.assertEqual(result['from_status'], from_status)
                self.assertEqual(result['to_status'], to_status)

    def test_validate_status_transition_invalid(self):
        """Test invalid status transitions"""
        invalid_transitions = [
            ('accepted', 'pending'),
            ('accepted', 'cancelled'),
            ('accepted', 'expired'),
            ('pending', 'invalid_status'),
        ]
        
        for from_status, to_status in invalid_transitions:
            with self.subTest(from_status=from_status, to_status=to_status):
                result = self.service.validate_status_transition(from_status, to_status)
                self.assertFalse(result['is_valid'])
                self.assertIn('error', result)

    def test_validate_status_transition_invalid_current_status(self):
        """Test validation with invalid current status"""
        result = self.service.validate_status_transition('invalid_status', 'pending')
        
        self.assertFalse(result['is_valid'])
        self.assertEqual(result['error'], 'invalid_current_status')

    def test_can_accept_valid_pending_invitation(self):
        """Test that valid pending invitation can be accepted"""
        invitation = Invitation.objects.create(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            token='test-token-123',
            expires_at=timezone.now() + timedelta(days=7),
            invited_by=self.inviter,
            status='pending'
        )
        
        result = self.service.can_accept(invitation)
        
        self.assertTrue(result['can_accept'])
        self.assertEqual(result['invitation'], invitation)

    def test_can_accept_soft_deleted_invitation(self):
        """Test that soft-deleted invitation cannot be accepted"""
        invitation = Invitation.objects.create(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            token='test-token-123',
            expires_at=timezone.now() + timedelta(days=7),
            invited_by=self.inviter,
            status='pending'
        )
        invitation.soft_delete()
        
        result = self.service.can_accept(invitation)
        
        self.assertFalse(result['can_accept'])
        self.assertEqual(result['error'], 'deleted_invitation')

    def test_can_accept_non_pending_invitation(self):
        """Test that non-pending invitation cannot be accepted"""
        for status in ['accepted', 'expired', 'cancelled']:
            with self.subTest(status=status):
                invitation = Invitation.objects.create(
                    email=f'test-{status}@example.com',
                    first_name='Test',
                    last_name='User',
                    token=f'test-token-{status}',
                    expires_at=timezone.now() + timedelta(days=7),
                    invited_by=self.inviter,
                    status=status
                )
                
                result = self.service.can_accept(invitation)
                
                self.assertFalse(result['can_accept'])
                self.assertEqual(result['error'], 'invalid_status')

    def test_can_accept_expired_invitation(self):
        """Test that expired invitation cannot be accepted"""
        invitation = Invitation.objects.create(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            token='test-token-123',
            expires_at=timezone.now() - timedelta(days=1),  # Expired
            invited_by=self.inviter,
            status='pending'
        )
        
        result = self.service.can_accept(invitation)
        
        self.assertFalse(result['can_accept'])
        self.assertEqual(result['error'], 'expired')

    def test_can_accept_existing_user(self):
        """Test that invitation for existing user cannot be accepted"""
        invitation = Invitation.objects.create(
            email=self.accepter.email,  # User already exists
            first_name='Test',
            last_name='User',
            token='test-token-123',
            expires_at=timezone.now() + timedelta(days=7),
            invited_by=self.inviter,
            status='pending'
        )
        
        result = self.service.can_accept(invitation)
        
        self.assertFalse(result['can_accept'])
        self.assertEqual(result['error'], 'user_exists')

    def test_can_cancel_pending_invitation(self):
        """Test that pending invitation can be cancelled"""
        invitation = Invitation.objects.create(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            token='test-token-123',
            expires_at=timezone.now() + timedelta(days=7),
            invited_by=self.inviter,
            status='pending'
        )
        
        result = self.service.can_cancel(invitation)
        
        self.assertTrue(result['can_cancel'])

    def test_can_cancel_non_pending_invitation(self):
        """Test that non-pending invitation cannot be cancelled"""
        for status in ['accepted', 'expired', 'cancelled']:
            with self.subTest(status=status):
                invitation = Invitation.objects.create(
                    email=f'test-{status}@example.com',
                    first_name='Test',
                    last_name='User',
                    token=f'test-token-{status}',
                    expires_at=timezone.now() + timedelta(days=7),
                    invited_by=self.inviter,
                    status=status
                )
                
                result = self.service.can_cancel(invitation)
                
                self.assertFalse(result['can_cancel'])
                self.assertEqual(result['error'], 'invalid_status')

    def test_can_resend_pending_invitation(self):
        """Test that pending invitations can be resent"""
        invitation = Invitation.objects.create(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            token='test-token-123',
            expires_at=timezone.now() + timedelta(days=7),
            invited_by=self.inviter,
            status='pending'
        )
        
        result = self.service.can_resend(invitation)
        
        self.assertTrue(result['can_resend'])

    def test_can_resend_non_pending_invitation(self):
        """Test that non-pending invitations cannot be resent"""
        for status in ['expired', 'cancelled']:
            with self.subTest(status=status):
                invitation = Invitation.objects.create(
                    email=f'test-{status}@example.com',
                    first_name='Test',
                    last_name='User',
                    token=f'test-token-{status}',
                    expires_at=timezone.now() + timedelta(days=7),
                    invited_by=self.inviter,
                    status=status
                )
                
                result = self.service.can_resend(invitation)
                
                self.assertFalse(result['can_resend'])
                self.assertEqual(result['error'], 'invalid_status')

    def test_can_resend_accepted_invitation(self):
        """Test that accepted invitation cannot be resent"""
        invitation = Invitation.objects.create(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            token='test-token-123',
            expires_at=timezone.now() + timedelta(days=7),
            invited_by=self.inviter,
            status='accepted'
        )
        
        result = self.service.can_resend(invitation)
        
        self.assertFalse(result['can_resend'])
        self.assertEqual(result['error'], 'invalid_status')

    def test_accept_invitation_success(self):
        """Test successful invitation acceptance"""
        invitation = Invitation.objects.create(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            token='test-token-123',
            expires_at=timezone.now() + timedelta(days=7),
            invited_by=self.inviter,
            status='pending'
        )
        
        # Create a different user for acceptance
        accepting_user = User.objects.create_user(
            email='different@example.com',
            password='password123'
        )
        
        result = self.service.accept_invitation(invitation, accepting_user)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['old_status'], 'pending')
        self.assertEqual(result['new_status'], 'accepted')
        self.assertIsNotNone(result['accepted_at'])
        
        # Check invitation was updated
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, 'accepted')
        self.assertEqual(invitation.accepted_by, accepting_user)
        self.assertIsNotNone(invitation.accepted_at)

    def test_accept_invitation_cannot_accept(self):
        """Test acceptance fails when invitation cannot be accepted"""
        invitation = Invitation.objects.create(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            token='test-token-123',
            expires_at=timezone.now() + timedelta(days=7),
            invited_by=self.inviter,
            status='accepted'  # Already accepted
        )
        
        result = self.service.accept_invitation(invitation, self.accepter)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_cancel_invitation_success(self):
        """Test successful invitation cancellation"""
        invitation = Invitation.objects.create(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            token='test-token-123',
            expires_at=timezone.now() + timedelta(days=7),
            invited_by=self.inviter,
            status='pending'
        )
        
        result = self.service.cancel_invitation(invitation)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['old_status'], 'pending')
        self.assertEqual(result['new_status'], 'cancelled')
        
        # Check invitation was updated
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, 'cancelled')

    def test_expire_invitation_success(self):
        """Test successful invitation expiration"""
        invitation = Invitation.objects.create(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            token='test-token-123',
            expires_at=timezone.now() + timedelta(days=7),
            invited_by=self.inviter,
            status='pending'
        )
        
        result = self.service.expire_invitation(invitation)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['old_status'], 'pending')
        self.assertEqual(result['new_status'], 'expired')
        
        # Check invitation was updated
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, 'expired')

    def test_expire_invitation_non_pending(self):
        """Test that non-pending invitation cannot be expired"""
        invitation = Invitation.objects.create(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            token='test-token-123',
            expires_at=timezone.now() + timedelta(days=7),
            invited_by=self.inviter,
            status='accepted'
        )
        
        result = self.service.expire_invitation(invitation)
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'invalid_status')

    def test_get_status_summary_pending_invitation(self):
        """Test status summary for pending invitation"""
        invitation = Invitation.objects.create(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            token='test-token-123',
            expires_at=timezone.now() + timedelta(days=7),
            invited_by=self.inviter,
            status='pending'
        )
        
        summary = self.service.get_status_summary(invitation)
        
        self.assertEqual(summary['current_status'], 'pending')
        self.assertFalse(summary['is_terminal'])
        self.assertTrue(summary['is_pending'])
        self.assertFalse(summary['is_accepted'])
        self.assertFalse(summary['is_expired'])
        self.assertFalse(summary['is_cancelled'])
        
        # Should have available actions for valid pending invitation
        self.assertIn('accept', summary['available_actions'])
        self.assertIn('cancel', summary['available_actions'])
        self.assertIn('resend', summary['available_actions'])

    def test_get_status_summary_accepted_invitation(self):
        """Test status summary for accepted invitation"""
        accepted_at = timezone.now()
        invitation = Invitation.objects.create(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            token='test-token-123',
            expires_at=timezone.now() + timedelta(days=7),
            invited_by=self.inviter,
            status='accepted',
            accepted_by=self.accepter,
            accepted_at=accepted_at
        )
        
        summary = self.service.get_status_summary(invitation)
        
        self.assertEqual(summary['current_status'], 'accepted')
        self.assertTrue(summary['is_terminal'])
        self.assertFalse(summary['is_pending'])
        self.assertTrue(summary['is_accepted'])
        self.assertEqual(summary['accepted_at'], accepted_at)
        self.assertEqual(summary['accepted_by'], self.accepter.email)
        
        # No actions available for accepted invitation
        self.assertEqual(len(summary['available_actions']), 0)

    def test_get_status_summary_expired_invitation_with_user_exists(self):
        """Test status summary for expired invitation when user exists"""
        invitation = Invitation.objects.create(
            email=self.accepter.email,  # User exists
            first_name='Test',
            last_name='User',
            token='test-token-123',
            expires_at=timezone.now() - timedelta(days=1),
            invited_by=self.inviter,
            status='expired'
        )
        
        summary = self.service.get_status_summary(invitation)
        
        self.assertEqual(summary['current_status'], 'expired')
        self.assertTrue(summary['is_expired'])
        
        # Cannot accept, resend, or cancel expired invitations in this refactoring
        self.assertNotIn('accept', summary['available_actions'])
        self.assertNotIn('resend', summary['available_actions'])
        self.assertNotIn('cancel', summary['available_actions'])  # Cannot cancel expired

    def test_get_status_summary_time_remaining(self):
        """Test status summary includes time remaining for non-expired invitations"""
        expires_at = timezone.now() + timedelta(days=7)
        invitation = Invitation.objects.create(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            token='test-token-123',
            expires_at=expires_at,
            invited_by=self.inviter,
            status='pending'
        )
        
        summary = self.service.get_status_summary(invitation)
        
        self.assertEqual(summary['expires_at'], expires_at)
        self.assertFalse(summary['is_time_expired'])
        self.assertIsNotNone(summary['time_remaining'])
        
        # Time remaining should be close to 7 days
        expected_remaining = timedelta(days=7)
        actual_remaining = summary['time_remaining']
        
        # Allow for small time differences in test execution
        self.assertAlmostEqual(
            actual_remaining.total_seconds(),
            expected_remaining.total_seconds(),
            delta=10  # 10 seconds tolerance
        )

    def test_bulk_expire_invitations_success(self):
        """Test bulk expiration of invitations"""
        # Create multiple pending invitations
        invitations = []
        for i in range(3):
            invitation = Invitation.objects.create(
                email=f'test{i}@example.com',
                first_name='Test',
                last_name='User',
                token=f'test-token-{i}',
                expires_at=timezone.now() + timedelta(days=7),
                invited_by=self.inviter,
                status='pending'
            )
            invitations.append(invitation)
        
        # Create one non-pending invitation
        non_pending = Invitation.objects.create(
            email='accepted@example.com',
            first_name='Accepted',
            last_name='User',
            token='accepted-token',
            expires_at=timezone.now() + timedelta(days=7),
            invited_by=self.inviter,
            status='accepted'
        )
        
        # Bulk expire all invitations
        all_invitations = Invitation.objects.all()
        result = self.service.bulk_expire_invitations(all_invitations)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['expired_count'], 3)  # Only pending ones
        
        # Check that pending invitations were expired
        for invitation in invitations:
            invitation.refresh_from_db()
            self.assertEqual(invitation.status, 'expired')
        
        # Check that accepted invitation wasn't changed
        non_pending.refresh_from_db()
        self.assertEqual(non_pending.status, 'accepted')

    def test_bulk_expire_invitations_no_pending(self):
        """Test bulk expiration when no pending invitations exist"""
        # Create only non-pending invitations
        Invitation.objects.create(
            email='accepted@example.com',
            first_name='Accepted',
            last_name='User',
            token='accepted-token',
            expires_at=timezone.now() + timedelta(days=7),
            invited_by=self.inviter,
            status='accepted'
        )
        
        all_invitations = Invitation.objects.all()
        result = self.service.bulk_expire_invitations(all_invitations)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['expired_count'], 0)
        self.assertIn('No pending invitations', result['message'])

    def test_bulk_expire_invitations_empty_queryset(self):
        """Test bulk expiration with empty queryset"""
        empty_qs = Invitation.objects.none()
        result = self.service.bulk_expire_invitations(empty_qs)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['expired_count'], 0)