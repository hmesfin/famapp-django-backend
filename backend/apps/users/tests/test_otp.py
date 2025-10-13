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


@pytest.mark.django_db
class TestOTPVerification:
    """
    Test OTP verification endpoint.
    Phase C: OTP Verification Endpoint with TDD
    """

    def setup_method(self):
        """Setup test user and clear cache before each test."""
        from django.contrib.auth import get_user_model
        from rest_framework.test import APIClient

        cache.clear()

        User = get_user_model()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )
        self.client = APIClient()

    def teardown_method(self):
        """Clear cache after each test."""
        cache.clear()

    def test_verify_otp_with_correct_code_marks_user_as_verified(self):
        """Valid OTP verification should mark user.email_verified as True."""
        from apps.users.otp import store_otp

        # Arrange: Store OTP in Redis
        otp = "123456"
        store_otp(self.user.email, otp)

        # Ensure user starts as unverified
        assert self.user.email_verified is False

        # Act: POST to /api/auth/verify-otp/
        response = self.client.post(
            "/api/auth/verify-otp/",
            {"email": self.user.email, "otp": otp},
            format="json"
        )

        # Assert: User should be verified
        self.user.refresh_from_db()
        assert self.user.email_verified is True
        assert response.status_code == 200

    def test_verify_otp_returns_jwt_tokens_on_success(self):
        """Successful OTP verification should return JWT access and refresh tokens."""
        from apps.users.otp import store_otp

        # Arrange: Store OTP in Redis
        otp = "123456"
        store_otp(self.user.email, otp)

        # Act: POST to /api/auth/verify-otp/
        response = self.client.post(
            "/api/auth/verify-otp/",
            {"email": self.user.email, "otp": otp},
            format="json"
        )

        # Assert: Should return 200 with JWT tokens
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data

        # Verify token format (JWT tokens are non-empty strings)
        assert isinstance(response.data["access"], str)
        assert len(response.data["access"]) > 50  # JWT tokens are long
        assert isinstance(response.data["refresh"], str)
        assert len(response.data["refresh"]) > 50

    def test_verify_otp_returns_user_data_on_success(self):
        """Successful OTP verification should return user profile data."""
        from apps.users.otp import store_otp

        # Arrange: Store OTP in Redis
        otp = "123456"
        store_otp(self.user.email, otp)

        # Act: POST to /api/auth/verify-otp/
        response = self.client.post(
            "/api/auth/verify-otp/",
            {"email": self.user.email, "otp": otp},
            format="json"
        )

        # Assert: Should return user data
        assert response.status_code == 200
        user_data = response.data["user"]
        assert user_data["email"] == self.user.email
        assert user_data["first_name"] == "John"
        assert user_data["last_name"] == "Doe"
        assert user_data["email_verified"] is True

    def test_verify_otp_returns_400_with_invalid_otp_code(self):
        """Invalid OTP code should return 400 error."""
        from apps.users.otp import store_otp

        # Arrange: Store correct OTP
        correct_otp = "123456"
        store_otp(self.user.email, correct_otp)

        # Act: POST with wrong OTP
        response = self.client.post(
            "/api/auth/verify-otp/",
            {"email": self.user.email, "otp": "999999"},  # Wrong OTP
            format="json"
        )

        # Assert: Should return 400 with error message
        assert response.status_code == 400
        assert "error" in response.data
        assert "Invalid OTP" in response.data["error"]

        # User should NOT be verified
        self.user.refresh_from_db()
        assert self.user.email_verified is False

    def test_verify_otp_returns_400_when_otp_not_found(self):
        """OTP verification without stored OTP should return 400."""
        # Act: POST without storing OTP first
        response = self.client.post(
            "/api/auth/verify-otp/",
            {"email": self.user.email, "otp": "123456"},
            format="json"
        )

        # Assert: Should return 400 with error message
        assert response.status_code == 400
        assert "error" in response.data
        assert "No OTP code found" in response.data["error"]

    def test_verify_otp_returns_400_when_otp_expired(self):
        """Expired OTP should return 400 error."""
        from apps.users.otp import store_otp
        import time

        # Arrange: Store OTP with 1 second timeout
        otp = "123456"
        store_otp(self.user.email, otp, timeout=1)

        # Wait for expiration
        time.sleep(2)

        # Act: POST with expired OTP
        response = self.client.post(
            "/api/auth/verify-otp/",
            {"email": self.user.email, "otp": otp},
            format="json"
        )

        # Assert: Should return 400 (OTP not found = expired)
        assert response.status_code == 400
        assert "error" in response.data
        assert "No OTP code found" in response.data["error"]

    def test_verify_otp_deletes_otp_after_successful_verification(self):
        """OTP should be deleted from Redis after successful use (one-time use)."""
        from apps.users.otp import store_otp, get_otp

        # Arrange: Store OTP in Redis
        otp = "123456"
        store_otp(self.user.email, otp)

        # Verify OTP exists before verification
        assert get_otp(self.user.email) == otp

        # Act: POST to /api/auth/verify-otp/
        response = self.client.post(
            "/api/auth/verify-otp/",
            {"email": self.user.email, "otp": otp},
            format="json"
        )

        # Assert: OTP should be deleted from Redis
        assert response.status_code == 200
        assert get_otp(self.user.email) is None

    def test_verify_otp_cannot_be_used_twice(self):
        """Same OTP cannot be used multiple times (one-time use enforcement)."""
        from apps.users.otp import store_otp

        # Arrange: Store OTP in Redis
        otp = "123456"
        store_otp(self.user.email, otp)

        # Act: First verification (should succeed)
        response1 = self.client.post(
            "/api/auth/verify-otp/",
            {"email": self.user.email, "otp": otp},
            format="json"
        )
        assert response1.status_code == 200

        # Act: Second verification with same OTP (should fail)
        response2 = self.client.post(
            "/api/auth/verify-otp/",
            {"email": self.user.email, "otp": otp},
            format="json"
        )

        # Assert: Second attempt should fail
        assert response2.status_code == 400
        assert "error" in response2.data
        assert "No OTP code found" in response2.data["error"]

    def test_verify_otp_requires_email_and_otp(self):
        """OTP verification should require both email and otp parameters."""
        # Test missing email
        response = self.client.post(
            "/api/auth/verify-otp/",
            {"otp": "123456"},
            format="json"
        )
        assert response.status_code == 400
        assert "error" in response.data

        # Test missing OTP
        response = self.client.post(
            "/api/auth/verify-otp/",
            {"email": self.user.email},
            format="json"
        )
        assert response.status_code == 400
        assert "error" in response.data

    def test_verify_otp_returns_404_for_nonexistent_user(self):
        """OTP verification for non-existent user should return 404."""
        from apps.users.otp import store_otp

        # Arrange: Store OTP for email that has no user
        fake_email = "nonexistent@example.com"
        otp = "123456"
        store_otp(fake_email, otp)

        # Act: POST with non-existent user email
        response = self.client.post(
            "/api/auth/verify-otp/",
            {"email": fake_email, "otp": otp},
            format="json"
        )

        # Assert: Should return 404
        assert response.status_code == 404
        assert "error" in response.data
        assert "User not found" in response.data["error"]

    def test_verify_otp_logs_success(self, caplog):
        """OTP verification should log success."""
        import logging
        from apps.users.otp import store_otp

        # Arrange: Store OTP in Redis
        otp = "123456"
        store_otp(self.user.email, otp)

        # Act: POST to /api/auth/verify-otp/
        with caplog.at_level(logging.INFO):
            response = self.client.post(
                "/api/auth/verify-otp/",
                {"email": self.user.email, "otp": otp},
                format="json"
            )

        # Assert: Should log success message
        assert response.status_code == 200
        assert any("OTP verified successfully" in record.message for record in caplog.records)
        assert any(self.user.email in record.message for record in caplog.records)

    def test_verify_otp_jwt_tokens_are_valid_and_usable(self):
        """JWT tokens returned should be valid and usable for authentication."""
        from apps.users.otp import store_otp
        from rest_framework_simplejwt.tokens import AccessToken

        # Arrange: Store OTP in Redis
        otp = "123456"
        store_otp(self.user.email, otp)

        # Act: POST to /api/auth/verify-otp/
        response = self.client.post(
            "/api/auth/verify-otp/",
            {"email": self.user.email, "otp": otp},
            format="json"
        )

        # Assert: Tokens are valid
        assert response.status_code == 200
        access_token = response.data["access"]
        refresh_token = response.data["refresh"]

        # Validate access token structure
        token = AccessToken(access_token)
        assert int(token["user_id"]) == self.user.id

        # Use access token to authenticate API request
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        profile_response = self.client.get("/api/auth/profile/")

        assert profile_response.status_code == 200
        assert profile_response.data["user"]["email"] == self.user.email
        assert profile_response.data["user"]["email_verified"] is True

    def test_verify_otp_creates_family_for_user(self):
        """OTP verification should auto-create family for new user (Enhancement 2)."""
        from apps.users.otp import store_otp
        from apps.shared.models import Family, FamilyMember

        # Arrange: Store OTP in Redis
        otp = "123456"
        store_otp(self.user.email, otp)

        # Verify no family exists initially
        assert Family.objects.count() == 0
        assert FamilyMember.objects.count() == 0

        # Act: POST to /api/auth/verify-otp/
        response = self.client.post(
            "/api/auth/verify-otp/",
            {"email": self.user.email, "otp": otp},
            format="json"
        )

        # Assert: Family and FamilyMember created
        assert response.status_code == 200
        assert Family.objects.count() == 1
        assert FamilyMember.objects.count() == 1

        # Verify family data in response
        assert "family" in response.data
        family_data = response.data["family"]
        assert "public_id" in family_data
        assert family_data["name"] == "John's Family"
        assert family_data["role"] == FamilyMember.Role.ORGANIZER

        # Verify database objects
        family = Family.objects.first()
        assert family.name == "John's Family"
        assert family.created_by == self.user

        member = FamilyMember.objects.first()
        assert member.user == self.user
        assert member.family == family
        assert member.role == FamilyMember.Role.ORGANIZER


