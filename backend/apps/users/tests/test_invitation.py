"""
Tests for Family Invitation System (Enhancement 3).

This module implements TDD for the Family Invitation & Onboarding System.

Phase A: Invitation Model Tests
Phase B: Invitation Serializer Tests
Phase C: Invitation Creation Endpoint Tests
Phase D: Invitation Listing & Management Tests
Phase E: Invitation Acceptance Flow Tests
Phase F: Invitation Email & Celery Task Tests
Phase G: Signup with Invitation Flow Tests
Phase H: Invitation Expiration & Cleanup Tests
Phase I: Permission & Authorization Tests
Phase J: Edge Cases & Data Integrity Tests

Following the TDD Gospel: RED → GREEN → REFACTOR
"""

import uuid
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.test import APIClient

from apps.shared.models import Family, FamilyMember
from apps.users.models import User


# ============================================================================
# Phase A: Invitation Model Tests
# ============================================================================


@pytest.mark.django_db
class TestInvitationModelCreation:
    """Test basic invitation model creation and fields."""

    def setup_method(self):
        """Create test users and family."""
        self.organizer = User.objects.create_user(
            email="organizer@example.com",
            password="testpass123",
            first_name="Alice",
            last_name="Organizer",
        )
        self.family = Family.objects.create(
            name="Test Family",
            created_by=self.organizer,
        )
        FamilyMember.objects.create(
            family=self.family,
            user=self.organizer,
            role=FamilyMember.Role.ORGANIZER,
        )

    def test_invitation_model_exists(self):
        """Invitation model should exist."""
        from apps.users.models import Invitation

        assert Invitation is not None

    def test_create_invitation_with_required_fields(self):
        """Should create invitation with inviter, invitee_email, family, role."""
        from apps.users.models import Invitation

        invitation = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="invitee@example.com",
            family=self.family,
            role="parent",
        )

        assert invitation.id is not None
        assert invitation.inviter == self.organizer
        assert invitation.invitee_email == "invitee@example.com"
        assert invitation.family == self.family
        assert invitation.role == "parent"

    def test_invitation_has_token_field(self):
        """Invitation should have a token field (UUID)."""
        from apps.users.models import Invitation

        invitation = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="invitee@example.com",
            family=self.family,
            role="parent",
        )

        assert invitation.token is not None
        assert isinstance(invitation.token, uuid.UUID)

    def test_invitation_token_auto_generated(self):
        """Invitation token should be auto-generated as UUID."""
        from apps.users.models import Invitation

        invitation1 = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="invitee1@example.com",
            family=self.family,
            role="parent",
        )
        invitation2 = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="invitee2@example.com",
            family=self.family,
            role="parent",
        )

        # Tokens should be unique
        assert invitation1.token != invitation2.token

    def test_invitation_has_status_field(self):
        """Invitation should have status field with TextChoices."""
        from apps.users.models import Invitation

        invitation = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="invitee@example.com",
            family=self.family,
            role="parent",
        )

        # Should default to PENDING
        assert invitation.status == "pending"

    def test_invitation_status_choices(self):
        """Invitation status should support all required states."""
        from apps.users.models import Invitation

        # Test all status choices
        statuses = ["pending", "accepted", "declined", "expired", "cancelled"]

        for status in statuses:
            invitation = Invitation.objects.create(
                inviter=self.organizer,
                invitee_email=f"{status}@example.com",
                family=self.family,
                role="parent",
                status=status,
            )
            assert invitation.status == status

    def test_invitation_role_choices(self):
        """Invitation role should only allow PARENT and CHILD."""
        from apps.users.models import Invitation

        # Test valid roles
        valid_roles = ["parent", "child"]
        for role in valid_roles:
            invitation = Invitation.objects.create(
                inviter=self.organizer,
                invitee_email=f"{role}@example.com",
                family=self.family,
                role=role,
            )
            assert invitation.role == role

    def test_invitation_role_excludes_organizer(self):
        """Invitation role should NOT include ORGANIZER option."""
        from apps.users.models import Invitation

        # Attempting to create with 'organizer' role should fail validation
        with pytest.raises(ValidationError):
            invitation = Invitation(
                inviter=self.organizer,
                invitee_email="invitee@example.com",
                family=self.family,
                role="organizer",  # Invalid role
            )
            invitation.full_clean()  # Trigger validation

    def test_invitation_has_expires_at_field(self):
        """Invitation should have expires_at field."""
        from apps.users.models import Invitation

        invitation = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="invitee@example.com",
            family=self.family,
            role="parent",
        )

        assert invitation.expires_at is not None
        assert isinstance(invitation.expires_at, timezone.datetime)

    def test_invitation_expires_at_auto_set_to_7_days(self):
        """Invitation expires_at should auto-set to 7 days from now."""
        from apps.users.models import Invitation

        now = timezone.now()

        invitation = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="invitee@example.com",
            family=self.family,
            role="parent",
        )

        # Should be approximately 7 days from now (within 1 minute tolerance)
        expected_expiry = now + timedelta(days=7)
        time_diff = abs((invitation.expires_at - expected_expiry).total_seconds())
        assert time_diff < 60  # Within 1 minute

    def test_invitation_inherits_from_base_model(self):
        """Invitation should inherit from BaseModel (audit trail + soft delete)."""
        from apps.users.models import Invitation

        invitation = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="invitee@example.com",
            family=self.family,
            role="parent",
            created_by=self.organizer,
        )

        # Should have BaseModel fields
        assert hasattr(invitation, "public_id")
        assert hasattr(invitation, "created_at")
        assert hasattr(invitation, "updated_at")
        assert hasattr(invitation, "created_by")
        assert hasattr(invitation, "updated_by")
        assert hasattr(invitation, "is_deleted")
        assert hasattr(invitation, "deleted_at")
        assert hasattr(invitation, "deleted_by")

        # Check values
        assert invitation.public_id is not None
        assert invitation.created_at is not None
        assert invitation.created_by == self.organizer
        assert invitation.is_deleted is False


