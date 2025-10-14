"""
Tests for Family Invitation API Endpoints (Enhancement 3 - Phases C, D, E).

Phase C: Invitation Creation Endpoint
Phase D: Invitation Listing & Cancel Endpoints
Phase E: Invitation Accept/Decline Endpoints

Following the TDD Gospel: RED → GREEN → REFACTOR
"""

from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.shared.models import Family, FamilyMember
from apps.users.models import Invitation, User


# ============================================================================
# Phase C: Invitation Creation Endpoint Tests
# ============================================================================


@pytest.mark.django_db
class TestInvitationCreationEndpoint:
    """Test POST /api/v1/families/{public_id}/invitations/ endpoint."""

    def setup_method(self):
        """Create test users, family, and API client."""
        self.client = APIClient()

        # Create organizer
        self.organizer = User.objects.create_user(
            email="organizer@example.com",
            password="testpass123",
            first_name="Alice",
        )

        # Create family
        self.family = Family.objects.create(
            name="Test Family",
            created_by=self.organizer,
        )
        FamilyMember.objects.create(
            family=self.family,
            user=self.organizer,
            role=FamilyMember.Role.ORGANIZER,
        )

        # Create parent member
        self.parent = User.objects.create_user(
            email="parent@example.com",
            password="testpass123",
        )
        FamilyMember.objects.create(
            family=self.family,
            user=self.parent,
            role=FamilyMember.Role.PARENT,
        )

        # Create child member
        self.child = User.objects.create_user(
            email="child@example.com",
            password="testpass123",
        )
        FamilyMember.objects.create(
            family=self.family,
            user=self.child,
            role=FamilyMember.Role.CHILD,
        )

    def test_organizer_can_create_invitation(self):
        """ORGANIZER can create invitation for new member."""
        self.client.force_authenticate(user=self.organizer)

        data = {
            "invitee_email": "newuser@example.com",
            "role": "parent",
        }
        response = self.client.post(
            f"/api/v1/families/{self.family.public_id}/invitations/",
            data=data,
        )

        assert response.status_code == status.HTTP_201_CREATED

    def test_create_invitation_returns_201_with_data(self):
        """Create invitation returns 201 with full invitation data."""
        self.client.force_authenticate(user=self.organizer)

        data = {
            "invitee_email": "newuser@example.com",
            "role": "parent",
        }
        response = self.client.post(
            f"/api/v1/families/{self.family.public_id}/invitations/",
            data=data,
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert "token" in response.data
        assert "invitee_email" in response.data
        assert response.data["invitee_email"] == "newuser@example.com"
        assert response.data["role"] == "parent"
        assert response.data["status"] == "pending"

    def test_create_invitation_auto_generates_token(self):
        """Created invitation has auto-generated token."""
        self.client.force_authenticate(user=self.organizer)

        data = {
            "invitee_email": "newuser@example.com",
            "role": "parent",
        }
        response = self.client.post(
            f"/api/v1/families/{self.family.public_id}/invitations/",
            data=data,
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["token"] is not None

        # Verify token is in database
        invitation = Invitation.objects.get(token=response.data["token"])
        assert invitation is not None

    def test_create_invitation_auto_sets_expires_at(self):
        """Created invitation has expires_at set to 7 days from now."""
        self.client.force_authenticate(user=self.organizer)

        data = {
            "invitee_email": "newuser@example.com",
            "role": "parent",
        }
        now = timezone.now()
        response = self.client.post(
            f"/api/v1/families/{self.family.public_id}/invitations/",
            data=data,
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert "expires_at" in response.data

        # Verify expires_at is approximately 7 days from now
        invitation = Invitation.objects.get(token=response.data["token"])
        expected_expiry = now + timedelta(days=7)
        time_diff = abs((invitation.expires_at - expected_expiry).total_seconds())
        assert time_diff < 60  # Within 1 minute

    @patch("apps.users.tasks.send_invitation_email.delay")
    def test_create_invitation_triggers_email_task(self, mock_task):
        """Creating invitation triggers Celery email task."""
        self.client.force_authenticate(user=self.organizer)

        data = {
            "invitee_email": "newuser@example.com",
            "role": "parent",
        }
        response = self.client.post(
            f"/api/v1/families/{self.family.public_id}/invitations/",
            data=data,
        )

        assert response.status_code == status.HTTP_201_CREATED

        # Verify Celery task was called
        mock_task.assert_called_once()
        invitation = Invitation.objects.get(token=response.data["token"])
        mock_task.assert_called_with(invitation.id)

    def test_create_invitation_400_if_already_member(self):
        """Cannot invite user who is already a family member."""
        self.client.force_authenticate(user=self.organizer)

        data = {
            "invitee_email": "parent@example.com",  # Already a member
            "role": "parent",
        }
        response = self.client.post(
            f"/api/v1/families/{self.family.public_id}/invitations/",
            data=data,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "invitee_email" in response.data

    def test_create_invitation_400_if_duplicate_pending(self):
        """Cannot create duplicate pending invitation for same email."""
        self.client.force_authenticate(user=self.organizer)

        # Create first invitation
        Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="newuser@example.com",
            family=self.family,
            role="parent",
            status="pending",
        )

        # Attempt duplicate
        data = {
            "invitee_email": "newuser@example.com",
            "role": "parent",
        }
        response = self.client.post(
            f"/api/v1/families/{self.family.public_id}/invitations/",
            data=data,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "invitee_email" in response.data

    def test_create_invitation_403_if_not_organizer(self):
        """Only ORGANIZER can create invitations (not PARENT or CHILD)."""
        self.client.force_authenticate(user=self.parent)

        data = {
            "invitee_email": "newuser@example.com",
            "role": "parent",
        }
        response = self.client.post(
            f"/api/v1/families/{self.family.public_id}/invitations/",
            data=data,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_invitation_404_if_family_not_found(self):
        """Returns 404 if family does not exist."""
        self.client.force_authenticate(user=self.organizer)

        data = {
            "invitee_email": "newuser@example.com",
            "role": "parent",
        }
        response = self.client.post(
            "/api/v1/families/00000000-0000-0000-0000-000000000000/invitations/",
            data=data,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_parent_cannot_create_invitation(self):
        """PARENT cannot create invitations."""
        self.client.force_authenticate(user=self.parent)

        data = {
            "invitee_email": "newuser@example.com",
            "role": "parent",
        }
        response = self.client.post(
            f"/api/v1/families/{self.family.public_id}/invitations/",
            data=data,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_child_cannot_create_invitation(self):
        """CHILD cannot create invitations."""
        self.client.force_authenticate(user=self.child)

        data = {
            "invitee_email": "newuser@example.com",
            "role": "parent",
        }
        response = self.client.post(
            f"/api/v1/families/{self.family.public_id}/invitations/",
            data=data,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


# ============================================================================
# Phase D: Invitation Listing & Cancel Endpoint Tests
# ============================================================================


@pytest.mark.django_db
class TestInvitationListingEndpoint:
    """Test GET /api/v1/families/{public_id}/invitations/ endpoint."""

    def setup_method(self):
        """Create test users, family, invitations, and API client."""
        self.client = APIClient()

        # Create organizer
        self.organizer = User.objects.create_user(
            email="organizer@example.com",
            password="testpass123",
        )

        # Create family
        self.family = Family.objects.create(
            name="Test Family",
            created_by=self.organizer,
        )
        FamilyMember.objects.create(
            family=self.family,
            user=self.organizer,
            role=FamilyMember.Role.ORGANIZER,
        )

        # Create parent member
        self.parent = User.objects.create_user(
            email="parent@example.com",
            password="testpass123",
        )
        FamilyMember.objects.create(
            family=self.family,
            user=self.parent,
            role=FamilyMember.Role.PARENT,
        )

        # Create child member
        self.child = User.objects.create_user(
            email="child@example.com",
            password="testpass123",
        )
        FamilyMember.objects.create(
            family=self.family,
            user=self.child,
            role=FamilyMember.Role.CHILD,
        )

        # Create test invitations
        self.pending_invitation = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="pending@example.com",
            family=self.family,
            role="parent",
            status="pending",
        )
        self.accepted_invitation = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="accepted@example.com",
            family=self.family,
            role="parent",
            status="accepted",
        )
        self.declined_invitation = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="declined@example.com",
            family=self.family,
            role="parent",
            status="declined",
        )

    def test_organizer_can_list_invitations(self):
        """ORGANIZER can list all invitations for their family."""
        self.client.force_authenticate(user=self.organizer)

        response = self.client.get(
            f"/api/v1/families/{self.family.public_id}/invitations/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_list_invitations_returns_all_statuses(self):
        """List includes invitations of all statuses."""
        self.client.force_authenticate(user=self.organizer)

        response = self.client.get(
            f"/api/v1/families/{self.family.public_id}/invitations/"
        )

        assert response.status_code == status.HTTP_200_OK
        statuses = [inv["status"] for inv in response.data]
        assert "pending" in statuses
        assert "accepted" in statuses
        assert "declined" in statuses

    def test_list_invitations_includes_is_expired(self):
        """List response includes is_expired field."""
        self.client.force_authenticate(user=self.organizer)

        response = self.client.get(
            f"/api/v1/families/{self.family.public_id}/invitations/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert "is_expired" in response.data[0]

    def test_list_invitations_filter_by_status(self):
        """Can filter invitations by status query param."""
        self.client.force_authenticate(user=self.organizer)

        response = self.client.get(
            f"/api/v1/families/{self.family.public_id}/invitations/?status=pending"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["status"] == "pending"

    def test_list_invitations_403_if_not_organizer(self):
        """PARENT cannot list invitations."""
        self.client.force_authenticate(user=self.parent)

        response = self.client.get(
            f"/api/v1/families/{self.family.public_id}/invitations/"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_parent_cannot_list_invitations(self):
        """PARENT cannot list invitations."""
        self.client.force_authenticate(user=self.parent)

        response = self.client.get(
            f"/api/v1/families/{self.family.public_id}/invitations/"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_child_cannot_list_invitations(self):
        """CHILD cannot list invitations."""
        self.client.force_authenticate(user=self.child)

        response = self.client.get(
            f"/api/v1/families/{self.family.public_id}/invitations/"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestInvitationCancelEndpoint:
    """Test DELETE /api/v1/invitations/{token}/ endpoint."""

    def setup_method(self):
        """Create test users, family, invitations, and API client."""
        self.client = APIClient()

        # Create organizer
        self.organizer = User.objects.create_user(
            email="organizer@example.com",
            password="testpass123",
        )

        # Create family
        self.family = Family.objects.create(
            name="Test Family",
            created_by=self.organizer,
        )
        FamilyMember.objects.create(
            family=self.family,
            user=self.organizer,
            role=FamilyMember.Role.ORGANIZER,
        )

        # Create parent member
        self.parent = User.objects.create_user(
            email="parent@example.com",
            password="testpass123",
        )
        FamilyMember.objects.create(
            family=self.family,
            user=self.parent,
            role=FamilyMember.Role.PARENT,
        )

        # Create child member
        self.child = User.objects.create_user(
            email="child@example.com",
            password="testpass123",
        )
        FamilyMember.objects.create(
            family=self.family,
            user=self.child,
            role=FamilyMember.Role.CHILD,
        )

        # Create test invitation
        self.pending_invitation = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="pending@example.com",
            family=self.family,
            role="parent",
            status="pending",
        )

    def test_organizer_can_cancel_pending_invitation(self):
        """ORGANIZER can cancel pending invitation."""
        self.client.force_authenticate(user=self.organizer)

        response = self.client.delete(
            f"/api/v1/invitations/{self.pending_invitation.token}/"
        )

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]

    def test_cancel_sets_status_to_cancelled(self):
        """Canceling invitation sets status to CANCELLED."""
        self.client.force_authenticate(user=self.organizer)

        response = self.client.delete(
            f"/api/v1/invitations/{self.pending_invitation.token}/"
        )

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]

        # Verify status changed
        self.pending_invitation.refresh_from_db()
        assert self.pending_invitation.status == "cancelled"

    def test_cancel_400_if_already_accepted(self):
        """Cannot cancel already accepted invitation."""
        self.client.force_authenticate(user=self.organizer)

        # Accept the invitation first
        self.pending_invitation.status = "accepted"
        self.pending_invitation.save()

        response = self.client.delete(
            f"/api/v1/invitations/{self.pending_invitation.token}/"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cancel_400_if_already_declined(self):
        """Cannot cancel already declined invitation."""
        self.client.force_authenticate(user=self.organizer)

        # Decline the invitation first
        self.pending_invitation.status = "declined"
        self.pending_invitation.save()

        response = self.client.delete(
            f"/api/v1/invitations/{self.pending_invitation.token}/"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cancel_400_if_already_cancelled(self):
        """Cannot cancel already cancelled invitation."""
        self.client.force_authenticate(user=self.organizer)

        # Cancel the invitation first
        self.pending_invitation.status = "cancelled"
        self.pending_invitation.save()

        response = self.client.delete(
            f"/api/v1/invitations/{self.pending_invitation.token}/"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cancel_403_if_not_organizer(self):
        """PARENT cannot cancel invitation."""
        self.client.force_authenticate(user=self.parent)

        response = self.client.delete(
            f"/api/v1/invitations/{self.pending_invitation.token}/"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cancel_404_if_token_not_found(self):
        """Returns 404 if invitation token not found."""
        self.client.force_authenticate(user=self.organizer)

        response = self.client.delete(
            "/api/v1/invitations/00000000-0000-0000-0000-000000000000/"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_parent_cannot_cancel_invitation(self):
        """PARENT cannot cancel invitation."""
        self.client.force_authenticate(user=self.parent)

        response = self.client.delete(
            f"/api/v1/invitations/{self.pending_invitation.token}/"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_child_cannot_cancel_invitation(self):
        """CHILD cannot cancel invitation."""
        self.client.force_authenticate(user=self.child)

        response = self.client.delete(
            f"/api/v1/invitations/{self.pending_invitation.token}/"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


# ============================================================================
# Phase E: Invitation Accept/Decline Endpoint Tests
# ============================================================================


@pytest.mark.django_db
class TestInvitationAcceptEndpoint:
    """Test POST /api/v1/invitations/{token}/accept/ endpoint."""

    def setup_method(self):
        """Create test users, family, invitations, and API client."""
        self.client = APIClient()

        # Create organizer
        self.organizer = User.objects.create_user(
            email="organizer@example.com",
            password="testpass123",
        )

        # Create family
        self.family = Family.objects.create(
            name="Test Family",
            created_by=self.organizer,
        )
        FamilyMember.objects.create(
            family=self.family,
            user=self.organizer,
            role=FamilyMember.Role.ORGANIZER,
        )

        # Create invitee user
        self.invitee = User.objects.create_user(
            email="invitee@example.com",
            password="testpass123",
        )

        # Create pending invitation
        self.invitation = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="invitee@example.com",
            family=self.family,
            role="parent",
            status="pending",
        )

    def test_accept_creates_family_member(self):
        """Accepting invitation creates FamilyMember record."""
        self.client.force_authenticate(user=self.invitee)

        response = self.client.post(
            f"/api/v1/invitations/{self.invitation.token}/accept/"
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify FamilyMember created
        member = FamilyMember.objects.filter(
            family=self.family, user=self.invitee
        ).first()
        assert member is not None

    def test_accept_creates_member_with_correct_role(self):
        """Accepted member has role from invitation."""
        self.client.force_authenticate(user=self.invitee)

        response = self.client.post(
            f"/api/v1/invitations/{self.invitation.token}/accept/"
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify role matches invitation
        member = FamilyMember.objects.get(family=self.family, user=self.invitee)
        assert member.role == "parent"

    def test_accept_sets_status_to_accepted(self):
        """Accepting invitation sets status to ACCEPTED."""
        self.client.force_authenticate(user=self.invitee)

        response = self.client.post(
            f"/api/v1/invitations/{self.invitation.token}/accept/"
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify status changed
        self.invitation.refresh_from_db()
        assert self.invitation.status == "accepted"

    def test_accept_returns_family_data(self):
        """Accept endpoint returns family data."""
        self.client.force_authenticate(user=self.invitee)

        response = self.client.post(
            f"/api/v1/invitations/{self.invitation.token}/accept/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert "public_id" in response.data
        assert "name" in response.data
        assert response.data["name"] == "Test Family"

    def test_accept_requires_authentication(self):
        """Accept endpoint requires authentication."""
        # No authentication
        response = self.client.post(f"/api/v1/invitations/{self.invitation.token}/accept/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_accept_400_if_expired(self):
        """Cannot accept expired invitation."""
        self.client.force_authenticate(user=self.invitee)

        # Expire the invitation
        self.invitation.expires_at = timezone.now() - timedelta(days=1)
        self.invitation.save()

        response = self.client.post(
            f"/api/v1/invitations/{self.invitation.token}/accept/"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_accept_400_if_not_pending(self):
        """Cannot accept invitation that is not pending."""
        self.client.force_authenticate(user=self.invitee)

        # Accept the invitation first
        self.invitation.status = "accepted"
        self.invitation.save()

        response = self.client.post(
            f"/api/v1/invitations/{self.invitation.token}/accept/"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_accept_400_if_email_mismatch(self):
        """Cannot accept invitation if user email doesn't match."""
        # Create different user
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=other_user)

        response = self.client.post(
            f"/api/v1/invitations/{self.invitation.token}/accept/"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_accept_400_if_already_member(self):
        """Cannot accept invitation if already a family member."""
        self.client.force_authenticate(user=self.invitee)

        # Add user as member first
        FamilyMember.objects.create(
            family=self.family,
            user=self.invitee,
            role=FamilyMember.Role.PARENT,
        )

        response = self.client.post(
            f"/api/v1/invitations/{self.invitation.token}/accept/"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_accept_404_if_token_not_found(self):
        """Returns 404 if invitation token not found."""
        self.client.force_authenticate(user=self.invitee)

        response = self.client.post(
            "/api/v1/invitations/00000000-0000-0000-0000-000000000000/accept/"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_other_user_cannot_accept_invitation(self):
        """User with different email cannot accept invitation."""
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=other_user)

        response = self.client.post(
            f"/api/v1/invitations/{self.invitation.token}/accept/"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestInvitationDeclineEndpoint:
    """Test POST /api/v1/invitations/{token}/decline/ endpoint."""

    def setup_method(self):
        """Create test users, family, invitations, and API client."""
        self.client = APIClient()

        # Create organizer
        self.organizer = User.objects.create_user(
            email="organizer@example.com",
            password="testpass123",
        )

        # Create family
        self.family = Family.objects.create(
            name="Test Family",
            created_by=self.organizer,
        )
        FamilyMember.objects.create(
            family=self.family,
            user=self.organizer,
            role=FamilyMember.Role.ORGANIZER,
        )

        # Create invitee user
        self.invitee = User.objects.create_user(
            email="invitee@example.com",
            password="testpass123",
        )

        # Create pending invitation
        self.invitation = Invitation.objects.create(
            inviter=self.organizer,
            invitee_email="invitee@example.com",
            family=self.family,
            role="parent",
            status="pending",
        )

    def test_decline_sets_status_to_declined(self):
        """Declining invitation sets status to DECLINED."""
        self.client.force_authenticate(user=self.invitee)

        response = self.client.post(
            f"/api/v1/invitations/{self.invitation.token}/decline/"
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify status changed
        self.invitation.refresh_from_db()
        assert self.invitation.status == "declined"

    def test_decline_requires_authentication(self):
        """Decline endpoint requires authentication."""
        # No authentication
        response = self.client.post(
            f"/api/v1/invitations/{self.invitation.token}/decline/"
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_decline_400_if_expired(self):
        """Cannot decline expired invitation."""
        self.client.force_authenticate(user=self.invitee)

        # Expire the invitation
        self.invitation.expires_at = timezone.now() - timedelta(days=1)
        self.invitation.save()

        response = self.client.post(
            f"/api/v1/invitations/{self.invitation.token}/decline/"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_decline_400_if_not_pending(self):
        """Cannot decline invitation that is not pending."""
        self.client.force_authenticate(user=self.invitee)

        # Decline the invitation first
        self.invitation.status = "declined"
        self.invitation.save()

        response = self.client.post(
            f"/api/v1/invitations/{self.invitation.token}/decline/"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_decline_400_if_email_mismatch(self):
        """Cannot decline invitation if user email doesn't match."""
        # Create different user
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=other_user)

        response = self.client.post(
            f"/api/v1/invitations/{self.invitation.token}/decline/"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_decline_404_if_token_not_found(self):
        """Returns 404 if invitation token not found."""
        self.client.force_authenticate(user=self.invitee)

        response = self.client.post(
            "/api/v1/invitations/00000000-0000-0000-0000-000000000000/decline/"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_other_user_cannot_decline_invitation(self):
        """User with different email cannot decline invitation."""
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=other_user)

        response = self.client.post(
            f"/api/v1/invitations/{self.invitation.token}/decline/"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