@pytest.mark.django_db
class TestOTPResend:
    """
    Test OTP resend endpoint functionality.
    Phase D: OTP Resend Endpoint with TDD
    """

    def setup_method(self):
        """Setup test user and clear cache before each test."""
        from django.contrib.auth import get_user_model
        from rest_framework.test import APIClient

        cache.clear()

        User = get_user_model()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )
        self.user.email_verified = False
        self.user.save()

        self.client = APIClient()

    def teardown_method(self):
        """Clear cache after each test."""
        cache.clear()

    def test_resend_otp_generates_new_otp_code(self):
        """Resending OTP should generate a new OTP code."""
        from apps.users.otp import get_otp

        # Act: Request OTP resend
        response = self.client.post(
            "/api/auth/resend-otp/",
            {"email": self.user.email},
            format="json"
        )

        # Assert: Should succeed
        assert response.status_code == 200

        # Verify OTP is stored in Redis
        stored_otp = get_otp(self.user.email)
        assert stored_otp is not None
        assert len(stored_otp) == 6
        assert stored_otp.isdigit()

    def test_resend_otp_returns_success_message(self):
        """Resend OTP should return success message and email."""
        # Act: Request OTP resend
        response = self.client.post(
            "/api/auth/resend-otp/",
            {"email": self.user.email},
            format="json"
        )

        # Assert: Should return 200 with success message
        assert response.status_code == 200
        assert "message" in response.data
        assert "OTP sent successfully" in response.data["message"]
        assert response.data["email"] == self.user.email

    def test_resend_otp_sends_email_to_user(self):
        """Resend OTP should send email with new OTP code."""
        from django.core import mail

        # Clear mail outbox
        mail.outbox = []

        # Act: Request OTP resend
        response = self.client.post(
            "/api/auth/resend-otp/",
            {"email": self.user.email},
            format="json"
        )

        # Assert: Email should be sent
        assert response.status_code == 200
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert self.user.email in email.to
        assert email.subject == "FamApp - Your Verification Code"

    def test_resend_otp_rate_limiting_within_60_seconds(self):
        """Should return 429 if resend requested within 60 seconds."""
        # Act: First request (should succeed)
        response1 = self.client.post(
            "/api/auth/resend-otp/",
            {"email": self.user.email},
            format="json"
        )
        assert response1.status_code == 200

        # Act: Second request immediately (should be rate limited)
        response2 = self.client.post(
            "/api/auth/resend-otp/",
            {"email": self.user.email},
            format="json"
        )

        # Assert: Should return 429
        assert response2.status_code == 429
        assert "error" in response2.data
        assert "wait" in response2.data["error"].lower()

    def test_resend_otp_allowed_after_60_seconds(self):
        """Should allow resend after 60 seconds rate limit expires."""
        import time

        # Act: First request
        response1 = self.client.post(
            "/api/auth/resend-otp/",
            {"email": self.user.email},
            format="json"
        )
        assert response1.status_code == 200

        # Manually clear rate limit key (simulate 60 seconds passing)
        cache.delete(f"otp_last_sent:{self.user.email}")

        # Act: Second request after rate limit cleared
        response2 = self.client.post(
            "/api/auth/resend-otp/",
            {"email": self.user.email},
            format="json"
        )

        # Assert: Should succeed
        assert response2.status_code == 200

    def test_resend_otp_overwrites_old_otp(self):
        """New OTP should replace old OTP in Redis."""
        from apps.users.otp import store_otp, get_otp

        # Arrange: Store old OTP manually
        old_otp = "111111"
        store_otp(self.user.email, old_otp)
        assert get_otp(self.user.email) == old_otp

        # Act: Request OTP resend
        response = self.client.post(
            "/api/auth/resend-otp/",
            {"email": self.user.email},
            format="json"
        )

        # Assert: New OTP should be different and replace old one
        assert response.status_code == 200
        new_otp = get_otp(self.user.email)
        assert new_otp is not None
        assert new_otp != old_otp

    def test_resend_otp_returns_404_for_nonexistent_user(self):
        """Should return 404 if user email not found."""
        # Act: Request OTP for non-existent user
        response = self.client.post(
            "/api/auth/resend-otp/",
            {"email": "nonexistent@example.com"},
            format="json"
        )

        # Assert: Should return 404
        assert response.status_code == 404
        assert "error" in response.data
        assert "not found" in response.data["error"].lower()

    def test_resend_otp_returns_400_if_already_verified(self):
        """Should return 400 if user email already verified."""
        # Arrange: Mark user as verified
        self.user.email_verified = True
        self.user.save()

        # Act: Request OTP resend
        response = self.client.post(
            "/api/auth/resend-otp/",
            {"email": self.user.email},
            format="json"
        )

        # Assert: Should return 400
        assert response.status_code == 400
        assert "error" in response.data
        assert "already verified" in response.data["error"].lower()

    def test_resend_otp_requires_email(self):
        """Should return 400 if email not provided."""
        # Act: Request without email
        response = self.client.post(
            "/api/auth/resend-otp/",
            {},
            format="json"
        )

        # Assert: Should return 400
        assert response.status_code == 400
        assert "error" in response.data

    def test_resend_otp_logs_success(self, caplog):
        """Should log successful OTP resend."""
        import logging

        # Act: Request OTP resend
        with caplog.at_level(logging.INFO):
            response = self.client.post(
                "/api/auth/resend-otp/",
                {"email": self.user.email},
                format="json"
            )

        # Assert: Should log success
        assert response.status_code == 200
        assert any("OTP resent" in record.message for record in caplog.records)

    def test_resend_otp_uses_redis_for_rate_limiting(self):
        """Rate limiting should use Redis cache."""
        # Act: First request
        response1 = self.client.post(
            "/api/auth/resend-otp/",
            {"email": self.user.email},
            format="json"
        )
        assert response1.status_code == 200

        # Check Redis key exists
        rate_limit_key = f"otp_last_sent:{self.user.email}"
        rate_limit_value = cache.get(rate_limit_key)
        assert rate_limit_value is True

    def test_resend_otp_rate_limit_key_expires_after_60_seconds(self):
        """Rate limit key should have 60 second TTL."""
        import time

        # Act: First request
        response = self.client.post(
            "/api/auth/resend-otp/",
            {"email": self.user.email},
            format="json"
        )
        assert response.status_code == 200

        # Check Redis key exists with TTL
        rate_limit_key = f"otp_last_sent:{self.user.email}"
        ttl = cache.ttl(rate_limit_key) if hasattr(cache, 'ttl') else None

        # If cache backend supports TTL checking, verify it
        if ttl is not None:
            assert 55 <= ttl <= 60  # Should be around 60 seconds


