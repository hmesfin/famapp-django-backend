from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

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
    """
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password", "password_confirm"]

    def validate(self, attrs):
        """
        Validate that password and password_confirm match.
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        """
        Create user with validated data.
        """
        # Remove password_confirm as it's not a model field
        validated_data.pop('password_confirm', None)
        
        # Create user with password hashing
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user
