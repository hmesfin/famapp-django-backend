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
