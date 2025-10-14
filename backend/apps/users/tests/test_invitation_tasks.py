"""
Tests for invitation email Celery task.
TDD-first approach: These tests define the behavior before implementation.
"""

import logging
from datetime import datetime
from datetime import timedelta
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from celery.exceptions import Retry
from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from django.utils import timezone

from apps.shared.models import Family
from apps.shared.models import FamilyMember
from apps.users.models import Invitation
from apps.users.models import User
from apps.users.tasks import send_invitation_email


@pytest.mark.django_db
class TestSendInvitationEmail:
    """Test send_invitation_email Celery task"""

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

    @pytest.fixture
    def invitation(self, inviter, family):
        """Create an invitation"""
        return Invitation.objects.create(
            family=family,
            inviter=inviter,
            invitee_email="newmember@example.com",
            role="parent",
            expires_at=timezone.now() + timedelta(days=7),
        )

    def test_send_invitation_email_sends_email(self, invitation, settings):
        """Task sends email to invitee"""
        settings.CELERY_TASK_ALWAYS_EAGER = True

        # Execute task
        result = send_invitation_email.apply(args=[invitation.id])

        # Check email was sent
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.to == [invitation.invitee_email]
        assert result.result["status"] == "success"
        assert result.result["invitation_id"] == invitation.id

    def test_send_invitation_email_includes_inviter_name(self, invitation, settings):
        """Email includes inviter's name"""
        settings.CELERY_TASK_ALWAYS_EAGER = True

        # Execute task
        send_invitation_email.apply(args=[invitation.id])

        # Check email content
        email = mail.outbox[0]
        assert "John Doe" in email.body
        # Also check HTML version
        assert "John Doe" in email.alternatives[0][0] if email.alternatives else email.body

    def test_send_invitation_email_includes_family_name(self, invitation, settings):
        """Email includes family name"""
        settings.CELERY_TASK_ALWAYS_EAGER = True

        # Execute task
        send_invitation_email.apply(args=[invitation.id])

        # Check email content
        email = mail.outbox[0]
        assert "The Doe Family" in email.body
        assert invitation.family.name in email.subject

    def test_send_invitation_email_includes_role(self, invitation, settings):
        """Email includes role (Parent/Child)"""
        settings.CELERY_TASK_ALWAYS_EAGER = True

        # Execute task
        send_invitation_email.apply(args=[invitation.id])

        # Check email content includes human-readable role
        email = mail.outbox[0]
        assert "Parent" in email.body  # Should use get_role_display()

    def test_send_invitation_email_includes_token(self, invitation, settings):
        """Email includes invitation token"""
        settings.CELERY_TASK_ALWAYS_EAGER = True

        # Execute task
        send_invitation_email.apply(args=[invitation.id])

        # Check email content
        email = mail.outbox[0]
        assert str(invitation.token) in email.body

    def test_send_invitation_email_includes_accept_url(self, invitation, settings):
        """Email includes accept URL with token"""
        settings.CELERY_TASK_ALWAYS_EAGER = True
        settings.FRONTEND_URL = "http://localhost:5173"

        # Execute task
        send_invitation_email.apply(args=[invitation.id])

        # Check email content
        email = mail.outbox[0]
        expected_url = f"http://localhost:5173/invitations/{invitation.token}/accept"
        assert expected_url in email.body

    def test_send_invitation_email_includes_decline_url(self, invitation, settings):
        """Email includes decline URL with token"""
        settings.CELERY_TASK_ALWAYS_EAGER = True
        settings.FRONTEND_URL = "http://localhost:5173"

        # Execute task
        send_invitation_email.apply(args=[invitation.id])

        # Check email content
        email = mail.outbox[0]
        expected_url = f"http://localhost:5173/invitations/{invitation.token}/decline"
        assert expected_url in email.body

    def test_send_invitation_email_includes_expiration(self, invitation, settings):
        """Email includes expiration date"""
        settings.CELERY_TASK_ALWAYS_EAGER = True

        # Execute task
        send_invitation_email.apply(args=[invitation.id])

        # Check email content includes expiration info
        email = mail.outbox[0]
        # Check for formatted date (e.g., "January 20, 2025")
        formatted_date = invitation.expires_at.strftime("%B")
        assert formatted_date in email.body

    def test_send_invitation_email_logs_success(self, invitation, settings, caplog):
        """Task logs success message"""
        settings.CELERY_TASK_ALWAYS_EAGER = True

        with caplog.at_level(logging.INFO):
            # Execute task
            send_invitation_email.apply(args=[invitation.id])

        # Check logs
        assert f"Invitation email sent successfully to {invitation.invitee_email}" in caplog.text
        assert f"invitation_id={invitation.id}" in caplog.text

    def test_send_invitation_email_handles_missing_invitation(self, settings, caplog):
        """Task handles missing invitation gracefully"""
        settings.CELERY_TASK_ALWAYS_EAGER = True
        non_existent_id = 99999

        with caplog.at_level(logging.ERROR):
            # Execute task with non-existent invitation
            result = send_invitation_email.apply(args=[non_existent_id])

        # Should return error status, not raise exception
        assert result.result["status"] == "error"
        assert result.result["message"] == "Invitation not found"
        assert f"Invitation with id={non_existent_id} does not exist" in caplog.text

        # No email should be sent
        assert len(mail.outbox) == 0

    def test_send_invitation_email_retries_on_failure(self, invitation, settings):
        """Task retries on email send failure"""
        settings.CELERY_TASK_ALWAYS_EAGER = True  # Test with eager mode

        with patch('apps.users.tasks.send_mail') as mock_send:
            # Simulate email failure
            mock_send.side_effect = Exception("SMTP connection failed")

            # Execute task - it should handle the exception
            result = send_invitation_email.apply(args=[invitation.id])

            # In eager mode, exceptions are captured in result
            assert result.failed()
            assert "SMTP connection failed" in str(result.info)

    def test_send_invitation_email_uses_correct_from_email(self, invitation, settings):
        """Email uses DEFAULT_FROM_EMAIL from settings"""
        settings.CELERY_TASK_ALWAYS_EAGER = True
        settings.DEFAULT_FROM_EMAIL = "noreply@famapp.com"

        # Execute task
        send_invitation_email.apply(args=[invitation.id])

        # Check from email
        email = mail.outbox[0]
        assert email.from_email == "noreply@famapp.com"

    def test_send_invitation_email_has_both_html_and_text(self, invitation, settings):
        """Email has both HTML and plain text versions"""
        settings.CELERY_TASK_ALWAYS_EAGER = True

        # Execute task
        send_invitation_email.apply(args=[invitation.id])

        # Check email has both versions
        email = mail.outbox[0]
        assert email.body  # Plain text version
        assert email.alternatives  # HTML version
        assert email.alternatives[0][1] == "text/html"

    def test_send_invitation_email_handles_user_without_name(self, inviter, family, settings):
        """Email handles inviter without first/last name gracefully"""
        settings.CELERY_TASK_ALWAYS_EAGER = True

        # Create inviter with no name, only email
        anonymous_inviter = User.objects.create_user(
            email="anonymous@example.com",
            password="testpass123",
        )
        FamilyMember.objects.create(
            family=family,
            user=anonymous_inviter,
            role=FamilyMember.Role.PARENT
        )

        invitation = Invitation.objects.create(
            family=family,
            inviter=anonymous_inviter,
            invitee_email="newuser@example.com",
            role="child",
            expires_at=timezone.now() + timedelta(days=7),
        )

        # Execute task
        send_invitation_email.apply(args=[invitation.id])

        # Check email uses email address as fallback
        email = mail.outbox[0]
        assert "anonymous@example.com" in email.body

    def test_send_invitation_email_respects_frontend_url_setting(self, invitation, settings):
        """Task uses FRONTEND_URL from settings for links"""
        settings.CELERY_TASK_ALWAYS_EAGER = True
        settings.FRONTEND_URL = "https://app.famapp.com"

        # Execute task
        send_invitation_email.apply(args=[invitation.id])

        # Check URLs use production domain
        email = mail.outbox[0]
        assert "https://app.famapp.com/invitations/" in email.body
        assert "http://localhost" not in email.body


