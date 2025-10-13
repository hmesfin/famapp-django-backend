"""
DRF Serializers for FamApp.

Following TDD methodology and DRF best practices:
- Separate serializers for create, update, read, and detail operations
- Validation at the serializer level
- Clean separation of concerns

Ham Dog & TC bringing data validation to life! 🚀
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.shared.models import Family
from apps.shared.models import FamilyMember
from apps.shared.models import GroceryItem
from apps.shared.models import Pet
from apps.shared.models import PetActivity
from apps.shared.models import ScheduleEvent
from apps.shared.models import Todo

User = get_user_model()


# ============================================================================
# User Serializers (for nested relationships)
# ============================================================================


class UserSerializer(serializers.ModelSerializer):
    """
    Basic user serializer for nested relationships.

    Only exposes safe, public information about users.
    """

    class Meta:
        model = User
        fields = ["id", "public_id", "email", "first_name", "last_name"]
        read_only_fields = ["id", "public_id", "email", "first_name", "last_name"]


# ============================================================================
# Family Serializers
# ============================================================================


class FamilyCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new family.

    Validates:
    - name: required, 1-100 characters
    """

    class Meta:
        model = Family
        fields = ["name"]

    def validate_name(self, value):
        """Validate that name is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")
        return value


class FamilyUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing family.

    All fields are optional (partial updates allowed).
    """

    name = serializers.CharField(max_length=100, required=False, allow_blank=False)

    class Meta:
        model = Family
        fields = ["name"]

    def validate_name(self, value):
        """Validate that name is not empty if provided."""
        if value is not None and (not value or not value.strip()):
            raise serializers.ValidationError("Name cannot be empty.")
        return value