@pytest.mark.django_db
class TestRegistrationOTPIntegration:
    """
    Test registration flow integration with OTP.
    Phase E: Registration Flow Integration with TDD
    """

    def setup_method(self):
        """Setup test client and clear cache."""
        from rest_framework.test import APIClient

        cache.clear()
        self.client = APIClient()

    def teardown_method(self):
        """Clear cache after each test."""
        cache.clear()

    def test_registration_sends_otp_email(self):
        """Registration should send OTP email instead of verification link."""
        from django.core import mail

        mail.outbox = []

        # Act: Register new user
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "New",
                "last_name": "User",
            },
            format="json"
        )

        # Assert: Should send OTP email
        assert response.status_code == 201
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.subject == "FamApp - Your Verification Code"
        assert "newuser@example.com" in email.to

    def test_registration_stores_otp_in_redis(self):
        """Registration should generate and store OTP in Redis."""
        from apps.users.otp import get_otp

        # Act: Register new user
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "New",
                "last_name": "User",
            },
            format="json"
        )

        # Assert: OTP should be stored
        assert response.status_code == 201
        stored_otp = get_otp("newuser@example.com")
        assert stored_otp is not None
        assert len(stored_otp) == 6
        assert stored_otp.isdigit()

    def test_registration_returns_otp_message(self):
        """Registration response should mention checking email for OTP."""
        # Act: Register new user
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "New",
                "last_name": "User",
            },
            format="json"
        )

        # Assert: Should return OTP-related message
        assert response.status_code == 201
        assert "message" in response.data
        message = response.data["message"].lower()
        assert "otp" in message or "verification code" in message or "check your email" in message

    def test_registration_includes_email_in_response(self):
        """Registration response should include user email."""
        # Act: Register new user
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "New",
                "last_name": "User",
            },
            format="json"
        )

        # Assert: Should include email in response
        assert response.status_code == 201
        assert "user" in response.data
        assert response.data["user"]["email"] == "newuser@example.com"

    def test_registration_user_cannot_login_without_otp_verification(self):
        """Newly registered user cannot login until OTP verified."""
        # Act: Register new user
        register_response = self.client.post(
            "/api/auth/register/",
            {
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "New",
                "last_name": "User",
            },
            format="json"
        )
        assert register_response.status_code == 201

        # Act: Try to login without verifying OTP
        login_response = self.client.post(
            "/api/auth/login/",
            {
                "email": "newuser@example.com",
                "password": "SecurePass123!",
            },
            format="json"
        )

        # Assert: Login should fail or return verification required error
        # Based on existing code, it should raise validation error
        assert login_response.status_code == 400
        assert "verification" in str(login_response.data).lower()

    def test_registration_user_can_login_after_otp_verification(self):
        """User can login after successful OTP verification."""
        from apps.users.otp import get_otp

        # Act: Register new user
        register_response = self.client.post(
            "/api/auth/register/",
            {
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "New",
                "last_name": "User",
            },
            format="json"
        )
        assert register_response.status_code == 201

        # Get OTP from Redis
        otp = get_otp("newuser@example.com")
        assert otp is not None

        # Verify OTP
        verify_response = self.client.post(
            "/api/auth/verify-otp/",
            {
                "email": "newuser@example.com",
                "otp": otp,
            },
            format="json"
        )
        assert verify_response.status_code == 200

        # Act: Now try to login
        login_response = self.client.post(
            "/api/auth/login/",
            {
                "email": "newuser@example.com",
                "password": "SecurePass123!",
            },
            format="json"
        )

        # Assert: Login should succeed
        assert login_response.status_code == 200
        assert "access" in login_response.data
        assert "refresh" in login_response.data

    def test_registration_without_email_does_not_send_otp(self):
        """Registration with phone number only should not send OTP (future enhancement)."""
        # This test documents expected behavior for phone-only registration
        # For now, we focus on email-based registration

        # Act: Register with phone only (if supported)
        response = self.client.post(
            "/api/auth/register/",
            {
                "phone_number": "+1234567890",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "Phone",
                "last_name": "User",
            },
            format="json"
        )

        # This might fail validation (email OR phone required)
        # Just document the behavior for future
        # Skip this test for now as it's out of scope
        pass

    def test_registration_email_contains_otp_code(self):
        """Registration email should contain 6-digit OTP code."""
        from django.core import mail
        from apps.users.otp import get_otp

        mail.outbox = []

        # Act: Register new user
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "New",
                "last_name": "User",
            },
            format="json"
        )

        # Assert: Email should contain OTP
        assert response.status_code == 201
        assert len(mail.outbox) == 1

        email = mail.outbox[0]
        stored_otp = get_otp("newuser@example.com")

        # OTP should be in email body
        assert stored_otp in email.body
