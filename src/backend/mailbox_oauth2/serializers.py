"""
Serializers for the mailbox_oauth2 app.
"""

from django.contrib.auth import authenticate

from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login authentication.

    Validates the email and password fields required for user authentication.
    """

    email = serializers.EmailField(
        help_text="User's email address for authentication",
        required=True,
    )
    password = serializers.CharField(
        write_only=True,
        help_text="User's password for authentication",
        required=True,
    )

    def create(self, validated_data):
        """Do not allow creating instances from this serializer."""
        raise RuntimeError("LoginSerializer does not support create method")

    def update(self, instance, validated_data):
        """Do not allow updating instances from this serializer."""
        raise RuntimeError("LoginSerializer does not support update method")

    def validate(self, attrs):
        """
        Validate the email and password fields.
        """
        email = attrs.get("email")
        password = attrs.get("password")

        if not (email and password):
            raise serializers.ValidationError('Must include "email" and "password"')

        attrs["user"] = authenticate(
            self.context["request"], email=email, password=password
        )
        return attrs
