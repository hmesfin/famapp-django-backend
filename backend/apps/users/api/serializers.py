from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.shared.models import FamilyMember
from apps.users.models import Invitation
from apps.users.models import User


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["id", "public_id", "first_name", "last_name", "email", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "public_id"},
        }


class UserCreateSerializer(serializers.ModelSerializer[User]):
    """
    Serializer for user registration.

    Phase G: Supports optional invitation_token for signup with invitation flow.
    """

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )
    invitation_token = serializers.UUIDField(
        required=False,
        allow_null=True,
        write_only=True,
        help_text="Optional invitation token to join family during signup (Phase G)",
    )

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
            "invitation_token",
        ]

    def validate_invitation_token(self, value):
        """
        Validate invitation token if provided (Phase G).

        Validates:
        - Token exists and is valid
        - Invitation is PENDING
        - Invitation has not expired
        - Email matches invitee_email (case-insensitive)
        """
        if value is None:
            return None

        try:
            invitation = Invitation.objects.select_related("family").get(
                token=value,
                status=Invitation.Status.PENDING,
            )
        except Invitation.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired invitation token")

        # Check not expired
        if invitation.is_expired:
            raise serializers.ValidationError("This invitation has expired")

        # Check email matches (case-insensitive) - need to get email from initial_data
        request_email = self.initial_data.get("email", "").lower()
        if invitation.invitee_email.lower() != request_email:
            raise serializers.ValidationError(
                f"This invitation is for {invitation.invitee_email}. "
                f"Please use that email address to sign up.",
            )

        # Store invitation in context for later use
        self.context["invitation"] = invitation
        return value

    def validate(self, attrs):
        """
        Validate that password and password_confirm match.
        """
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        """
        Create user with validated data.
        """
        # Remove password_confirm as it's not a model field
        validated_data.pop("password_confirm", None)

        # Create user with password hashing
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user


# ============================================================================
# Invitation Serializers (Enhancement 3)
# ============================================================================


class InvitationCreateSerializer(serializers.Serializer):
    """
    Serializer for creating family invitations.

    Only accepts PARENT or CHILD roles (ORGANIZER is excluded for security).
    Validates that invitee is not already a family member and no pending
    invitation exists for the same email.
    """

    invitee_email = serializers.EmailField(
        required=True,
        help_text="Email address of the person being invited",
    )
    role = serializers.ChoiceField(
        choices=["parent", "child"],
        required=True,
        help_text="Role to be assigned (PARENT or CHILD only)",
    )

    def validate_invitee_email(self, value):
        """
        Validate that invitee is not already a family member.
        """
        family = self.context.get("family")
        if not family:
            return value

        # Check if user with this email is already a member
        existing_member = FamilyMember.objects.filter(
            family=family,
            user__email=value,
        ).exists()

        if existing_member:
            raise serializers.ValidationError(
                f"A user with email {value} is already a member of this family.",
            )

        return value

    def validate(self, attrs):
        """
        Validate that no pending invitation exists for this email.
        """
        family = self.context.get("family")
        if not family:
            return attrs

        invitee_email = attrs.get("invitee_email")

        # Check for existing pending invitation
        pending_invitation = Invitation.objects.filter(
            family=family,
            invitee_email=invitee_email,
            status=Invitation.Status.PENDING,
        ).exists()

        if pending_invitation:
            raise serializers.ValidationError(
                {
                    "invitee_email": f"A pending invitation already exists for {invitee_email}.",
                },
            )

        return attrs


class InviterSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for inviter details (no hyperlinked field).
    Used as nested serializer in InvitationSerializer.
    """

    class Meta:
        model = User
        fields = ["id", "public_id", "email", "first_name", "last_name"]
        read_only_fields = fields


class InvitationSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for invitation details.

    Includes inviter details, family name, and computed is_expired field.
    """

    inviter = InviterSerializer(read_only=True)
    family_name = serializers.CharField(source="family.name", read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = Invitation
        fields = [
            "id",
            "public_id",
            "token",
            "inviter",
            "invitee_email",
            "family_name",
            "role",
            "status",
            "expires_at",
            "is_expired",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_is_expired(self, obj):
        """
        Compute is_expired status from model property.
        """
        return obj.is_expired
