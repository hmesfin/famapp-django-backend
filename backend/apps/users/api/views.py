from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ViewSet

from apps.shared.models import FamilyMember
from apps.shared.serializers import FamilySerializer
from apps.users.models import Invitation
from apps.users.models import User

from .serializers import UserSerializer


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "public_id"

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(public_id=self.request.user.public_id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(detail=False, methods=["get"])
    def search(self, request):
        """Search for users by email or name"""
        query = request.query_params.get("q", "").strip()

        if len(query) < 2:
            return Response([])

        # Search by email, first name, or last name
        users = User.objects.filter(
            Q(email__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query),
        ).exclude(
            public_id=request.user.public_id,  # Exclude current user
        )[:10]  # Limit to 10 results

        serializer = UserSerializer(users, many=True, context={"request": request})
        return Response(serializer.data)


class InvitationViewSet(ViewSet):
    """
    ViewSet for Invitation operations (Enhancement 3).

    Endpoints:
    - DELETE /api/v1/invitations/{token}/ - Cancel invitation (organizers only)
    - POST /api/v1/invitations/{token}/accept/ - Accept invitation (invitee only)
    - POST /api/v1/invitations/{token}/decline/ - Decline invitation (invitee only)
    """

    permission_classes = [IsAuthenticated]
    lookup_field = "token"

    def destroy(self, request, token=None):
        """
        DELETE /api/v1/invitations/{token}/ - Cancel pending invitation.

        Only ORGANIZER of the invitation's family can cancel.
        Invitation must be in PENDING status.
        """
        # Get invitation by token
        invitation = get_object_or_404(Invitation, token=token)

        # Check permission: only ORGANIZER can cancel
        is_organizer = FamilyMember.objects.filter(
            family=invitation.family,
            user=request.user,
            role=FamilyMember.Role.ORGANIZER,
        ).exists()

        if not is_organizer:
            return Response(
                {"detail": "You must be a family organizer to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Check status is PENDING
        if invitation.status != Invitation.Status.PENDING:
            return Response(
                {
                    "detail": f"Cannot cancel invitation with status '{invitation.status}'. "
                    "Only pending invitations can be cancelled.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Set status to CANCELLED
        invitation.status = Invitation.Status.CANCELLED
        invitation.updated_by = request.user
        invitation.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def accept(self, request, token=None):
        """
        POST /api/v1/invitations/{token}/accept/ - Accept invitation.

        Creates FamilyMember record and sets invitation status to ACCEPTED.
        Validates:
        - Invitation is PENDING
        - Not expired
        - User email matches invitee_email
        - User is not already a family member
        """
        # Get invitation by token
        invitation = get_object_or_404(Invitation, token=token)

        # Validate: status == PENDING
        if invitation.status != Invitation.Status.PENDING:
            return Response(
                {
                    "detail": f"Cannot accept invitation with status '{invitation.status}'. "
                    "Only pending invitations can be accepted.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate: not expired
        if invitation.is_expired:
            return Response(
                {"detail": "This invitation has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate: email matches (case-insensitive)
        if request.user.email.lower() != invitation.invitee_email.lower():
            return Response(
                {
                    "detail": "This invitation was sent to a different email address. "
                    "Please use the account associated with the invitation.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate: user not already a member
        if FamilyMember.objects.filter(
            family=invitation.family,
            user=request.user,
        ).exists():
            return Response(
                {"detail": "You are already a member of this family."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create FamilyMember and update invitation status atomically
        with transaction.atomic():
            # Create membership
            FamilyMember.objects.create(
                family=invitation.family,
                user=request.user,
                role=invitation.role,
            )

            # Update invitation status
            invitation.status = Invitation.Status.ACCEPTED
            invitation.updated_by = request.user
            invitation.save()

        # Return family data
        family_serializer = FamilySerializer(invitation.family)
        return Response(family_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def decline(self, request, token=None):
        """
        POST /api/v1/invitations/{token}/decline/ - Decline invitation.

        Sets invitation status to DECLINED.
        Validates:
        - Invitation is PENDING
        - Not expired
        - User email matches invitee_email
        """
        # Get invitation by token
        invitation = get_object_or_404(Invitation, token=token)

        # Validate: status == PENDING
        if invitation.status != Invitation.Status.PENDING:
            return Response(
                {
                    "detail": f"Cannot decline invitation with status '{invitation.status}'. "
                    "Only pending invitations can be declined.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate: not expired
        if invitation.is_expired:
            return Response(
                {"detail": "This invitation has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate: email matches (case-insensitive)
        if request.user.email.lower() != invitation.invitee_email.lower():
            return Response(
                {
                    "detail": "This invitation was sent to a different email address. "
                    "Please use the account associated with the invitation.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update invitation status
        invitation.status = Invitation.Status.DECLINED
        invitation.updated_by = request.user
        invitation.save()

        return Response(
            {"detail": "Invitation declined successfully."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="switch-family")
    def switch_family(self, request, token=None):
        """
        POST /api/v1/invitations/{token}/switch-family/ - Switch from current family to invited family.

        This handles the "Existing User" flow where a user already belongs to a family
        but wants to join a different one via invitation.

        Process:
        1. Validates invitation is valid
        2. Checks user has an existing family membership
        3. If user is ORGANIZER with other members, BLOCKS the switch
        4. Deletes current family membership (and family if user is sole ORGANIZER)
        5. Joins invited family with new role

        This action is IRREVERSIBLE.

        Expected payload:
        {
            "confirm": true  // User must explicitly confirm
        }
        """
        import logging

        from apps.shared.models import Family

        logger = logging.getLogger(__name__)

        # Get invitation by token
        invitation = get_object_or_404(Invitation, token=token)

        # Validate: status == PENDING
        if invitation.status != Invitation.Status.PENDING:
            return Response(
                {
                    "detail": f"Cannot accept invitation with status '{invitation.status}'. "
                    "Only pending invitations can be accepted.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate: not expired
        if invitation.is_expired:
            return Response(
                {"detail": "This invitation has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate: email matches (case-insensitive)
        if request.user.email.lower() != invitation.invitee_email.lower():
            return Response(
                {
                    "detail": "This invitation was sent to a different email address. "
                    "Please use the account associated with the invitation.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check user has existing family membership
        existing_membership = (
            FamilyMember.objects.select_related("family")
            .filter(user=request.user)
            .first()
        )

        if not existing_membership:
            return Response(
                {
                    "detail": "You don't belong to any family. Use the regular accept endpoint instead.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if user explicitly confirmed
        confirm = request.data.get("confirm", False)
        if not confirm:
            return Response(
                {
                    "detail": "You must confirm this action by setting 'confirm' to true.",
                    "warning": "Switching families is IRREVERSIBLE. You will leave your current family.",
                    "current_family": {
                        "public_id": str(existing_membership.family.public_id),
                        "name": existing_membership.family.name,
                        "role": existing_membership.role,
                    },
                    "new_family": {
                        "public_id": str(invitation.family.public_id),
                        "name": invitation.family.name,
                        "role": invitation.role,
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # CRITICAL: If user is ORGANIZER, check if there are other members
        if existing_membership.role == FamilyMember.Role.ORGANIZER:
            other_members_count = (
                FamilyMember.objects.filter(family=existing_membership.family)
                .exclude(user=request.user)
                .count()
            )

            if other_members_count > 0:
                return Response(
                    {
                        "detail": "You cannot leave this family as the organizer while other members exist. "
                        "Please remove all other members first, or transfer ownership.",
                        "other_members_count": other_members_count,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # All validations passed - perform the switch atomically
        with transaction.atomic():
            current_family = existing_membership.family
            was_sole_organizer = (
                existing_membership.role == FamilyMember.Role.ORGANIZER
                and FamilyMember.objects.filter(family=current_family).count() == 1
            )

            # Delete current membership
            existing_membership.delete()

            # If user was the sole member (ORGANIZER), delete the family too
            if was_sole_organizer:
                current_family.delete()
                logger.info(
                    f"Deleted family {current_family.name} as user {request.user.email} was sole member"
                )

            # Create new membership in invited family
            new_membership = FamilyMember.objects.create(
                family=invitation.family,
                user=request.user,
                role=invitation.role,
            )

            # Mark invitation as accepted
            invitation.status = Invitation.Status.ACCEPTED
            invitation.updated_by = request.user
            invitation.save()

            logger.info(
                f"User {request.user.email} switched from family to {invitation.family.name}"
            )

        # Return new family data
        family_serializer = FamilySerializer(invitation.family)
        return Response(
            {
                "detail": "Successfully switched families.",
                "family": family_serializer.data,
                "role": new_membership.role,
            },
            status=status.HTTP_200_OK,
        )
