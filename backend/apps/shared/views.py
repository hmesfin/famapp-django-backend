"""
DRF ViewSets for FamApp API endpoints.

Following TDD methodology and DRF best practices:
- Token authentication (drf-simplejwt)
- Permission-based authorization (IsFamilyMember, IsFamilyAdmin)
- Soft deletes for all models
- public_id (UUID) in URLs, NOT integer id

Ham Dog & TC building family collaboration APIs! 🚀
"""

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.shared.mixins import FamilyAccessMixin
from apps.shared.models import Family
from apps.shared.models import FamilyMember
from apps.shared.models import GroceryItem
from apps.shared.models import Pet
from apps.shared.models import PetActivity
from apps.shared.models import ScheduleEvent
from apps.shared.models import Todo
from apps.shared.permissions import IsFamilyAdmin
from apps.shared.permissions import IsFamilyMember
from apps.shared.serializers import EventCreateSerializer
from apps.shared.serializers import EventSerializer
from apps.shared.serializers import EventUpdateSerializer
from apps.shared.serializers import FamilyCreateSerializer
from apps.shared.serializers import FamilyDetailSerializer
from apps.shared.serializers import FamilySerializer
from apps.shared.serializers import FamilyUpdateSerializer
from apps.shared.serializers import GroceryCreateSerializer
from apps.shared.serializers import GrocerySerializer
from apps.shared.serializers import GroceryUpdateSerializer
from apps.shared.serializers import InviteMemberSerializer
from apps.shared.serializers import MemberSerializer
from apps.shared.serializers import PetActivityCreateSerializer
from apps.shared.serializers import PetActivitySerializer
from apps.shared.serializers import PetCreateSerializer
from apps.shared.serializers import PetSerializer
from apps.shared.serializers import PetUpdateSerializer
from apps.shared.serializers import TodoCreateSerializer
from apps.shared.serializers import TodoSerializer
from apps.shared.serializers import TodoUpdateSerializer
from apps.shared.serializers import UpdateMemberRoleSerializer

User = get_user_model()


