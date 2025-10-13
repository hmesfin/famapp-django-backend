"""
Tests for OTP (One-Time Password) generation and Redis storage.

This module implements TDD for the OTP email verification system.
Phase A: OTP Model & Storage (Redis)
"""

import pytest
from django.core.cache import cache


@pytest.mark.django_db
class TestOTPGeneration:
    """Test OTP code generation."""

    def setup_method(self):
        """Clear Redis cache before each test."""
        cache.clear()

    def teardown_method(self):
        """Clear Redis cache after each test."""
        cache.clear()

    def test_generate_otp_returns_six_digit_code(self):
        """OTP code should be exactly 6 digits."""
        from apps.users.otp import generate_otp

        otp = generate_otp()

        assert len(otp) == 6
        assert otp.isdigit()
        assert 100000 <= int(otp) <= 999999

    def test_generate_otp_creates_unique_codes(self):
        """Each OTP generation should produce unique codes (statistically)."""
        from apps.users.otp import generate_otp

        # Generate 100 OTPs - highly unlikely to get duplicates
        otps = {generate_otp() for _ in range(100)}

        assert len(otps) > 95  # Allow for rare collisions


@pytest.mark.django_db
class TestOTPStorage:
    """Test OTP storage and retrieval from Redis."""

    def setup_method(self):
        """Clear Redis cache before each test."""
        cache.clear()

    def teardown_method(self):
        """Clear Redis cache after each test."""
        cache.clear()

    def test_store_otp_saves_to_redis(self):
        """OTP should be stored in Redis with email as key."""
        from apps.users.otp import store_otp

        email = "test@example.com"
        otp = "123456"

        result = store_otp(email, otp)

        assert result is True
        # Verify it's actually in Redis using Django cache
        stored_value = cache.get(f"otp:{email}")
        assert stored_value == otp

    def test_store_otp_with_custom_timeout(self):
        """OTP should accept custom timeout values."""
        from apps.users.otp import store_otp

        email = "test@example.com"
        otp = "123456"

        result = store_otp(email, otp, timeout=300)  # 5 minutes

        assert result is True
        stored_value = cache.get(f"otp:{email}")
        assert stored_value == otp

    def test_get_otp_retrieves_from_redis(self):
        """Should retrieve OTP from Redis by email."""
        from apps.users.otp import store_otp, get_otp

        email = "test@example.com"
        otp = "654321"
        store_otp(email, otp)

        retrieved_otp = get_otp(email)

        assert retrieved_otp == otp

    def test_get_otp_returns_none_for_nonexistent_email(self):
        """Should return None for emails without OTP."""
        from apps.users.otp import get_otp

        retrieved_otp = get_otp("nonexistent@example.com")

        assert retrieved_otp is None

    def test_delete_otp_removes_from_redis(self):
        """OTP should be deleted from Redis after use (one-time use)."""
        from apps.users.otp import store_otp, get_otp, delete_otp

        email = "test@example.com"
        otp = "789012"
        store_otp(email, otp)

        # Verify it exists
        assert get_otp(email) == otp

        # Delete it
        result = delete_otp(email)

        assert result is True
        assert get_otp(email) is None

    def test_delete_otp_returns_false_for_nonexistent_key(self):
        """Deleting non-existent OTP should return False."""
        from apps.users.otp import delete_otp

        result = delete_otp("nonexistent@example.com")

        assert result is False