class FamilySerializer(serializers.ModelSerializer):
    """
    Read serializer for Family objects.

    Includes all essential fields with proper read-only settings.
    """

    class Meta:
        model = Family
        fields = [
            "id",
            "public_id",
            "name",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = [
            "id",
            "public_id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]


class MemberSerializer(serializers.ModelSerializer):
    """
    Serializer for FamilyMember (for nested use in FamilyDetailSerializer).

    Includes user information and role.
    """

    user = UserSerializer(read_only=True)

    class Meta:
        model = FamilyMember
        fields = ["id", "public_id", "user", "role", "created_at"]
        read_only_fields = ["id", "public_id", "user", "role", "created_at"]


class FamilyDetailSerializer(FamilySerializer):
    """
    Detailed serializer for Family with nested members.

    Extends FamilySerializer to include full member list with roles and user info.
    """

    members = MemberSerializer(many=True, read_only=True, source="familymember_set")

    class Meta(FamilySerializer.Meta):
        fields = FamilySerializer.Meta.fields + ["members"]
        read_only_fields = FamilySerializer.Meta.read_only_fields


# ============================================================================
# FamilyMember Serializers
# ============================================================================


class InviteMemberSerializer(serializers.Serializer):
    """
    Serializer for inviting a member to a family by email.

    Validates email format and checks if user exists.
    """

    email = serializers.EmailField(required=True)
    role = serializers.ChoiceField(
        choices=FamilyMember.Role.choices, default=FamilyMember.Role.PARENT
    )

    def validate_email(self, value):
        """Validate that user exists."""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(f"No user found with email: {value}")
        return value


class UpdateMemberRoleSerializer(serializers.Serializer):
    """
    Serializer for updating a family member's role.

    Validates role enum value.
    """

    role = serializers.ChoiceField(choices=FamilyMember.Role.choices, required=True)


# ============================================================================
# Todo Serializers
# ============================================================================


class TodoCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new todo.

    Accepts family_public_id and converts to family object.

    Validates:
    - title: required, 1-200 characters
    - due_date: must be in the future (if provided)
    - family_public_id: must be a valid family where user is a member
    """

    family_public_id = serializers.UUIDField(write_only=True)
    assigned_to_public_id = serializers.UUIDField(
        write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Todo
        fields = [
            "family_public_id",
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "assigned_to_public_id",
        ]

    def validate_title(self, value):
        """Validate that title is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_due_date(self, value):
        """Validate that due_date is in the future."""
        if value:
            from django.utils import timezone

            if value < timezone.now():
                raise serializers.ValidationError("Due date must be in the future.")
        return value

    def validate_family_public_id(self, value):
        """Validate that family exists and user is a member."""
        from apps.shared.models import Family, FamilyMember

        try:
            family = Family.objects.get(public_id=value, is_deleted=False)
        except Family.DoesNotExist:
            raise serializers.ValidationError("Family not found.")

        # Check if user is a member of the family
        request = self.context.get("request")
        if request and request.user:
            if not FamilyMember.objects.filter(
                family=family, user=request.user
            ).exists():
                raise serializers.ValidationError(
                    "You must be a member of this family to create todos."
                )

        return value

    def validate_assigned_to_public_id(self, value):
        """Validate that assigned_to user exists."""
        if value:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            try:
                User.objects.get(public_id=value)
            except User.DoesNotExist:
                raise serializers.ValidationError("Assigned user not found.")
        return value

    def create(self, validated_data):
        """Create todo and convert public_ids to actual objects."""
        from apps.shared.models import Family

        # Extract public_ids
        family_public_id = validated_data.pop("family_public_id")
        assigned_to_public_id = validated_data.pop("assigned_to_public_id", None)

        # Get family object
        family = Family.objects.get(public_id=family_public_id)
        validated_data["family"] = family

        # Get assigned_to user if provided
        if assigned_to_public_id:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            assigned_to = User.objects.get(public_id=assigned_to_public_id)
            validated_data["assigned_to"] = assigned_to

        return super().create(validated_data)


class TodoUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing todo.

    All fields are optional (partial updates allowed).
    """

    title = serializers.CharField(max_length=200, required=False, allow_blank=False)

    class Meta:
        model = Todo
        fields = [
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "assigned_to",
        ]

    def validate_title(self, value):
        """Validate that title is not empty if provided."""
        if value is not None and (not value or not value.strip()):
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_due_date(self, value):
        """Validate that due_date is in the future if provided."""
        if value:
            from django.utils import timezone

            if value < timezone.now():
                raise serializers.ValidationError("Due date must be in the future.")
        return value


class TodoSerializer(serializers.ModelSerializer):
    """
    Read serializer for Todo objects.

    Includes computed fields like is_overdue.
    """

    is_overdue = serializers.SerializerMethodField()
    assigned_to = UserSerializer(read_only=True)

    class Meta:
        model = Todo
        fields = [
            "id",
            "public_id",
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "assigned_to",
            "is_overdue",
            "created_at",
            "updated_at",
            "created_by",
        ]
        read_only_fields = [
            "id",
            "public_id",
            "is_overdue",
            "created_at",
            "updated_at",
            "created_by",
        ]

    def get_is_overdue(self, obj):
        """Calculate if todo is overdue."""
        if not obj.due_date or obj.status == Todo.Status.DONE:
            return False

        from django.utils import timezone

        return obj.due_date < timezone.now()


class TodoToggleSerializer(serializers.Serializer):
    """
    Serializer for toggling todo completion status.

    This is an action-based serializer with no fields.
    The toggle logic is handled in the view.
    """

    pass


# ============================================================================
# Schedule Serializers
# ============================================================================


class EventCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new schedule event.

    Accepts family_public_id and converts to family object.

    Validates:
    - title: required
    - start_time: required
    - end_time: required, must be after start_time
    - family_public_id: must be a valid family where user is a member
    """

    family_public_id = serializers.UUIDField(write_only=True)
    assigned_to_public_id = serializers.UUIDField(
        write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = ScheduleEvent
        fields = [
            "family_public_id",
            "title",
            "description",
            "event_type",
            "start_time",
            "end_time",
            "location",
            "assigned_to_public_id",
        ]

    def validate_family_public_id(self, value):
        """Validate that family exists and user is a member."""
        try:
            family = Family.objects.get(public_id=value, is_deleted=False)
        except Family.DoesNotExist:
            raise serializers.ValidationError("Family not found.")

        # Check if user is a member of the family
        request = self.context.get("request")
        if request and request.user:
            if not FamilyMember.objects.filter(
                family=family, user=request.user
            ).exists():
                raise serializers.ValidationError(
                    "You must be a member of this family to create events."
                )

        return value

    def validate_assigned_to_public_id(self, value):
        """Validate that assigned_to user exists."""
        if value:
            try:
                User.objects.get(public_id=value)
            except User.DoesNotExist:
                raise serializers.ValidationError("Assigned user not found.")
        return value

    def validate(self, data):
        """Validate that end_time is after start_time."""
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError(
                {"end_time": "End time must be after start time."}
            )

        return data

    def create(self, validated_data):
        """Create event and convert public_ids to actual objects."""
        # Extract public_ids
        family_public_id = validated_data.pop("family_public_id")
        assigned_to_public_id = validated_data.pop("assigned_to_public_id", None)

        # Get family object
        family = Family.objects.get(public_id=family_public_id)
        validated_data["family"] = family

        # Get assigned_to user if provided
        if assigned_to_public_id:
            assigned_to = User.objects.get(public_id=assigned_to_public_id)
            validated_data["assigned_to"] = assigned_to

        return super().create(validated_data)


class EventUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing event.

    All fields are optional (partial updates allowed).
    """

    class Meta:
        model = ScheduleEvent
        fields = [
            "title",
            "description",
            "event_type",
            "start_time",
            "end_time",
            "location",
            "assigned_to",
        ]

    def validate(self, data):
        """Validate that end_time is after start_time if both provided."""
        start_time = data.get("start_time") or (
            self.instance.start_time if self.instance else None
        )
        end_time = data.get("end_time") or (
            self.instance.end_time if self.instance else None
        )

        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError(
                {"end_time": "End time must be after start time."}
            )

        return data


class EventSerializer(serializers.ModelSerializer):
    """
    Read serializer for ScheduleEvent objects.

    Includes computed duration field.
    """

    duration = serializers.SerializerMethodField()
    assigned_to = UserSerializer(read_only=True)

    class Meta:
        model = ScheduleEvent
        fields = [
            "id",
            "public_id",
            "title",
            "description",
            "event_type",
            "start_time",
            "end_time",
            "location",
            "assigned_to",
            "duration",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "public_id",
            "duration",
            "created_at",
            "updated_at",
        ]

    def get_duration(self, obj):
        """Calculate event duration in minutes."""
        if obj.start_time and obj.end_time:
            delta = obj.end_time - obj.start_time
            return int(delta.total_seconds() / 60)
        return None


# ============================================================================
# Grocery Serializers
# ============================================================================


class GroceryCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new grocery item.

    Accepts family_public_id and converts to family object.

    Validates:
    - name: required, 1-200 characters
    - category: optional, must be valid enum
    - family_public_id: must be a valid family where user is a member
    """

    family_public_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = GroceryItem
        fields = ["family_public_id", "name", "quantity", "unit", "category"]

    def validate_name(self, value):
        """Validate that name is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")
        return value

    def validate_family_public_id(self, value):
        """Validate that family exists and user is a member."""
        try:
            family = Family.objects.get(public_id=value, is_deleted=False)
        except Family.DoesNotExist:
            raise serializers.ValidationError("Family not found.")

        # Check if user is a member of the family
        request = self.context.get("request")
        if request and request.user:
            if not FamilyMember.objects.filter(
                family=family, user=request.user
            ).exists():
                raise serializers.ValidationError(
                    "You must be a member of this family to create grocery items."
                )

        return value

    def create(self, validated_data):
        """Create grocery item and convert public_id to actual object."""
        # Extract family_public_id
        family_public_id = validated_data.pop("family_public_id")

        # Get family object
        family = Family.objects.get(public_id=family_public_id)
        validated_data["family"] = family

        return super().create(validated_data)


class GroceryUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing grocery item.

    All fields are optional (partial updates allowed).
    """

    class Meta:
        model = GroceryItem
        fields = ["name", "quantity", "unit", "category", "is_purchased"]

    def validate_name(self, value):
        """Validate that name is not empty if provided."""
        if value is not None and (not value or not value.strip()):
            raise serializers.ValidationError("Name cannot be empty.")
        return value


class GrocerySerializer(serializers.ModelSerializer):
    """
    Read serializer for GroceryItem objects.

    Includes purchaser information.
    """

    added_by = UserSerializer(read_only=True)

    class Meta:
        model = GroceryItem
        fields = [
            "id",
            "public_id",
            "name",
            "quantity",
            "unit",
            "category",
            "is_purchased",
            "added_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "public_id",
            "added_by",
            "created_at",
            "updated_at",
        ]


# ============================================================================
# Pet Serializers
# ============================================================================


class PetCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new pet.

    Validates:
    - name: required
    - species: required
    """

    class Meta:
        model = Pet
        fields = ["name", "species", "breed", "age", "notes"]

    def validate_name(self, value):
        """Validate that name is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")
        return value


class PetUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing pet.

    All fields are optional (partial updates allowed).
    """

    class Meta:
        model = Pet
        fields = ["name", "species", "breed", "age", "notes"]

    def validate_name(self, value):
        """Validate that name is not empty if provided."""
        if value is not None and (not value or not value.strip()):
            raise serializers.ValidationError("Name cannot be empty.")
        return value


class PetSerializer(serializers.ModelSerializer):
    """
    Read serializer for Pet objects.

    Includes last activity timestamps.
    """

    last_feeding = serializers.SerializerMethodField()
    last_walking = serializers.SerializerMethodField()

    class Meta:
        model = Pet
        fields = [
            "id",
            "public_id",
            "name",
            "species",
            "breed",
            "age",
            "notes",
            "last_feeding",
            "last_walking",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "public_id",
            "last_feeding",
            "last_walking",
            "created_at",
            "updated_at",
        ]

    def get_last_feeding(self, obj):
        """Get timestamp of last feeding activity."""
        last_activity = (
            PetActivity.objects.filter(
                pet=obj,
                activity_type=PetActivity.ActivityType.FEEDING,
                is_completed=True,
            )
            .order_by("-completed_at")
            .first()
        )
        return last_activity.completed_at if last_activity else None

    def get_last_walking(self, obj):
        """Get timestamp of last walking activity."""
        last_activity = (
            PetActivity.objects.filter(
                pet=obj,
                activity_type=PetActivity.ActivityType.WALKING,
                is_completed=True,
            )
            .order_by("-completed_at")
            .first()
        )
        return last_activity.completed_at if last_activity else None


class PetActivityCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/logging a new pet activity.

    Validates:
    - activity_type: required, must be valid enum
    - scheduled_time: required
    """

    class Meta:
        model = PetActivity
        fields = ["activity_type", "scheduled_time", "notes"]


class PetActivitySerializer(serializers.ModelSerializer):
    """
    Read serializer for PetActivity objects.

    Includes logger information.
    """

    completed_by = UserSerializer(read_only=True)

    class Meta:
        model = PetActivity
        fields = [
            "id",
            "public_id",
            "activity_type",
            "scheduled_time",
            "notes",
            "is_completed",
            "completed_at",
            "completed_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "public_id",
            "is_completed",
            "completed_at",
            "completed_by",
            "created_at",
            "updated_at",
        ]
