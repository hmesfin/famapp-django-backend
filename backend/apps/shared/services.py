"""
Business logic services for shared app.
"""

import logging

from django.db import transaction

from apps.shared.models import Family
from apps.shared.models import FamilyMember

logger = logging.getLogger(__name__)


@transaction.atomic
def create_family_for_user(user) -> tuple[Family, FamilyMember]:
    """
    Create a family and family membership for a new user.

    This service is called after user email verification to automatically
    set up their first family with ORGANIZER role.

    Args:
        user: User instance to create family for

    Returns:
        Tuple of (Family, FamilyMember) instances

    Raises:
        ValueError: If user is None
    """
    if user is None:
        raise ValueError("User cannot be None")

    # Check if user already has a family (idempotency)
    # Order by created_at to ensure we return the first family
    existing_membership = (
        user.familymember_set.select_related("family").order_by("created_at").first()
    )
    if existing_membership:
        logger.info(
            f"User {user.email} already has family '{existing_membership.family.name}', skipping creation"
        )
        return existing_membership.family, existing_membership

    # Create family with user's first name (fallback to "User")
    family_name = f"{user.first_name or 'User'}'s Family"

    try:
        family = Family.objects.create(name=family_name, created_by=user, updated_by=user)

        logger.info(f"Created family '{family.name}' for user {user.email}")

        # Create family membership with ORGANIZER role
        family_member = FamilyMember.objects.create(
            user=user,
            family=family,
            role=FamilyMember.Role.ORGANIZER,
        )

        logger.info(
            f"Added {user.email} as ORGANIZER of family {family.public_id}"
        )

        return family, family_member

    except Exception as error:
        logger.error(f"Failed to create family for {user.email}: {error}")
        raise
