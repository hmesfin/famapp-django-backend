"""
DRF ViewSets for FamApp API endpoints.

Following TDD methodology and DRF best practices:
- Token authentication (drf-simplejwt)
- Permission-based authorization (IsFamilyMember, IsFamilyAdmin)
- Soft deletes for all models
- public_id (UUID) in URLs, NOT integer id

Ham Dog & TC building family collaboration APIs! 🚀
"""

from django.db.models import Count, OuterRef, Subquery
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.shared.models import Family, FamilyMember
from apps.shared.permissions import IsFamilyAdmin, IsFamilyMember
from apps.shared.serializers import (
    FamilyCreateSerializer,
    FamilyDetailSerializer,
    FamilySerializer,
    FamilyUpdateSerializer,
)


class FamilyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Family CRUD operations.

    Endpoints:
    - POST /api/v1/families/ - Create family (authenticated users)
    - GET /api/v1/families/ - List families (user's families only)
    - GET /api/v1/families/{public_id}/ - Retrieve family details (members only)
    - PATCH /api/v1/families/{public_id}/ - Update family (organizers only)
    - DELETE /api/v1/families/{public_id}/ - Soft delete family (organizers only)

    CRITICAL: All URLs use public_id (UUID), NOT integer id!
    """

    lookup_field = "public_id"
    lookup_url_kwarg = "public_id"

    def get_permissions(self):
        """
        Set permissions based on action.

        - create/list: IsAuthenticated only
        - retrieve: IsFamilyMember (view-level check)
        - update/partial_update/destroy: IsFamilyAdmin (organizers only)
        """
        if self.action == "create":
            permission_classes = [IsAuthenticated]
        elif self.action in ["list"]:
            permission_classes = [IsAuthenticated]
        elif self.action in ["retrieve"]:
            permission_classes = [IsAuthenticated, IsFamilyMember]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, IsFamilyAdmin]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter queryset based on action.

        - list: Return families where user is a member (with member_count annotation)
        - retrieve/update/destroy: Return families where user is a member
        - Exclude soft-deleted families
        """
        user = self.request.user

        if self.action == "list":
            # Annotate with member count for list view
            # First get families where user is a member
            # Then annotate with member count (separate from the filter)
            user_family_ids = FamilyMember.objects.filter(user=user).values_list(
                "family_id", flat=True
            )
            return (
                Family.objects.filter(id__in=user_family_ids, is_deleted=False)
                .annotate(member_count=Count("familymember"))
                .order_by("-created_at")
            )

        # For retrieve/update/destroy, just filter by membership
        return Family.objects.filter(members=user, is_deleted=False)

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.

        - create: FamilyCreateSerializer (name only)
        - update/partial_update: FamilyUpdateSerializer (partial updates)
        - retrieve: FamilyDetailSerializer (includes members)
        - list: FamilySerializer (basic info + member_count)
        """
        if self.action == "create":
            return FamilyCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return FamilyUpdateSerializer
        elif self.action == "retrieve":
            return FamilyDetailSerializer
        else:
            return FamilySerializer

    def create(self, request, *args, **kwargs):
        """
        Create family and return full family data.

        Override to return FamilySerializer (with all fields) instead of
        FamilyCreateSerializer (which only has name).
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Use FamilySerializer to return full family data
        family = serializer.instance
        output_serializer = FamilySerializer(family)
        headers = self.get_success_headers(output_serializer.data)
        return Response(
            output_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        """
        Create family and automatically add creator as organizer.

        Sets:
        - created_by: current user
        - updated_by: current user

        Creates FamilyMember:
        - user: current user
        - role: ORGANIZER
        """
        family = serializer.save(
            created_by=self.request.user, updated_by=self.request.user
        )

        # Automatically add creator as organizer
        FamilyMember.objects.create(
            family=family, user=self.request.user, role=FamilyMember.Role.ORGANIZER
        )

    def perform_update(self, serializer):
        """
        Update family and set updated_by to current user.
        """
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        """
        Soft delete family by setting is_deleted=True and deleted_at.

        Does NOT hard delete from database (BaseModel soft delete pattern).
        """
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()

    def list(self, request, *args, **kwargs):
        """
        Override list to include member_count in response.

        The member_count annotation is added in get_queryset().
        We need to make sure the serializer includes it.
        """
        queryset = self.get_queryset()

        # Convert queryset to list to preserve annotations
        families_list = list(queryset)

        serializer = self.get_serializer(families_list, many=True)

        # Add member_count to each family in response
        data = serializer.data
        for i, family_data in enumerate(data):
            family_data["member_count"] = families_list[i].member_count

        return Response(data)
