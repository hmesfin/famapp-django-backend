"""
OTP (One-Time Password) utility functions for email verification.

This module provides functionality for generating, storing, and validating
OTP codes using Redis as the backend storage.
"""

import random

from django.core.cache import cache


def generate_otp() -> str:
    """
    Generate a 6-digit OTP code.

    Returns:
        str: A 6-digit numeric code as a string.
    """
    return str(random.randint(100000, 999999))


def store_otp(email: str, otp: str, timeout: int = 600) -> bool:
    """
    Store OTP in Redis with TTL (Time To Live).

    Args:
        email: User's email address (used as key).
        otp: The 6-digit OTP code to store.
        timeout: Expiration time in seconds (default: 600 = 10 minutes).

    Returns:
        bool: True if OTP was stored successfully.
    """
    key = f"otp:{email}"
    cache.set(key, otp, timeout=timeout)
    return True


def get_otp(email: str) -> str | None:
    """
    Retrieve OTP from Redis by email.

    Args:
        email: User's email address.

    Returns:
        str | None: The OTP code if found, None otherwise.
    """
    key = f"otp:{email}"
    return cache.get(key)


def delete_otp(email: str) -> bool:
    """
    Delete OTP from Redis (enforces one-time use).

    Args:
        email: User's email address.

    Returns:
        bool: True if OTP was deleted, False if key didn't exist.
    """
    key = f"otp:{email}"
    # cache.delete() returns None, but we need to check if key existed
    existed = cache.get(key) is not None
    cache.delete(key)
    return existed