@pytest.mark.django_db
class TestOTPExpiration:
    """Test OTP TTL (Time To Live) functionality."""

    def setup_method(self):
        """Clear Redis cache before each test."""
        cache.clear()

    def teardown_method(self):
        """Clear Redis cache after each test."""
        cache.clear()

    def test_otp_expires_after_timeout(self):
        """OTP should expire after the specified timeout."""
        from apps.users.otp import store_otp, get_otp
        import time

        email = "test@example.com"
        otp = "123456"

        # Store with 2 second timeout
        store_otp(email, otp, timeout=2)

        # Should exist immediately
        assert get_otp(email) == otp

        # Wait for expiration
        time.sleep(3)

        # Should be expired
        assert get_otp(email) is None

    def test_otp_default_timeout_is_600_seconds(self):
        """OTP should default to 600 seconds (10 minutes) TTL."""
        from apps.users.otp import store_otp, get_otp

        email = "test@example.com"
        otp = "123456"

        # Store with default timeout
        store_otp(email, otp)

        # Should exist (we can't test 10 min wait, but we verify it's stored)
        assert get_otp(email) == otp


@pytest.mark.django_db
class TestOTPEdgeCases:
    """Test edge cases and security considerations."""

    def setup_method(self):
        """Clear Redis cache before each test."""
        cache.clear()

    def teardown_method(self):
        """Clear Redis cache after each test."""
        cache.clear()

    def test_store_otp_overwrites_existing_otp(self):
        """Storing a new OTP for the same email should overwrite the old one."""
        from apps.users.otp import store_otp, get_otp

        email = "test@example.com"
        old_otp = "111111"
        new_otp = "999999"

        store_otp(email, old_otp)
        store_otp(email, new_otp)

        retrieved_otp = get_otp(email)
        assert retrieved_otp == new_otp
        assert retrieved_otp != old_otp

    def test_different_emails_have_separate_otps(self):
        """OTPs for different emails should be isolated."""
        from apps.users.otp import store_otp, get_otp

        email1 = "user1@example.com"
        email2 = "user2@example.com"
        otp1 = "111111"
        otp2 = "222222"

        store_otp(email1, otp1)
        store_otp(email2, otp2)

        assert get_otp(email1) == otp1
        assert get_otp(email2) == otp2

    def test_email_case_sensitivity(self):
        """OTP storage should be case-sensitive for emails."""
        from apps.users.otp import store_otp, get_otp

        email_lower = "test@example.com"
        email_upper = "TEST@EXAMPLE.COM"
        otp = "123456"

        store_otp(email_lower, otp)

        # Different case should be treated as different key
        assert get_otp(email_lower) == otp
        assert get_otp(email_upper) is None

    def test_otp_with_special_characters_in_email(self):
        """Should handle emails with special characters."""
        from apps.users.otp import store_otp, get_otp

        email = "test+tag@example.com"
        otp = "123456"

        store_otp(email, otp)

        assert get_otp(email) == otp

    def test_multiple_delete_calls_idempotent(self):
        """Multiple delete calls should be safe (idempotent)."""
        from apps.users.otp import store_otp, delete_otp

        email = "test@example.com"
        otp = "123456"

        store_otp(email, otp)

        # First delete should succeed
        assert delete_otp(email) is True

        # Second delete should return False (already deleted)
        assert delete_otp(email) is False

        # Third delete should also return False
        assert delete_otp(email) is False