@extend_schema_view(
    list=extend_schema(tags=["Families"]),
    create=extend_schema(tags=["Families"]),
    retrieve=extend_schema(tags=["Families"]),
    update=extend_schema(tags=["Families"]),
    partial_update=extend_schema(tags=["Families"]),
    destroy=extend_schema(tags=["Families"]),
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

    # Swagger/OpenAPI schema tag
    tags = ["Families"]

    def get_permissions(self):
        """
        Set permissions based on action.

        - create/list: IsAuthenticated only
        - retrieve: IsFamilyMember (view-level check)
        - update/partial_update/destroy: IsFamilyAdmin (organizers only)
        """
        if self.action == "create" or self.action in ["list"]:
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
        - members/member_detail: Don't filter by membership (permission checked in action)
        - Exclude soft-deleted families
        """
        user = self.request.user

        if self.action == "list":
            # Annotate with member count for list view
            # First get families where user is a member
            # Then annotate with member count (separate from the filter)
            user_family_ids = FamilyMember.objects.filter(user=user).values_list(
                "family_id", flat=True,
            )
            return (
                Family.objects.filter(id__in=user_family_ids, is_deleted=False)
                .annotate(member_count=Count("familymember"))
                .order_by("-created_at")
            )

        # For member management actions, don't filter by membership
        # (permission is checked manually in the action)
        if self.action in ["members", "member_detail"]:
            return Family.objects.filter(is_deleted=False)

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
        if self.action in ["update", "partial_update"]:
            return FamilyUpdateSerializer
        if self.action == "retrieve":
            return FamilyDetailSerializer
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
            output_serializer.data, status=status.HTTP_201_CREATED, headers=headers,
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
            created_by=self.request.user, updated_by=self.request.user,
        )

        # Automatically add creator as organizer
        FamilyMember.objects.create(
            family=family, user=self.request.user, role=FamilyMember.Role.ORGANIZER,
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

    # ========================================================================
    # Family Member Management Actions
    # ========================================================================

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="members",
    )
    def members(self, request, public_id=None):
        """
        GET /api/v1/families/{public_id}/members/ - List members (any member)
        POST /api/v1/families/{public_id}/members/ - Invite member (organizers only)

        Handles both listing and inviting members on the same endpoint.
        """
        family = self.get_object()

        if request.method == "GET":
            # List members - any family member can view
            # Check permission manually
            if not FamilyMember.objects.filter(
                family=family, user=request.user,
            ).exists():
                return Response(
                    {"detail": "You must be a family member to access this resource."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            members = FamilyMember.objects.filter(family=family).select_related("user")
            serializer = MemberSerializer(members, many=True)
            return Response(serializer.data)

        if request.method == "POST":
            # Invite member - organizers only
            # Check permission manually
            if not FamilyMember.objects.filter(
                family=family, user=request.user, role=FamilyMember.Role.ORGANIZER,
            ).exists():
                return Response(
                    {
                        "detail": "You must be a family organizer to perform this action.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = InviteMemberSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data["email"]
            role = serializer.validated_data.get("role", FamilyMember.Role.PARENT)

            # Get user by email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {"email": f"No user found with email: {email}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if user already a member
            if FamilyMember.objects.filter(family=family, user=user).exists():
                return Response(
                    {"detail": "User is already a member of this family."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create membership
            membership = FamilyMember.objects.create(
                family=family, user=user, role=role,
            )

            # Return member data
            output_serializer = MemberSerializer(membership)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["patch", "delete"],
        url_path="members/(?P<user_public_id>[^/.]+)",
    )
    def member_detail(self, request, public_id=None, user_public_id=None):
        """
        PATCH /api/v1/families/{public_id}/members/{user_public_id}/ - Update role
        DELETE /api/v1/families/{public_id}/members/{user_public_id}/ - Remove member

        Handles both updating and removing individual members.
        """
        family = self.get_object()

        # Get user by public_id
        user = get_object_or_404(User, public_id=user_public_id)

        # Get membership
        membership = get_object_or_404(FamilyMember, family=family, user=user)

        if request.method == "PATCH":
            # Update member role - organizers only
            if not FamilyMember.objects.filter(
                family=family, user=request.user, role=FamilyMember.Role.ORGANIZER,
            ).exists():
                return Response(
                    {
                        "detail": "You must be a family organizer to perform this action.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = UpdateMemberRoleSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            membership.role = serializer.validated_data["role"]
            membership.save()

            # Return updated member data
            output_serializer = MemberSerializer(membership)
            return Response(output_serializer.data)

        if request.method == "DELETE":
            # Remove member
            # Allow if: (1) user is organizer OR (2) user is removing themselves
            is_organizer = FamilyMember.objects.filter(
                family=family, user=request.user, role=FamilyMember.Role.ORGANIZER,
            ).exists()
            is_self_removal = user == request.user

            if not (is_organizer or is_self_removal):
                return Response(
                    {"detail": "You do not have permission to remove this member."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Delete membership
            membership.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

    # ========================================================================
    # Family Invitation Management Actions (Enhancement 3)
    # ========================================================================

    @action(
        detail=True,
        methods=["post", "get"],
        url_path="invitations",
    )
    def invitations(self, request, public_id=None):
        """
        POST /api/v1/families/{public_id}/invitations/ - Create invitation (organizers only)
        GET /api/v1/families/{public_id}/invitations/ - List invitations (organizers only)

        Handles both creating and listing invitations on the same endpoint.
        """
        from apps.users.api.serializers import InvitationCreateSerializer, InvitationSerializer
        from apps.users.models import Invitation
        from apps.users.tasks import send_invitation_email

        family = self.get_object()

        # Check permission: only ORGANIZER can manage invitations
        if not FamilyMember.objects.filter(
            family=family, user=request.user, role=FamilyMember.Role.ORGANIZER
        ).exists():
            return Response(
                {"detail": "You must be a family organizer to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.method == "POST":
            # Create invitation
            serializer = InvitationCreateSerializer(
                data=request.data, context={"family": family}
            )
            serializer.is_valid(raise_exception=True)

            # Create invitation
            invitation = Invitation.objects.create(
                inviter=request.user,
                invitee_email=serializer.validated_data["invitee_email"],
                family=family,
                role=serializer.validated_data["role"],
                created_by=request.user,
                updated_by=request.user,
            )

            # Trigger Celery email task
            send_invitation_email.delay(invitation.id)

            # Return invitation data
            output_serializer = InvitationSerializer(invitation)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "GET":
            # List invitations
            queryset = Invitation.objects.filter(family=family, is_deleted=False).order_by(
                "-created_at"
            )

            # Filter by status if provided
            status_filter = request.query_params.get("status")
            if status_filter:
                queryset = queryset.filter(status=status_filter.lower())

            serializer = InvitationSerializer(queryset, many=True)
            return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(tags=["Todos"]),
    create=extend_schema(tags=["Todos"]),
    retrieve=extend_schema(tags=["Todos"]),
    update=extend_schema(tags=["Todos"]),
    partial_update=extend_schema(tags=["Todos"]),
    destroy=extend_schema(tags=["Todos"]),
)
class TodoViewSet(FamilyAccessMixin, viewsets.ModelViewSet):
    """
    ViewSet for Todo CRUD operations.

    Uses FamilyAccessMixin to automatically filter todos by family membership!

    Endpoints:
    - GET /api/v1/todos/ - List todos (user's families only)
    - POST /api/v1/todos/ - Create todo
    - GET /api/v1/todos/{public_id}/ - Retrieve todo details
    - PATCH /api/v1/todos/{public_id}/ - Update todo
    - PATCH /api/v1/todos/{public_id}/toggle/ - Toggle completion status
    - DELETE /api/v1/todos/{public_id}/ - Soft delete todo

    CRITICAL: All URLs use public_id (UUID), NOT integer id!
    """

    queryset = Todo.objects.all()  # Mixin filters this automatically!
    lookup_field = "public_id"
    lookup_url_kwarg = "public_id"
    permission_classes = [IsAuthenticated]

    # Swagger/OpenAPI schema tag
    tags = ["Todos"]

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.

        - create: TodoCreateSerializer (with family_public_id)
        - update/partial_update: TodoUpdateSerializer (all optional)
        - retrieve/list: TodoSerializer (includes computed fields)
        """
        if self.action == "create":
            return TodoCreateSerializer
        if self.action in ["update", "partial_update"]:
            return TodoUpdateSerializer
        return TodoSerializer

    def create(self, request, *args, **kwargs):
        """
        Create todo and return full todo data.

        Override to return TodoSerializer (with all fields) instead of
        TodoCreateSerializer (which only has input fields).
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Use TodoSerializer to return full todo data
        todo = serializer.instance
        output_serializer = TodoSerializer(todo)
        headers = self.get_success_headers(output_serializer.data)
        return Response(
            output_serializer.data, status=status.HTTP_201_CREATED, headers=headers,
        )

    def perform_create(self, serializer):
        """
        Create todo and set created_by/updated_by to current user.

        The serializer handles family lookup via family_public_id.
        """
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        """
        Update todo and set updated_by to current user.
        """
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        """
        Soft delete todo by setting is_deleted=True and deleted_at.

        Does NOT hard delete from database (BaseModel soft delete pattern).
        """
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()

    @action(detail=True, methods=["patch"], url_path="toggle")
    def toggle(self, request, public_id=None):
        """
        PATCH /api/v1/todos/{public_id}/toggle/ - Toggle completion status.

        Toggles between TODO and DONE status.
        """
        todo = self.get_object()

        # Toggle status
        if todo.status == Todo.Status.DONE:
            todo.status = Todo.Status.TODO
        else:
            todo.status = Todo.Status.DONE

        todo.updated_by = request.user
        todo.save()

        # Return updated todo
        serializer = self.get_serializer(todo)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(tags=["Events"]),
    create=extend_schema(tags=["Events"]),
    retrieve=extend_schema(tags=["Events"]),
    update=extend_schema(tags=["Events"]),
    partial_update=extend_schema(tags=["Events"]),
    destroy=extend_schema(tags=["Events"]),
)
class ScheduleEventViewSet(FamilyAccessMixin, viewsets.ModelViewSet):
    """
    ViewSet for ScheduleEvent CRUD operations.

    Uses FamilyAccessMixin to automatically filter events by family membership!

    Endpoints:
    - GET /api/v1/events/ - List events (user's families only)
    - POST /api/v1/events/ - Create event
    - GET /api/v1/events/{public_id}/ - Retrieve event details
    - PATCH /api/v1/events/{public_id}/ - Update event
    - DELETE /api/v1/events/{public_id}/ - Soft delete event

    CRITICAL: All URLs use public_id (UUID), NOT integer id!
    """

    queryset = ScheduleEvent.objects.all()  # Mixin filters this automatically!
    lookup_field = "public_id"
    lookup_url_kwarg = "public_id"
    permission_classes = [IsAuthenticated]

    # Swagger/OpenAPI schema tag
    tags = ["Events"]

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.

        - create: EventCreateSerializer (with family_public_id)
        - update/partial_update: EventUpdateSerializer (all optional)
        - retrieve/list: EventSerializer (includes computed fields)
        """
        if self.action == "create":
            return EventCreateSerializer
        if self.action in ["update", "partial_update"]:
            return EventUpdateSerializer
        return EventSerializer

    def create(self, request, *args, **kwargs):
        """
        Create event and return full event data.

        Override to return EventSerializer (with all fields) instead of
        EventCreateSerializer (which only has input fields).
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Use EventSerializer to return full event data
        event = serializer.instance
        output_serializer = EventSerializer(event)
        headers = self.get_success_headers(output_serializer.data)
        return Response(
            output_serializer.data, status=status.HTTP_201_CREATED, headers=headers,
        )

    def perform_create(self, serializer):
        """
        Create event and set created_by/updated_by to current user.

        The serializer handles family lookup via family_public_id.
        """
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        """
        Update event and set updated_by to current user.
        """
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        """
        Soft delete event by setting is_deleted=True and deleted_at.

        Does NOT hard delete from database (BaseModel soft delete pattern).
        """
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()


@extend_schema_view(
    list=extend_schema(tags=["Groceries"]),
    create=extend_schema(tags=["Groceries"]),
    retrieve=extend_schema(tags=["Groceries"]),
    update=extend_schema(tags=["Groceries"]),
    partial_update=extend_schema(tags=["Groceries"]),
    destroy=extend_schema(tags=["Groceries"]),
)
class GroceryItemViewSet(FamilyAccessMixin, viewsets.ModelViewSet):
    """
    ViewSet for GroceryItem CRUD operations.

    Uses FamilyAccessMixin to automatically filter grocery items by family membership!

    Endpoints:
    - GET /api/v1/groceries/ - List grocery items (user's families only)
    - POST /api/v1/groceries/ - Create grocery item
    - GET /api/v1/groceries/{public_id}/ - Retrieve grocery item details
    - PATCH /api/v1/groceries/{public_id}/ - Update grocery item
    - PATCH /api/v1/groceries/{public_id}/toggle/ - Toggle purchased status
    - DELETE /api/v1/groceries/{public_id}/ - Soft delete grocery item

    CRITICAL: All URLs use public_id (UUID), NOT integer id!
    """

    queryset = GroceryItem.objects.all()  # Mixin filters this automatically!
    lookup_field = "public_id"
    lookup_url_kwarg = "public_id"
    permission_classes = [IsAuthenticated]

    # Swagger/OpenAPI schema tag
    tags = ["Groceries"]

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.

        - create: GroceryCreateSerializer (with family_public_id)
        - update/partial_update: GroceryUpdateSerializer (all optional)
        - retrieve/list: GrocerySerializer (includes added_by)
        """
        if self.action == "create":
            return GroceryCreateSerializer
        if self.action in ["update", "partial_update"]:
            return GroceryUpdateSerializer
        return GrocerySerializer

    def create(self, request, *args, **kwargs):
        """
        Create grocery item and return full item data.

        Override to return GrocerySerializer (with all fields) instead of
        GroceryCreateSerializer (which only has input fields).
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Use GrocerySerializer to return full item data
        item = serializer.instance
        output_serializer = GrocerySerializer(item)
        headers = self.get_success_headers(output_serializer.data)
        return Response(
            output_serializer.data, status=status.HTTP_201_CREATED, headers=headers,
        )

    def perform_create(self, serializer):
        """
        Create grocery item and set added_by to current user.

        The serializer handles family lookup via family_public_id.
        """
        serializer.save(added_by=self.request.user)

    def perform_destroy(self, instance):
        """
        Soft delete grocery item by setting is_deleted=True and deleted_at.

        Does NOT hard delete from database (BaseModel soft delete pattern).
        """
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()

    @action(detail=True, methods=["patch"], url_path="toggle")
    def toggle(self, request, public_id=None):
        """
        PATCH /api/v1/groceries/{public_id}/toggle/ - Toggle purchased status.

        Toggles is_purchased between True and False.
        """
        item = self.get_object()

        # Toggle is_purchased
        item.is_purchased = not item.is_purchased
        item.save()

        # Return updated item
        serializer = self.get_serializer(item)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(tags=["Pets"]),
    create=extend_schema(tags=["Pets"]),
    retrieve=extend_schema(tags=["Pets"]),
    update=extend_schema(tags=["Pets"]),
    partial_update=extend_schema(tags=["Pets"]),
    destroy=extend_schema(tags=["Pets"]),
)
class PetViewSet(FamilyAccessMixin, viewsets.ModelViewSet):
    """
    ViewSet for Pet CRUD operations and PetActivity logging.

    Uses FamilyAccessMixin to automatically filter pets by family membership!

    Endpoints:
    - GET /api/v1/pets/ - List pets (user's families only)
    - POST /api/v1/pets/ - Create pet
    - GET /api/v1/pets/{public_id}/ - Retrieve pet details
    - PATCH /api/v1/pets/{public_id}/ - Update pet
    - DELETE /api/v1/pets/{public_id}/ - Soft delete pet
    - POST /api/v1/pets/{public_id}/activities/ - Log pet activity
    - GET /api/v1/pets/{public_id}/activities/ - List pet activities

    CRITICAL: All URLs use public_id (UUID), NOT integer id!
    """

    queryset = Pet.objects.all()  # Mixin filters this automatically!
    lookup_field = "public_id"
    lookup_url_kwarg = "public_id"
    permission_classes = [IsAuthenticated]

    # Swagger/OpenAPI schema tag
    tags = ["Pets"]

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.

        - create: PetCreateSerializer (with family_public_id)
        - update/partial_update: PetUpdateSerializer (all optional)
        - retrieve/list: PetSerializer (includes last activity timestamps)
        - activities (POST): PetActivityCreateSerializer
        - activities (GET): PetActivitySerializer
        """
        if self.action == "create":
            return PetCreateSerializer
        if self.action in ["update", "partial_update"]:
            return PetUpdateSerializer
        if self.action == "activities" and self.request.method == "POST":
            return PetActivityCreateSerializer
        if self.action == "activities" and self.request.method == "GET":
            return PetActivitySerializer
        return PetSerializer

    def create(self, request, *args, **kwargs):
        """
        Create pet and return full pet data.

        Override to return PetSerializer (with all fields) instead of
        PetCreateSerializer (which only has input fields).
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Use PetSerializer to return full pet data
        pet = serializer.instance
        output_serializer = PetSerializer(pet)
        headers = self.get_success_headers(output_serializer.data)
        return Response(
            output_serializer.data, status=status.HTTP_201_CREATED, headers=headers,
        )

    def perform_create(self, serializer):
        """
        Create pet and set created_by/updated_by to current user.

        The serializer handles family lookup via family_public_id.
        """
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        """
        Update pet and set updated_by to current user.
        """
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        """
        Soft delete pet by setting is_deleted=True and deleted_at.

        Does NOT hard delete from database (BaseModel soft delete pattern).
        Cascade delete to PetActivity handled by Django on_delete=CASCADE.
        """
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()

    # ========================================================================
    # Pet Activity Management Actions
    # ========================================================================

    @action(
        detail=True,
        methods=["post", "get"],
        url_path="activities",
    )
    def activities(self, request, public_id=None):
        """
        POST /api/v1/pets/{public_id}/activities/ - Log pet activity
        GET /api/v1/pets/{public_id}/activities/ - List pet activities

        Handles both logging and listing pet activities on the same endpoint.
        """
        pet = self.get_object()

        if request.method == "POST":
            # Log activity
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Create activity linked to this pet
            activity = serializer.save(
                pet=pet, created_by=request.user, updated_by=request.user,
            )

            # If is_completed=True, set completed_by to current user
            if activity.is_completed and not activity.completed_by:
                activity.completed_by = request.user
                activity.save()

            # Return activity data
            output_serializer = PetActivitySerializer(activity)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "GET":
            # List activities
            queryset = PetActivity.objects.filter(pet=pet, is_deleted=False).order_by(
                "-scheduled_time",
            )

            # Filter by activity_type if provided
            activity_type = request.query_params.get("activity_type")
            if activity_type:
                # Convert to lowercase to match enum values
                queryset = queryset.filter(activity_type=activity_type.lower())

            # Limit results if provided
            limit = request.query_params.get("limit")
            if limit:
                try:
                    queryset = queryset[: int(limit)]
                except ValueError:
                    pass  # Ignore invalid limit

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
