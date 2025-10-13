"""
Serializers for the invitations app
TDD approach - implementing to pass our API tests!
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.invitations.models import Invitation

User = get_user_model()


class UserSummarySerializer(serializers.ModelSerializer):
    """Lightweight user representation for nested serialization"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['public_id', 'email', 'first_name', 'last_name', 'full_name']
        read_only_fields = fields

    def get_full_name(self, obj):
        """Get user's full name"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email


class InvitationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating invitations"""

    invitation_url = serializers.SerializerMethodField(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    first_name = serializers.CharField(required=True, allow_blank=False)
    last_name = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = Invitation
        fields = [
            'public_id', 'first_name', 'last_name', 'full_name', 'email', 'role', 'organization_name',
            'message', 'status', 'invitation_url', 'created_at'
        ]
        read_only_fields = ['public_id', 'status', 'created_at', 'full_name']

    def validate_email(self, value):
        """Check that the email is not already registered"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email is already registered."
            )
        return value

    def get_invitation_url(self, obj):
        """Generate the invitation URL"""
        request = self.context.get('request')
        if request:
            # In production, this would be your frontend URL
            base_url = request.build_absolute_uri('/').rstrip('/')
            return f"{base_url}/invitations/accept?token={obj.token}"
        return None

    def create(self, validated_data):
        """Create invitation with the current user as inviter"""
        validated_data['invited_by'] = self.context['request'].user
        return super().create(validated_data)


class InvitationListSerializer(serializers.ModelSerializer):
    """Serializer for listing invitations"""

    invited_by = UserSummarySerializer(read_only=True)
    accepted_by = UserSummarySerializer(read_only=True, allow_null=True)
    is_expired = serializers.SerializerMethodField()
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = Invitation
        fields = [
            'public_id', 'first_name', 'last_name', 'full_name', 'email', 'role', 'organization_name',
            'status', 'invited_by', 'accepted_by',
            'created_at', 'expires_at', 'is_expired',
            'message', 'accepted_at'
        ]
        read_only_fields = fields

    def get_is_expired(self, obj):
        """Check if invitation is expired"""
        return obj.is_expired


class InvitationAcceptSerializer(serializers.Serializer):
    """Serializer for accepting an invitation"""

    token = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    def validate_token(self, value):
        """Validate the invitation token"""
        try:
            invitation = Invitation.objects.get(token=value)
        except Invitation.DoesNotExist:
            raise serializers.ValidationError("Invalid invitation token.")

        if invitation.is_expired:
            raise serializers.ValidationError("This invitation has expired.")

        if invitation.status != 'pending':
            raise serializers.ValidationError("This invitation has already been used.")

        self.invitation = invitation
        return value

    def validate_password(self, value):
        """Validate password strength"""
        validate_password(value)
        return value

    def save(self):
        """Create the user and accept the invitation"""
        # Create the new user
        user = User.objects.create_user(
            email=self.invitation.email,
            password=self.validated_data['password'],
            first_name=self.validated_data.get('first_name', ''),
            last_name=self.validated_data.get('last_name', ''),
            email_verified=True  # Invitation counts as email verification
        )

        # Accept the invitation
        self.invitation.accept(user)

        return user, self.invitation


class InvitationVerifySerializer(serializers.ModelSerializer):
    """Serializer for verifying an invitation token"""

    invited_by = UserSummarySerializer(read_only=True)
    is_expired = serializers.SerializerMethodField()
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = Invitation
        fields = [
            'public_id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'organization_name',
            'role',
            'status',
            'is_expired',
            'expires_at',
            'invited_by',
            'message',
            'created_at'
        ]
        read_only_fields = fields

    def get_is_expired(self, obj):
        """Check if invitation is expired"""
        return obj.is_expired