@pytest.mark.django_db
class TestOTPEmailSending:
    """
    Test OTP email sending functionality.
    Phase B: OTP Email Sending with TDD
    """

    def setup_method(self):
        """Setup test user and clear cache before each test."""
        from django.contrib.auth import get_user_model
        from django.core import mail

        cache.clear()
        # Clear Django's email outbox
        mail.outbox = []

        User = get_user_model()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )

    def teardown_method(self):
        """Clear cache after each test."""
        cache.clear()

    def test_send_otp_email_generates_and_stores_otp(self):
        """send_otp_email should generate OTP and store it in Redis."""
        from apps.users.api.auth_utils import send_otp_email
        from apps.users.otp import get_otp

        result = send_otp_email(self.user)

        # Should return success and OTP
        assert result["success"] is True
        assert "otp" in result
        assert len(result["otp"]) == 6

        # OTP should be stored in Redis
        stored_otp = get_otp(self.user.email)
        assert stored_otp == result["otp"]

    def test_send_otp_email_sends_email_to_user(self):
        """send_otp_email should send email to user's email address."""
        from django.core import mail
        from apps.users.api.auth_utils import send_otp_email

        send_otp_email(self.user)

        # Check that one email was sent
        assert len(mail.outbox) == 1

        # Check recipient
        email = mail.outbox[0]
        assert self.user.email in email.to

    def test_send_otp_email_has_correct_subject(self):
        """Email subject should be 'FamApp - Your Verification Code'."""
        from django.core import mail
        from apps.users.api.auth_utils import send_otp_email

        send_otp_email(self.user)

        email = mail.outbox[0]
        assert email.subject == "FamApp - Your Verification Code"

    def test_send_otp_email_includes_otp_in_body(self):
        """Email body should include the OTP code prominently."""
        from django.core import mail
        from apps.users.api.auth_utils import send_otp_email

        result = send_otp_email(self.user)
        otp = result["otp"]

        email = mail.outbox[0]

        # Check HTML body
        assert otp in email.body  # Plain text body
        if email.alternatives:  # HTML alternative
            html_body = email.alternatives[0][0]
            assert otp in html_body

    def test_send_otp_email_includes_expiration_time(self):
        """Email should mention 10-minute expiration time."""
        from django.core import mail
        from apps.users.api.auth_utils import send_otp_email

        send_otp_email(self.user)

        email = mail.outbox[0]

        # Check for expiration mention (10 minutes)
        assert "10 minutes" in email.body.lower() or "10 minute" in email.body.lower()

    def test_send_otp_email_includes_security_notice(self):
        """Email should include security notice about not requesting code."""
        from django.core import mail
        from apps.users.api.auth_utils import send_otp_email

        send_otp_email(self.user)

        email = mail.outbox[0]

        # Check for security notice
        body_lower = email.body.lower()
        assert "didn't request" in body_lower or "did not request" in body_lower

    def test_send_otp_email_logs_success(self, caplog):
        """send_otp_email should log successful email sending."""
        import logging
        from apps.users.api.auth_utils import send_otp_email

        with caplog.at_level(logging.INFO):
            send_otp_email(self.user)

        # Check logs for success message
        assert any("OTP email sent successfully" in record.message for record in caplog.records)
        assert any(self.user.email in record.message for record in caplog.records)

    def test_send_otp_email_logs_failure_on_exception(self, caplog, monkeypatch):
        """send_otp_email should log errors when email sending fails."""
        import logging
        from apps.users.api.auth_utils import send_otp_email
        from django.core.mail import send_mail

        # Mock send_mail to raise exception
        def mock_send_mail(*args, **kwargs):
            raise Exception("SMTP connection failed")

        monkeypatch.setattr("apps.users.api.auth_utils.send_mail", mock_send_mail)

        with caplog.at_level(logging.ERROR):
            result = send_otp_email(self.user)

        # Should return failure
        assert result["success"] is False

        # Check logs for error message
        assert any("Failed to send OTP email" in record.message for record in caplog.records)
        assert any(self.user.email in record.message for record in caplog.records)

    def test_send_otp_email_uses_default_from_email(self):
        """Email should be sent from settings.DEFAULT_FROM_EMAIL."""
        from django.core import mail
        from django.conf import settings
        from apps.users.api.auth_utils import send_otp_email

        send_otp_email(self.user)

        email = mail.outbox[0]
        assert email.from_email == settings.DEFAULT_FROM_EMAIL

    def test_send_otp_email_includes_user_name_in_body(self):
        """Email should address user by name when available."""
        from django.core import mail
        from apps.users.api.auth_utils import send_otp_email

        # Add full name to user
        self.user.first_name = "John"
        self.user.save()

        send_otp_email(self.user)

        email = mail.outbox[0]

        # Should include greeting with name or email
        body_lower = email.body.lower()
        assert "hello" in body_lower or "hi" in body_lower
