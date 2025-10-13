"""
API views for the invitations app
TDD approach - implementing to pass our API tests!
"""

from django.contrib.auth import get_user_model
from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.invitations.models import Invitation
from apps.invitations.api.serializers import (
    InvitationCreateSerializer,
    InvitationListSerializer,
    InvitationAcceptSerializer,
    InvitationVerifySerializer,
)
from apps.invitations.permissions import (
    CanSendInvitations,
    CanManageInvitations,
    IsOwnerOrAdmin,
)
from apps.invitations.services import (
    InvitationService,
    BulkInvitationService,
    InvitationStatsService,
    InvitationExpiryService,
)
from apps.invitations.services.permission_service import PermissionService

User = get_user_model()


class InvitationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing invitations - Refactored with Service Layer

    list: Get all invitations sent by the current user (or all for admins)
    create: Send a new invitation (admins and managers only)
    retrieve: Get details of a specific invitation
    destroy: Cancel an invitation
    resend: Resend an invitation with new token

    Ham Dog & TC's Refactored Architecture:
    - Business logic extracted to service layer
    - ViewSet focuses only on HTTP concerns
    - Clean dependency injection pattern
    """

    lookup_field = "public_id"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dependency injection for service layer
        self.permission_service = PermissionService()
        self.invitation_service = InvitationService()
        self.bulk_service = BulkInvitationService()
        self.stats_service = InvitationStatsService(self.permission_service)
        self.expiry_service = InvitationExpiryService(self.permission_service)

    def get_permissions(self):
        """Return appropriate permission classes based on action"""
        if self.action == "create":
            # Only admins and managers can send invitations
            permission_classes = [IsAuthenticated, CanSendInvitations]
        elif self.action in ["resend", "destroy"]:
            # Can manage own invitations or admin can manage all
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        elif self.action in ["list", "retrieve"]:
            # Authenticated users can view
            permission_classes = [IsAuthenticated]
        elif self.action in ["accept", "verify"]:
            # Public endpoints
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Return invitations based on user's role:
        - Admins see all invitations
        - Regular users see only their sent invitations

        Optimized with select_related to avoid N+1 queries
        """
        queryset = (
            Invitation.objects.active()
            .select_related("invited_by", "accepted_by", "created_by", "updated_by")
            .order_by("-created_at")
        )

        # Apply permission-based filtering first
        if not self.permission_service.can_view_all_invitations(self.request.user):
            # Regular users only see invitations they sent
            queryset = queryset.filter(invited_by=self.request.user)

        # Apply query parameter filters
        status = self.request.query_params.get("status")
        role = self.request.query_params.get("role")
        email = self.request.query_params.get("email")
        search = self.request.query_params.get("search")
        expired = self.request.query_params.get("expired")

        if status:
            queryset = queryset.filter(status=status)

        if role:
            queryset = queryset.filter(role=role)

        if email:
            queryset = queryset.filter(email__icontains=email)

        if search:
            queryset = queryset.filter(
                models.Q(email__icontains=search)
                | models.Q(organization_name__icontains=search)
                | models.Q(invited_by__email__icontains=search)
            )

        if expired is not None:
            from django.utils import timezone

            if expired.lower() in ["true", "1"]:
                queryset = queryset.filter(expires_at__lt=timezone.now())
            elif expired.lower() in ["false", "0"]:
                queryset = queryset.filter(expires_at__gte=timezone.now())

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "create":
            return InvitationCreateSerializer
        return InvitationListSerializer

    def destroy(self, request, *args, **kwargs):
        """Cancel an invitation (set status to cancelled)"""
        invitation = self.get_object()
        result = self.invitation_service.cancel_invitation(invitation)

        if not result["success"]:
            return Response(
                {"error": result["error"]}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def resend(self, request, public_id=None):
        """Resend an invitation with a new token"""
        invitation = self.get_object()
        custom_message = request.data.get("message")

        result = self.invitation_service.resend_invitation(invitation, custom_message)

        if not result["success"]:
            return Response(
                {
                    "error": result["error"],
                    "message": result.get("message", "Cannot resend invitation"),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"message": result["message"]}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def accept(self, request):
        """
        Accept an invitation (public endpoint)
        Creates a new user account and returns JWT tokens
        """
        # Keep existing serializer logic as it handles JWT generation
        serializer = InvitationAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user, invitation = serializer.save()

        # Generate JWT tokens (keeping existing logic)
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "public_id": str(user.public_id),
                },
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def verify(self, request):
        """
        Verify an invitation token (public endpoint)
        Returns invitation details if valid
        """
        token = request.query_params.get("token")

        if not token:
            return Response(
                {"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        invitation_data = self.invitation_service.verify_invitation_token(token)

        if not invitation_data["is_valid"]:
            return Response(
                {"error": invitation_data.get("message", "Invalid invitation token")},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = InvitationVerifySerializer(invitation_data["invitation"])
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """
        Get invitation statistics
        Only admins and managers can see stats
        """
        # Check permission using centralized service
        if not self.permission_service.can_view_stats(request.user):
            return Response(
                {"error": "You do not have permission to view statistics"},
                status=status.HTTP_403_FORBIDDEN,
            )

        stats_data = self.stats_service.calculate_stats(request.user)
        return Response(stats_data)

    @action(detail=False, methods=["get"])
    def my_invitations(self, request):
        """
        Get invitations sent by the current user
        Optimized with select_related for foreign keys
        """
        invitations = self.invitation_service.get_my_invitations(request.user)
        serializer = InvitationListSerializer(invitations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def pending_count(self, request):
        """
        Get count of pending invitations
        """
        count = self.stats_service.get_pending_count(request.user)
        return Response({"count": count})

    @action(detail=False, methods=["get"])
    def check_email(self, request):
        """
        Check if an email already has a pending invitation
        """
        email = request.query_params.get("email")

        if not email:
            return Response(
                {"error": "Email parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        exists = self.invitation_service.check_email_exists(email)
        return Response({"exists": exists})

    @action(detail=True, methods=["post"])
    def cancel(self, request, public_id=None):
        """Cancel an invitation"""
        invitation = self.get_object()

        result = self.invitation_service.cancel_invitation(invitation)

        if not result["success"]:
            return Response(
                {"error": result["error"]}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = InvitationListSerializer(result["invitation"])
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def extend_expiry(self, request, public_id=None):
        """
        Extend the expiry date of an invitation
        Only admins can extend expiry
        """
        # Check permission first using centralized service
        if not self.permission_service.can_extend_expiry(request.user):
            return Response(
                {"error": "Only administrators can extend invitation expiry"},
                status=status.HTTP_403_FORBIDDEN,
            )

        invitation = self.get_object()
        days = request.data.get("days", 7)

        result = self.expiry_service.extend_expiry(invitation, days, request.user)

        if not result["success"]:
            return Response(
                {"error": result["error"]}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = InvitationListSerializer(result["invitation"])
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def bulk_invite(self, request):
        """
        Send bulk invitations
        Only admins and managers can send bulk invitations
        """
        # Check permission using centralized service
        if not self.permission_service.can_send_bulk_invitations(request.user):
            return Response(
                {"error": "You do not have permission to send bulk invitations"},
                status=status.HTTP_403_FORBIDDEN,
            )

        emails = request.data.get("emails", [])
        role = request.data.get("role", "member")
        organization_name = request.data.get("organization_name")
        message = request.data.get("message")

        result = self.bulk_service.process_bulk_invitations(
            emails=emails,
            invited_by=request.user,
            role=role,
            message=message,
            organization_name=organization_name,
        )

        response_status = (
            status.HTTP_201_CREATED
            if result["successful"]
            else status.HTTP_400_BAD_REQUEST
        )
        return Response(result, status=response_status)