@pytest.mark.django_db
class TestInvitationEmailIntegration:
    """Integration tests for invitation email sending"""

    @pytest.fixture
    def api_client(self):
        """Create API client"""
        from rest_framework.test import APIClient
        return APIClient()

    @pytest.fixture
    def organizer_user(self):
        """Create an organizer user"""
        return User.objects.create_user(
            email="organizer@example.com",
            password="testpass123",
            first_name="Jane",
            last_name="Smith",
        )

    @pytest.fixture
    def family(self, organizer_user):
        """Create a family with organizer"""
        family = Family.objects.create(
            name="Test Family",
            created_by=organizer_user
        )
        FamilyMember.objects.create(
            family=family,
            user=organizer_user,
            role=FamilyMember.Role.ORGANIZER
        )
        return family

    def test_create_invitation_triggers_email_task(self, api_client, organizer_user, family, settings):
        """Creating invitation via API triggers email sending"""
        settings.CELERY_TASK_ALWAYS_EAGER = True

        # Authenticate
        api_client.force_authenticate(user=organizer_user)

        # Clear mailbox
        mail.outbox = []

        # Create invitation via API
        url = f"/api/v1/families/{family.public_id}/invitations/"
        data = {
            "invitee_email": "newinvitee@example.com",
            "role": "parent",
        }

        response = api_client.post(url, data, format="json")

        # Check response
        assert response.status_code == 201

        # Email should be sent
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.to == ["newinvitee@example.com"]
        assert "invited" in email.subject.lower()
        assert family.name in email.body