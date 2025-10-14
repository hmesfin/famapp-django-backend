"""
Tests for Phase G: Signup with Invitation Flow

The Mobile-First Money Shot: Users can join families during registration!

Test Flow:
1. User receives invitation email
2. Clicks link or enters token during signup
3. Completes registration with invitation_token
4. Verifies OTP
5. BOOM! Auto-joins invited family + has own auto-created family

Following Ham Dog & TC's TDD Philosophy:
- Tests FIRST, implementation SECOND
- RED-GREEN-REFACTOR cycle
- No code exists until there's a test that needs it
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.shared.models import Family
from apps.shared.models import FamilyMember
from apps.users.models import Invitation

User = get_user_model()


@pytest.mark.django_db
class TestSignupWithInvitation:
    """Test registration flow with invitation token (Phase G)."""

    def setup_method(self):
        """Setup test data before each test."""
        cache.clear()
        self.client = APIClient()

        # Create inviter user and family
        self.inviter = User.objects.create_user(
            email="inviter@example.com",
            password="testpass123",
            first_name="Inviter",
            last_name="User",
        )

        self.family = Family.objects.create(
            name="Inviter's Family",
            created_by=self.inviter,
        )

        FamilyMember.objects.create(
            user=self.inviter,
            family=self.family,
            role=FamilyMember.Role.ORGANIZER,
        )

    def teardown_method(self):
        """Clear cache after each test."""
        cache.clear()

    def test_register_accepts_optional_invitation_token(self):
        """Registration endpoint accepts optional invitation_token field."""
        # Arrange: Create invitation
        invitation = Invitation.objects.create(
            inviter=self.inviter,
            invitee_email="newuser@example.com",
            family=self.family,
            role=Invitation.Role.PARENT,
            created_by=self.inviter,
        )

        # Act: Register with invitation_token
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "New",
                "last_name": "User",
                "invitation_token": str(invitation.token),
            },
            format="json",
        )

        # Assert: Should succeed
        assert response.status_code == 201
        assert "user" in response.data
        assert response.data["user"]["email"] == "newuser@example.com"

    def test_register_without_invitation_token_still_works(self):
        """Registration without invitation_token works (backward compatible)."""
        # Act: Register without invitation_token
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "normaluser@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "Normal",
                "last_name": "User",
            },
            format="json",
        )

        # Assert: Should succeed normally
        assert response.status_code == 201
        assert "user" in response.data

    def test_register_with_invalid_invitation_token_returns_400(self):
        """Registration with invalid invitation token returns 400."""
        import uuid

        # Act: Register with invalid token
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "New",
                "last_name": "User",
                "invitation_token": str(uuid.uuid4()),  # Random invalid token
            },
            format="json",
        )

        # Assert: Should return 400 with error
        assert response.status_code == 400
        assert "invitation_token" in response.data

    def test_register_with_expired_invitation_returns_400(self):
        """Registration with expired invitation returns 400."""
        from datetime import timedelta

        from django.utils import timezone

        # Arrange: Create expired invitation
        invitation = Invitation.objects.create(
            inviter=self.inviter,
            invitee_email="newuser@example.com",
            family=self.family,
            role=Invitation.Role.PARENT,
            created_by=self.inviter,
        )

        # Manually set expires_at to past
        invitation.expires_at = timezone.now() - timedelta(days=1)
        invitation.save()

        # Act: Register with expired token
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "New",
                "last_name": "User",
                "invitation_token": str(invitation.token),
            },
            format="json",
        )

        # Assert: Should return 400
        assert response.status_code == 400
        assert "invitation_token" in response.data
        assert "expired" in str(response.data["invitation_token"]).lower()

    def test_register_email_must_match_invitation(self):
        """Registration requires email to match invitation email."""
        # Arrange: Create invitation for specific email
        invitation = Invitation.objects.create(
            inviter=self.inviter,
            invitee_email="invited@example.com",
            family=self.family,
            role=Invitation.Role.PARENT,
            created_by=self.inviter,
        )

        # Act: Register with different email
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "wrong@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "Wrong",
                "last_name": "User",
                "invitation_token": str(invitation.token),
            },
            format="json",
        )

        # Assert: Should return 400
        assert response.status_code == 400
        assert "invitation_token" in response.data
        assert "invited@example.com" in str(response.data["invitation_token"])

    def test_register_email_match_case_insensitive(self):
        """Email matching is case-insensitive for invitation."""
        # Arrange: Create invitation with lowercase email
        invitation = Invitation.objects.create(
            inviter=self.inviter,
            invitee_email="invited@example.com",
            family=self.family,
            role=Invitation.Role.PARENT,
            created_by=self.inviter,
        )

        # Act: Register with uppercase email
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "INVITED@EXAMPLE.COM",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "Invited",
                "last_name": "User",
                "invitation_token": str(invitation.token),
            },
            format="json",
        )

        # Assert: Should succeed (case-insensitive match)
        assert response.status_code == 201

    def test_verify_otp_with_invitation_auto_joins_family(self):
        """After OTP verification, user auto-joins invited family."""
        from apps.users.otp import get_otp

        # Arrange: Create invitation
        invitation = Invitation.objects.create(
            inviter=self.inviter,
            invitee_email="newuser@example.com",
            family=self.family,
            role=Invitation.Role.PARENT,
            created_by=self.inviter,
        )

        # Register with invitation token
        register_response = self.client.post(
            "/api/auth/register/",
            {
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "New",
                "last_name": "User",
                "invitation_token": str(invitation.token),
            },
            format="json",
        )
        assert register_response.status_code == 201

        # Get OTP from Redis
        otp = get_otp("newuser@example.com")
        assert otp is not None

        # Act: Verify OTP
        verify_response = self.client.post(
            "/api/auth/verify-otp/",
            {
                "email": "newuser@example.com",
                "otp": otp,
            },
            format="json",
        )

        # Assert: User should be member of invited family
        assert verify_response.status_code == 200

        user = User.objects.get(email="newuser@example.com")
        assert FamilyMember.objects.filter(user=user, family=self.family).exists()

    def test_verify_otp_with_invitation_sets_correct_role(self):
        """User gets role from invitation (PARENT or CHILD)."""
        from apps.users.otp import get_otp

        # Arrange: Create invitation with CHILD role
        invitation = Invitation.objects.create(
            inviter=self.inviter,
            invitee_email="child@example.com",
            family=self.family,
            role=Invitation.Role.CHILD,
            created_by=self.inviter,
        )

        # Register with invitation token
        register_response = self.client.post(
            "/api/auth/register/",
            {
                "email": "child@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "Child",
                "last_name": "User",
                "invitation_token": str(invitation.token),
            },
            format="json",
        )
        assert register_response.status_code == 201

        # Get OTP and verify
        otp = get_otp("child@example.com")
        verify_response = self.client.post(
            "/api/auth/verify-otp/",
            {"email": "child@example.com", "otp": otp},
            format="json",
        )

        # Assert: User should have CHILD role
        assert verify_response.status_code == 200
        user = User.objects.get(email="child@example.com")
        member = FamilyMember.objects.get(user=user, family=self.family)
        assert member.role == FamilyMember.Role.CHILD

    def test_verify_otp_with_invitation_marks_accepted(self):
        """Invitation status set to ACCEPTED after signup completion."""
        from apps.users.otp import get_otp

        # Arrange: Create invitation
        invitation = Invitation.objects.create(
            inviter=self.inviter,
            invitee_email="newuser@example.com",
            family=self.family,
            role=Invitation.Role.PARENT,
            created_by=self.inviter,
        )

        # Verify initial status is PENDING
        assert invitation.status == Invitation.Status.PENDING

        # Register and verify OTP
        self.client.post(
            "/api/auth/register/",
            {
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "New",
                "last_name": "User",
                "invitation_token": str(invitation.token),
            },
            format="json",
        )

        otp = get_otp("newuser@example.com")
        self.client.post(
            "/api/auth/verify-otp/",
            {"email": "newuser@example.com", "otp": otp},
            format="json",
        )

        # Assert: Invitation status should be ACCEPTED
        invitation.refresh_from_db()
        assert invitation.status == Invitation.Status.ACCEPTED

    def test_verify_otp_with_invitation_returns_invited_family_data(self):
        """Verify-OTP response includes invited family info."""
        from apps.users.otp import get_otp

        # Arrange: Create invitation
        invitation = Invitation.objects.create(
            inviter=self.inviter,
            invitee_email="newuser@example.com",
            family=self.family,
            role=Invitation.Role.PARENT,
            created_by=self.inviter,
        )

        # Register and verify OTP
        self.client.post(
            "/api/auth/register/",
            {
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "New",
                "last_name": "User",
                "invitation_token": str(invitation.token),
            },
            format="json",
        )

        otp = get_otp("newuser@example.com")
        verify_response = self.client.post(
            "/api/auth/verify-otp/",
            {"email": "newuser@example.com", "otp": otp},
            format="json",
        )

        # Assert: Response should include invited family
        assert verify_response.status_code == 200
        assert "families" in verify_response.data or "invited_family" in verify_response.data

    def test_signup_with_invitation_user_has_both_families(self):
        """User has both invited family AND auto-created family."""
        from apps.users.otp import get_otp

        # Arrange: Create invitation
        invitation = Invitation.objects.create(
            inviter=self.inviter,
            invitee_email="newuser@example.com",
            family=self.family,
            role=Invitation.Role.PARENT,
            created_by=self.inviter,
        )

        # Register and verify OTP
        self.client.post(
            "/api/auth/register/",
            {
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "New",
                "last_name": "User",
                "invitation_token": str(invitation.token),
            },
            format="json",
        )

        otp = get_otp("newuser@example.com")
        self.client.post(
            "/api/auth/verify-otp/",
            {"email": "newuser@example.com", "otp": otp},
            format="json",
        )

        # Assert: User should be member of 2 families
        user = User.objects.get(email="newuser@example.com")
        memberships = FamilyMember.objects.filter(user=user)

        assert memberships.count() == 2

        # One membership should be ORGANIZER (auto-created family)
        # One membership should be PARENT (invited family)
        roles = [m.role for m in memberships]
        assert FamilyMember.Role.ORGANIZER in roles
        assert FamilyMember.Role.PARENT in roles

        # Verify invited family membership
        assert memberships.filter(family=self.family, role=FamilyMember.Role.PARENT).exists()

    def test_expired_invitation_during_otp_verify_fails_gracefully(self):
        """If invitation expires between register and verify, handle gracefully."""
        from datetime import timedelta

        from django.utils import timezone

        from apps.users.otp import get_otp

        # Arrange: Create invitation
        invitation = Invitation.objects.create(
            inviter=self.inviter,
            invitee_email="newuser@example.com",
            family=self.family,
            role=Invitation.Role.PARENT,
            created_by=self.inviter,
        )

        # Register with invitation token
        self.client.post(
            "/api/auth/register/",
            {
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "New",
                "last_name": "User",
                "invitation_token": str(invitation.token),
            },
            format="json",
        )

        # Expire the invitation before OTP verification
        invitation.expires_at = timezone.now() - timedelta(days=1)
        invitation.save()

        # Get OTP and verify
        otp = get_otp("newuser@example.com")
        verify_response = self.client.post(
            "/api/auth/verify-otp/",
            {"email": "newuser@example.com", "otp": otp},
            format="json",
        )

        # Assert: Should still succeed but without joining invited family
        assert verify_response.status_code == 200

        user = User.objects.get(email="newuser@example.com")

        # User should NOT be member of invited family (expired)
        assert not FamilyMember.objects.filter(user=user, family=self.family).exists()

        # User should still have auto-created family (fallback)
        assert FamilyMember.objects.filter(
            user=user, role=FamilyMember.Role.ORGANIZER
        ).exists()

    def test_register_with_non_pending_invitation_returns_400(self):
        """Cannot register with invitation that's not PENDING."""
        # Arrange: Create invitation and mark as ACCEPTED
        invitation = Invitation.objects.create(
            inviter=self.inviter,
            invitee_email="newuser@example.com",
            family=self.family,
            role=Invitation.Role.PARENT,
            created_by=self.inviter,
        )
        invitation.status = Invitation.Status.ACCEPTED
        invitation.save()

        # Act: Try to register with non-pending invitation
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "New",
                "last_name": "User",
                "invitation_token": str(invitation.token),
            },
            format="json",
        )

        # Assert: Should return 400
        assert response.status_code == 400
        assert "invitation_token" in response.data

    def test_signup_flow_end_to_end_with_invitation(self):
        """Complete signup flow with invitation (E2E test)."""
        from apps.users.otp import get_otp

        # Arrange: Create invitation
        invitation = Invitation.objects.create(
            inviter=self.inviter,
            invitee_email="complete@example.com",
            family=self.family,
            role=Invitation.Role.PARENT,
            created_by=self.inviter,
        )

        # Step 1: Register with invitation
        register_response = self.client.post(
            "/api/auth/register/",
            {
                "email": "complete@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "Complete",
                "last_name": "User",
                "invitation_token": str(invitation.token),
            },
            format="json",
        )
        assert register_response.status_code == 201

        # Step 2: Get OTP from Redis
        otp = get_otp("complete@example.com")
        assert otp is not None

        # Step 3: Verify OTP
        verify_response = self.client.post(
            "/api/auth/verify-otp/",
            {"email": "complete@example.com", "otp": otp},
            format="json",
        )
        assert verify_response.status_code == 200

        # Step 4: Verify all expected outcomes
        user = User.objects.get(email="complete@example.com")

        # User is verified
        assert user.email_verified is True

        # Invitation is accepted
        invitation.refresh_from_db()
        assert invitation.status == Invitation.Status.ACCEPTED

        # User has 2 families (invited + auto-created)
        assert FamilyMember.objects.filter(user=user).count() == 2

        # User is member of invited family with PARENT role
        invited_membership = FamilyMember.objects.get(user=user, family=self.family)
        assert invited_membership.role == FamilyMember.Role.PARENT

        # User has auto-created family with ORGANIZER role
        auto_family_membership = FamilyMember.objects.get(
            user=user, role=FamilyMember.Role.ORGANIZER
        )
        assert auto_family_membership.family.name == "Complete's Family"

        # Response includes JWT tokens
        assert "access" in verify_response.data
        assert "refresh" in verify_response.data

        # Step 5: User can login with tokens
        access_token = verify_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        profile_response = self.client.get("/api/auth/profile/")
        assert profile_response.status_code == 200
        assert profile_response.data["user"]["email"] == "complete@example.com"