@pytest.mark.django_db
class TestInvitationModelRelationships:
    """Test invitation model foreign key relationships."""

    def setup_method(self):
        """Create test users and family."""
        self.organizer = User.objects.create_user(
            email="organizer@example.com",
            password="testpass123",
        )
        self.family = Family.objects.create(
            name="Test Family",
            created_by=self.organizer,
        )
        FamilyMember.objects.create(
            family=self.family,
            user=self.organizer,
            role=FamilyMember.Role.ORGANIZER,
        )

    def test_invitation_foreign_key_to_inviter(self):
        """Invitation should have ForeignKey to inviter (User)."""
        from apps.users.models import Invitation

        invitation = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="invitee@example.com",
            family=self.family,
            role="parent",
        )

        assert invitation.inviter == self.organizer
        assert isinstance(invitation.inviter, User)

    def test_invitation_foreign_key_to_family(self):
        """Invitation should have ForeignKey to Family."""
        from apps.users.models import Invitation

        invitation = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="invitee@example.com",
            family=self.family,
            role="parent",
        )

        assert invitation.family == self.family
        assert isinstance(invitation.family, Family)

    def test_invitation_cascade_delete_when_family_deleted(self):
        """Invitations should be deleted when family is deleted."""
        from apps.users.models import Invitation

        invitation = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="invitee@example.com",
            family=self.family,
            role="parent",
        )
        invitation_id = invitation.id

        # Delete family
        self.family.delete()

        # Invitation should be cascade deleted
        assert not Invitation.objects.filter(id=invitation_id).exists()


@pytest.mark.django_db
class TestInvitationModelValidation:
    """Test invitation model validation rules."""

    def setup_method(self):
        """Create test users and family."""
        self.organizer = User.objects.create_user(
            email="organizer@example.com",
            password="testpass123",
        )
        self.family = Family.objects.create(
            name="Test Family",
            created_by=self.organizer,
        )
        FamilyMember.objects.create(
            family=self.family,
            user=self.organizer,
            role=FamilyMember.Role.ORGANIZER,
        )

    def test_invitation_validates_email_format(self):
        """Invitation should validate invitee_email format."""
        from apps.users.models import Invitation

        # Invalid email should fail validation
        with pytest.raises(ValidationError):
            invitation = Invitation(
                inviter=self.organizer,
                invitee_email="not-an-email",  # Invalid format
                family=self.family,
                role="parent",
            )
            invitation.full_clean()  # Trigger validation

    def test_invitation_prevents_duplicate_pending_invites_same_email(self):
        """Cannot have multiple pending invitations for same email to same family."""
        from apps.users.models import Invitation
        from django.db import IntegrityError

        # Create first pending invitation
        Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="invitee@example.com",
            family=self.family,
            role="parent",
            status="pending",
        )

        # Attempt to create duplicate pending invitation should fail
        with pytest.raises((IntegrityError, ValidationError)):
            Invitation.objects.create(
                inviter=self.organizer,
                invitee_email="invitee@example.com",
                family=self.family,
                role="parent",
                status="pending",
            )

    def test_invitation_allows_new_invite_after_acceptance(self):
        """Can create new invitation for same email after previous was accepted."""
        from apps.users.models import Invitation

        # Create and accept first invitation
        invitation1 = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="invitee@example.com",
            family=self.family,
            role="parent",
            status="pending",
        )
        invitation1.status = "accepted"
        invitation1.save()

        # Should allow new pending invitation now
        invitation2 = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="invitee@example.com",
            family=self.family,
            role="child",  # Different role
            status="pending",
        )

        assert invitation2.id is not None


