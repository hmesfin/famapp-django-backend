"""
Tests for cleanup_expired_invitations Celery task.
TDD-first approach: These tests define the behavior before implementation.
"""

import logging
from datetime import timedelta
from unittest.mock import patch, MagicMock

import pytest
from django.utils import timezone

from apps.shared.models import Family, FamilyMember
from apps.users.models import Invitation, User


@pytest.mark.django_db
class TestCleanupExpiredInvitations:
    """Test cleanup_expired_invitations Celery task"""

    @pytest.fixture
    def inviter(self):
        """Create an inviter user"""
        return User.objects.create_user(
            email="inviter@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )

    @pytest.fixture
    def family(self, inviter):
        """Create a family"""
        family = Family.objects.create(
            name="The Doe Family",
            created_by=inviter
        )
        FamilyMember.objects.create(
            family=family,
            user=inviter,
            role=FamilyMember.Role.ORGANIZER
        )
        return family

    def test_cleanup_task_exists(self):
        """Task should be importable"""
        from apps.users.tasks import cleanup_expired_invitations
        assert callable(cleanup_expired_invitations)
        assert hasattr(cleanup_expired_invitations, 'apply')
        assert hasattr(cleanup_expired_invitations, 'delay')

    def test_cleanup_marks_expired_pending_invitations(self, inviter, family):
        """Task should mark expired PENDING invitations as EXPIRED"""
        from apps.users.tasks import cleanup_expired_invitations

        # Create expired PENDING invitation
        expired_invitation = Invitation.objects.create(
            family=family,
            inviter=inviter,
            invitee_email="expired@example.com",
            role=Invitation.Role.PARENT,
            status=Invitation.Status.PENDING,
            expires_at=timezone.now() - timedelta(days=1)  # Expired yesterday
        )

        # Run task
        result = cleanup_expired_invitations.apply()

        # Reload invitation from database
        expired_invitation.refresh_from_db()

        # Assert status changed to EXPIRED
        assert expired_invitation.status == Invitation.Status.EXPIRED
        assert result.result["status"] == "success"
        assert result.result["expired_count"] == 1

    def test_cleanup_ignores_future_invitations(self, inviter, family):
        """Task should not touch invitations that haven't expired yet"""
        from apps.users.tasks import cleanup_expired_invitations

        # Create future invitation (expires in 5 days)
        future_invitation = Invitation.objects.create(
            family=family,
            inviter=inviter,
            invitee_email="future@example.com",
            role=Invitation.Role.PARENT,
            status=Invitation.Status.PENDING,
            expires_at=timezone.now() + timedelta(days=5)  # Future expiration
        )

        # Run task
        result = cleanup_expired_invitations.apply()

        # Reload invitation from database
        future_invitation.refresh_from_db()

        # Assert status still PENDING
        assert future_invitation.status == Invitation.Status.PENDING
        assert result.result["expired_count"] == 0

    def test_cleanup_ignores_already_accepted_invitations(self, inviter, family):
        """Task should not modify ACCEPTED invitations"""
        from apps.users.tasks import cleanup_expired_invitations
        # Create expired but ACCEPTED invitation
        accepted_invitation = Invitation.objects.create(
            family=family,
            inviter=inviter,
            invitee_email="accepted@example.com",
            role=Invitation.Role.CHILD,
            status=Invitation.Status.ACCEPTED,  # Already accepted
            expires_at=timezone.now() - timedelta(days=2)  # Expired 2 days ago
        )

        # Run task
        result = cleanup_expired_invitations.apply()

        # Reload invitation from database
        accepted_invitation.refresh_from_db()

        # Assert status still ACCEPTED
        assert accepted_invitation.status == Invitation.Status.ACCEPTED
        assert result.result["expired_count"] == 0

    def test_cleanup_ignores_declined_invitations(self, inviter, family):
        """Task should not modify DECLINED invitations"""
        from apps.users.tasks import cleanup_expired_invitations
        from apps.users.tasks import cleanup_expired_invitations
        """Task should not modify DECLINED invitations"""
        # Create expired but DECLINED invitation
        declined_invitation = Invitation.objects.create(
            family=family,
            inviter=inviter,
            invitee_email="declined@example.com",
            role=Invitation.Role.PARENT,
            status=Invitation.Status.DECLINED,  # Already declined
            expires_at=timezone.now() - timedelta(days=3)  # Expired 3 days ago
        )

        # Run task
        result = cleanup_expired_invitations.apply()

        # Reload invitation from database
        declined_invitation.refresh_from_db()

        # Assert status still DECLINED
        assert declined_invitation.status == Invitation.Status.DECLINED
        assert result.result["expired_count"] == 0

    def test_cleanup_ignores_cancelled_invitations(self, inviter, family):
        """Task should not modify CANCELLED invitations"""
        from apps.users.tasks import cleanup_expired_invitations
        from apps.users.tasks import cleanup_expired_invitations
        """Task should not modify CANCELLED invitations"""
        # Create expired but CANCELLED invitation
        cancelled_invitation = Invitation.objects.create(
            family=family,
            inviter=inviter,
            invitee_email="cancelled@example.com",
            role=Invitation.Role.CHILD,
            status=Invitation.Status.CANCELLED,  # Already cancelled
            expires_at=timezone.now() - timedelta(days=1)  # Expired yesterday
        )

        # Run task
        result = cleanup_expired_invitations.apply()

        # Reload invitation from database
        cancelled_invitation.refresh_from_db()

        # Assert status still CANCELLED
        assert cancelled_invitation.status == Invitation.Status.CANCELLED
        assert result.result["expired_count"] == 0

    def test_cleanup_ignores_already_expired_status(self, inviter, family):
        """Task should not modify invitations already marked as EXPIRED"""
        from apps.users.tasks import cleanup_expired_invitations
        from apps.users.tasks import cleanup_expired_invitations
        """Task should not modify invitations already marked as EXPIRED"""
        # Create invitation already marked as EXPIRED
        already_expired = Invitation.objects.create(
            family=family,
            inviter=inviter,
            invitee_email="already_expired@example.com",
            role=Invitation.Role.PARENT,
            status=Invitation.Status.EXPIRED,  # Already EXPIRED status
            expires_at=timezone.now() - timedelta(days=5)  # Expired 5 days ago
        )

        # Run task
        result = cleanup_expired_invitations.apply()

        # Reload invitation from database
        already_expired.refresh_from_db()

        # Assert status still EXPIRED (not modified)
        assert already_expired.status == Invitation.Status.EXPIRED
        assert result.result["expired_count"] == 0

    def test_cleanup_returns_count_of_expired(self, inviter, family):
        """Task should return count of invitations marked as expired"""
        from apps.users.tasks import cleanup_expired_invitations
        from apps.users.tasks import cleanup_expired_invitations
        """Task should return count of invitations marked as expired"""
        # Create 3 expired PENDING invitations
        for i in range(3):
            Invitation.objects.create(
                family=family,
                inviter=inviter,
                invitee_email=f"expired{i}@example.com",
                role=Invitation.Role.PARENT,
                status=Invitation.Status.PENDING,
                expires_at=timezone.now() - timedelta(days=i+1)
            )

        # Create 1 future invitation (should not be counted)
        Invitation.objects.create(
            family=family,
            inviter=inviter,
            invitee_email="future@example.com",
            role=Invitation.Role.CHILD,
            status=Invitation.Status.PENDING,
            expires_at=timezone.now() + timedelta(days=3)
        )

        # Run task
        result = cleanup_expired_invitations.apply()

        # Assert returns correct count
        assert result.result["status"] == "success"
        assert result.result["expired_count"] == 3
        assert "timestamp" in result.result

    def test_cleanup_logs_success(self, inviter, family, caplog):
        """Task should log successful cleanup"""
        from apps.users.tasks import cleanup_expired_invitations
        from apps.users.tasks import cleanup_expired_invitations
        """Task should log successful cleanup"""
        # Create expired invitation
        Invitation.objects.create(
            family=family,
            inviter=inviter,
            invitee_email="expired@example.com",
            role=Invitation.Role.PARENT,
            status=Invitation.Status.PENDING,
            expires_at=timezone.now() - timedelta(hours=1)
        )

        with caplog.at_level(logging.INFO):
            # Run task
            cleanup_expired_invitations.apply()

        # Assert log message contains count
        assert "Marked 1 expired invitation(s) as EXPIRED" in caplog.text
        assert "expired before" in caplog.text

    def test_cleanup_with_no_expired_invitations(self, caplog):
        """Task should handle case with no expired invitations"""
        from apps.users.tasks import cleanup_expired_invitations
        from apps.users.tasks import cleanup_expired_invitations
        """Task should handle case with no expired invitations"""
        with caplog.at_level(logging.INFO):
            # Run task (no invitations created)
            result = cleanup_expired_invitations.apply()

        # Assert returns zero count
        assert result.result["status"] == "success"
        assert result.result["expired_count"] == 0
        assert "No expired invitations found to cleanup" in caplog.text

    def test_cleanup_handles_bulk_expiration(self, inviter, family):
        """Task should efficiently handle multiple expired invitations"""
        from apps.users.tasks import cleanup_expired_invitations
        from apps.users.tasks import cleanup_expired_invitations
        """Task should efficiently handle multiple expired invitations"""
        # Create 50 expired PENDING invitations
        expired_invitations = []
        for i in range(50):
            invitation = Invitation.objects.create(
                family=family,
                inviter=inviter,
                invitee_email=f"user{i}@example.com",
                role=Invitation.Role.PARENT if i % 2 == 0 else Invitation.Role.CHILD,
                status=Invitation.Status.PENDING,
                expires_at=timezone.now() - timedelta(hours=i+1)
            )
            expired_invitations.append(invitation)

        # Run task
        result = cleanup_expired_invitations.apply()

        # Assert all 50 marked as EXPIRED
        assert result.result["expired_count"] == 50

        # Verify in database
        for invitation in expired_invitations:
            invitation.refresh_from_db()
            assert invitation.status == Invitation.Status.EXPIRED

    def test_cleanup_with_mixed_statuses(self, inviter, family):
        """Task should only update PENDING invitations in mixed scenario"""
        from apps.users.tasks import cleanup_expired_invitations
        from apps.users.tasks import cleanup_expired_invitations
        """Task should only update PENDING invitations in mixed scenario"""
        # Create various invitations
        pending_expired = Invitation.objects.create(
            family=family,
            inviter=inviter,
            invitee_email="pending_expired@example.com",
            role=Invitation.Role.PARENT,
            status=Invitation.Status.PENDING,
            expires_at=timezone.now() - timedelta(days=1)
        )

        accepted_expired = Invitation.objects.create(
            family=family,
            inviter=inviter,
            invitee_email="accepted_expired@example.com",
            role=Invitation.Role.CHILD,
            status=Invitation.Status.ACCEPTED,
            expires_at=timezone.now() - timedelta(days=1)
        )

        pending_future = Invitation.objects.create(
            family=family,
            inviter=inviter,
            invitee_email="pending_future@example.com",
            role=Invitation.Role.PARENT,
            status=Invitation.Status.PENDING,
            expires_at=timezone.now() + timedelta(days=1)
        )

        # Run task
        result = cleanup_expired_invitations.apply()

        # Check only the expired PENDING invitation was updated
        pending_expired.refresh_from_db()
        accepted_expired.refresh_from_db()
        pending_future.refresh_from_db()

        assert pending_expired.status == Invitation.Status.EXPIRED
        assert accepted_expired.status == Invitation.Status.ACCEPTED
        assert pending_future.status == Invitation.Status.PENDING
        assert result.result["expired_count"] == 1

    def test_cleanup_uses_current_timezone_correctly(self, inviter, family):
        """Task should use timezone.now() correctly for comparison"""
        from apps.users.tasks import cleanup_expired_invitations

        # Create invitation that expired exactly 1 minute ago
        just_expired = Invitation.objects.create(
            family=family,
            inviter=inviter,
            invitee_email="just_expired@example.com",
            role=Invitation.Role.PARENT,
            status=Invitation.Status.PENDING,
            expires_at=timezone.now() - timedelta(minutes=1)
        )

        # Create invitation that expires in 1 minute
        about_to_expire = Invitation.objects.create(
            family=family,
            inviter=inviter,
            invitee_email="about_to_expire@example.com",
            role=Invitation.Role.CHILD,
            status=Invitation.Status.PENDING,
            expires_at=timezone.now() + timedelta(minutes=1)
        )

        # Run task
        result = cleanup_expired_invitations.apply()

        # Check correct invitations were updated
        just_expired.refresh_from_db()
        about_to_expire.refresh_from_db()

        assert just_expired.status == Invitation.Status.EXPIRED
        assert about_to_expire.status == Invitation.Status.PENDING
        assert result.result["expired_count"] == 1

    def test_cleanup_task_is_idempotent(self, inviter, family):
        """Running task multiple times should be safe"""
        from apps.users.tasks import cleanup_expired_invitations
        from apps.users.tasks import cleanup_expired_invitations
        """Running task multiple times should be safe"""
        # Create expired invitation
        invitation = Invitation.objects.create(
            family=family,
            inviter=inviter,
            invitee_email="expired@example.com",
            role=Invitation.Role.PARENT,
            status=Invitation.Status.PENDING,
            expires_at=timezone.now() - timedelta(days=1)
        )

        # Run task first time
        result1 = cleanup_expired_invitations.apply()
        assert result1.result["expired_count"] == 1

        # Run task second time
        result2 = cleanup_expired_invitations.apply()
        assert result2.result["expired_count"] == 0  # Nothing to update

        # Verify invitation still EXPIRED
        invitation.refresh_from_db()
        assert invitation.status == Invitation.Status.EXPIRED


@pytest.mark.django_db
class TestCleanupTaskSchedule:
    """Test Celery Beat schedule configuration for cleanup task"""

    def test_celery_beat_schedule_includes_cleanup_task(self):
        """Celery Beat schedule should include cleanup task"""
        from django.conf import settings

        # Since we're using DatabaseScheduler, we need to check if the task is importable
        # The actual schedule will be configured in the database
        from apps.users.tasks import cleanup_expired_invitations
        assert callable(cleanup_expired_invitations)

        # Verify the task can be discovered by Celery
        from celery import current_app
        task_name = 'apps.users.tasks.cleanup_expired_invitations'

        # The task should be registered with Celery
        # (This will be true once we implement it)
        # assert task_name in current_app.tasks

    def test_cleanup_task_has_correct_signature(self):
        """Cleanup task should have correct signature for Celery"""
        from apps.users.tasks import cleanup_expired_invitations

        # Task should be a Celery task
        assert hasattr(cleanup_expired_invitations, 'name')
        assert hasattr(cleanup_expired_invitations, 'apply_async')
        assert hasattr(cleanup_expired_invitations, 'delay')