@pytest.mark.django_db
class TestInvitationModelProperties:
    """Test invitation model properties and methods."""

    def setup_method(self):
        """Create test users and family."""
        self.organizer = User.objects.create_user(
            email="organizer@example.com",
            password="testpass123",
        )
        self.family = Family.objects.create(
            name="Test Family",
            created_by=self.organizer,
        )

    def test_invitation_has_is_expired_property(self):
        """Invitation should have is_expired property."""
        from apps.users.models import Invitation

        invitation = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="invitee@example.com",
            family=self.family,
            role="parent",
        )

        assert hasattr(invitation, "is_expired")

    def test_invitation_is_expired_returns_false_for_future_expiry(self):
        """is_expired should return False for future expiration date."""
        from apps.users.models import Invitation

        future_date = timezone.now() + timedelta(days=1)

        invitation = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="invitee@example.com",
            family=self.family,
            role="parent",
            expires_at=future_date,
        )

        assert invitation.is_expired is False

    def test_invitation_is_expired_returns_true_for_past_expiry(self):
        """is_expired should return True for past expiration date."""
        from apps.users.models import Invitation

        past_date = timezone.now() - timedelta(days=1)

        invitation = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="invitee@example.com",
            family=self.family,
            role="parent",
            expires_at=past_date,
        )

        assert invitation.is_expired is True

    def test_invitation_str_representation(self):
        """Invitation should have readable string representation."""
        from apps.users.models import Invitation

        invitation = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="invitee@example.com",
            family=self.family,
            role="parent",
        )

        str_repr = str(invitation)

        # Should contain email and family name
        assert "invitee@example.com" in str_repr
        assert "Test Family" in str_repr


# ============================================================================
# Phase B: Invitation Serializer Tests
# ============================================================================


@pytest.mark.django_db
class TestInvitationCreateSerializer:
    """Test InvitationCreateSerializer validation."""

    def setup_method(self):
        """Create test users and family."""
        self.organizer = User.objects.create_user(
            email="organizer@example.com",
            password="testpass123",
            first_name="Alice",
        )
        self.family = Family.objects.create(
            name="Test Family",
            created_by=self.organizer,
        )
        FamilyMember.objects.create(
            family=self.family,
            user=self.organizer,
            role=FamilyMember.Role.ORGANIZER,
        )

    def test_invitation_create_serializer_exists(self):
        """InvitationCreateSerializer should exist."""
        from apps.users.api.serializers import InvitationCreateSerializer

        assert InvitationCreateSerializer is not None

    def test_create_serializer_validates_email_required(self):
        """invitee_email field should be required."""
        from apps.users.api.serializers import InvitationCreateSerializer

        data = {
            "role": "parent",
        }
        serializer = InvitationCreateSerializer(data=data)

        assert not serializer.is_valid()
        assert "invitee_email" in serializer.errors

    def test_create_serializer_validates_email_format(self):
        """invitee_email should validate email format."""
        from apps.users.api.serializers import InvitationCreateSerializer

        data = {
            "invitee_email": "not-an-email",
            "role": "parent",
        }
        serializer = InvitationCreateSerializer(data=data)

        assert not serializer.is_valid()
        assert "invitee_email" in serializer.errors

    def test_create_serializer_validates_role_required(self):
        """role field should be required."""
        from apps.users.api.serializers import InvitationCreateSerializer

        data = {
            "invitee_email": "invitee@example.com",
        }
        serializer = InvitationCreateSerializer(data=data)

        assert not serializer.is_valid()
        assert "role" in serializer.errors

    def test_create_serializer_validates_role_choices(self):
        """role should only accept PARENT or CHILD."""
        from apps.users.api.serializers import InvitationCreateSerializer

        # Valid roles
        for role in ["parent", "child"]:
            data = {
                "invitee_email": "invitee@example.com",
                "role": role,
            }
            serializer = InvitationCreateSerializer(data=data)
            assert serializer.is_valid(), f"Role {role} should be valid"

        # Invalid role (ORGANIZER)
        data = {
            "invitee_email": "invitee@example.com",
            "role": "organizer",
        }
        serializer = InvitationCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "role" in serializer.errors

    def test_create_serializer_prevents_inviting_existing_member(self):
        """Cannot invite user who is already a family member."""
        from apps.users.api.serializers import InvitationCreateSerializer

        # Create existing member
        existing_member = User.objects.create_user(
            email="existing@example.com",
            password="testpass123",
        )
        FamilyMember.objects.create(
            family=self.family,
            user=existing_member,
            role=FamilyMember.Role.PARENT,
        )

        data = {
            "invitee_email": "existing@example.com",
            "role": "parent",
        }
        serializer = InvitationCreateSerializer(
            data=data,
            context={"family": self.family}
        )

        assert not serializer.is_valid()
        assert "invitee_email" in serializer.errors

    def test_create_serializer_prevents_duplicate_pending_invitations(self):
        """Cannot create duplicate pending invitation for same email."""
        from apps.users.api.serializers import InvitationCreateSerializer
        from apps.users.models import Invitation

        # Create existing pending invitation
        Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="invitee@example.com",
            family=self.family,
            role="parent",
            status="pending",
        )

        data = {
            "invitee_email": "invitee@example.com",
            "role": "parent",
        }
        serializer = InvitationCreateSerializer(
            data=data,
            context={"family": self.family}
        )

        assert not serializer.is_valid()
        assert "invitee_email" in serializer.errors

    def test_create_serializer_allows_invite_after_previous_accepted(self):
        """Can invite same email after previous invitation was accepted."""
        from apps.users.api.serializers import InvitationCreateSerializer
        from apps.users.models import Invitation

        # Create accepted invitation
        Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="invitee@example.com",
            family=self.family,
            role="parent",
            status="accepted",
        )

        data = {
            "invitee_email": "invitee@example.com",
            "role": "child",
        }
        serializer = InvitationCreateSerializer(
            data=data,
            context={"family": self.family}
        )

        assert serializer.is_valid()

    def test_create_serializer_valid_data(self):
        """Serializer should be valid with correct data."""
        from apps.users.api.serializers import InvitationCreateSerializer

        data = {
            "invitee_email": "newuser@example.com",
            "role": "parent",
        }
        serializer = InvitationCreateSerializer(
            data=data,
            context={"family": self.family}
        )

        assert serializer.is_valid()


@pytest.mark.django_db
class TestInvitationSerializer:
    """Test InvitationSerializer (read-only serializer)."""

    def setup_method(self):
        """Create test users, family, and invitation."""
        self.organizer = User.objects.create_user(
            email="organizer@example.com",
            password="testpass123",
            first_name="Alice",
            last_name="Organizer",
        )
        self.family = Family.objects.create(
            name="Test Family",
            created_by=self.organizer,
        )
        FamilyMember.objects.create(
            family=self.family,
            user=self.organizer,
            role=FamilyMember.Role.ORGANIZER,
        )

        from apps.users.models import Invitation

        self.invitation = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="invitee@example.com",
            family=self.family,
            role="parent",
        )

    def test_invitation_serializer_exists(self):
        """InvitationSerializer should exist."""
        from apps.users.api.serializers import InvitationSerializer

        assert InvitationSerializer is not None

    def test_invitation_serializer_includes_all_fields(self):
        """InvitationSerializer should include all necessary fields."""
        from apps.users.api.serializers import InvitationSerializer

        serializer = InvitationSerializer(instance=self.invitation)
        data = serializer.data

        # Check required fields
        assert "id" in data
        assert "public_id" in data
        assert "token" in data
        assert "invitee_email" in data
        assert "role" in data
        assert "status" in data
        assert "expires_at" in data
        assert "created_at" in data

    def test_invitation_serializer_includes_inviter_details(self):
        """InvitationSerializer should include inviter user details."""
        from apps.users.api.serializers import InvitationSerializer

        serializer = InvitationSerializer(instance=self.invitation)
        data = serializer.data

        assert "inviter" in data
        assert data["inviter"]["email"] == "organizer@example.com"
        assert data["inviter"]["first_name"] == "Alice"

    def test_invitation_serializer_includes_family_name(self):
        """InvitationSerializer should include family name."""
        from apps.users.api.serializers import InvitationSerializer

        serializer = InvitationSerializer(instance=self.invitation)
        data = serializer.data

        assert "family_name" in data
        assert data["family_name"] == "Test Family"

    def test_invitation_serializer_includes_is_expired_field(self):
        """InvitationSerializer should include is_expired computed field."""
        from apps.users.api.serializers import InvitationSerializer

        serializer = InvitationSerializer(instance=self.invitation)
        data = serializer.data

        assert "is_expired" in data
        assert isinstance(data["is_expired"], bool)

    def test_invitation_serializer_is_expired_false_for_future_expiry(self):
        """is_expired should be False for non-expired invitations."""
        from apps.users.api.serializers import InvitationSerializer

        serializer = InvitationSerializer(instance=self.invitation)
        data = serializer.data

        # Invitation created with default 7-day expiry
        assert data["is_expired"] is False

    def test_invitation_serializer_is_expired_true_for_past_expiry(self):
        """is_expired should be True for expired invitations."""
        from apps.users.api.serializers import InvitationSerializer
        from apps.users.models import Invitation

        # Create expired invitation
        expired_invitation = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="expired@example.com",
            family=self.family,
            role="parent",
            expires_at=timezone.now() - timedelta(days=1),
        )

        serializer = InvitationSerializer(instance=expired_invitation)
        data = serializer.data

        assert data["is_expired"] is True
