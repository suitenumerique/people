"""Serializers for the token_exchange application."""

from django.conf import settings

from rest_framework import serializers


class TokenExchangeSerializer(serializers.Serializer):
    """
    Serializer for RFC 8693 token exchange requests.

    Validates the token exchange request parameters according to RFC 8693.
    """

    grant_type = serializers.CharField(required=True)
    subject_token = serializers.CharField(required=True)
    subject_token_type = serializers.CharField(required=True)

    requested_token_type = serializers.CharField(required=False, allow_blank=True)
    audience = serializers.CharField(required=False, allow_blank=True)
    scope = serializers.CharField(required=False, allow_blank=True)
    actor_token = serializers.CharField(required=False, allow_blank=True)
    actor_token_type = serializers.CharField(required=False, allow_blank=True)
    resource = serializers.CharField(required=False, allow_blank=True)
    expires_in = serializers.IntegerField(required=False, min_value=1)

    def validate_grant_type(self, value):
        """Validate that grant_type is the correct RFC 8693 value."""
        expected = "urn:ietf:params:oauth:grant-type:token-exchange"
        if value != expected:
            raise serializers.ValidationError(
                f"Invalid grant_type. Expected '{expected}', got '{value}'"
            )
        return value

    def validate_requested_token_type(self, value):
        """Validate that the requested token type is allowed."""
        if not value:
            return value

        allowed_types = settings.TOKEN_EXCHANGE_ALLOWED_TOKEN_TYPES

        # Map URN types to simple types
        urn_mapping = {
            "urn:ietf:params:oauth:token-type:access_token": "access_token",
            "urn:ietf:params:oauth:token-type:jwt": "jwt",
            "urn:ietf:params:oauth:token-type:refresh_token": "refresh_token",
        }

        # Check if it's a URN or simple type
        simple_type = urn_mapping.get(value, value)

        if simple_type == "refresh_token":
            raise serializers.ValidationError(
                "refresh_token type is not supported for token exchange"
            )

        if simple_type not in allowed_types:
            raise serializers.ValidationError(
                f"Token type '{value}' is not allowed. "
                f"Allowed types: {', '.join(allowed_types)}"
            )

        return simple_type

    def validate_expires_in(self, value):
        """Validate that expires_in is within acceptable bounds."""
        if value is None:
            return value

        max_expires_in = settings.TOKEN_EXCHANGE_MAX_EXPIRES_IN
        if value > max_expires_in:
            raise serializers.ValidationError(
                f"expires_in must not exceed {max_expires_in} seconds"
            )

        return value

    def validate_scope(self, value):
        """Validate and parse scopes."""
        if not value:
            return ""

        scopes = [scope.strip() for scope in value.split() if scope.strip()]

        action_count = len([scope for scope in scopes if scope.startswith("action:")])
        if action_count > 1:
            raise serializers.ValidationError("Only one action scope is allowed")

        if action_count and len(scopes) != 1:
            raise serializers.ValidationError(
                "Actions cannot be combined with other scopes"
            )

        # Return as-is, will be validated against subject_token_scope in the view
        return scopes

    def validate_audience(self, value):
        """Parse multiple audiences separated by spaces."""
        if not value:
            return []
        # Split by spaces and filter empty strings
        audiences = [aud.strip() for aud in value.split() if aud.strip()]
        return audiences

    def validate_subject_token_type(self, value):
        """Validate that subject_token_type is access_token."""
        expected = "urn:ietf:params:oauth:token-type:access_token"
        if value != expected:
            raise serializers.ValidationError(
                f"Invalid subject_token_type. Expected '{expected}', got '{value}'"
            )
        return value

    def validate(self, attrs):
        """Additional cross-field validation."""
        # If actor_token is provided, actor_token_type should also be provided
        if attrs.get("actor_token") and not attrs.get("actor_token_type"):
            raise serializers.ValidationError(
                {
                    "actor_token_type": "actor_token_type is required when actor_token is provided"
                }
            )

        return attrs


class TokenRevocationSerializer(serializers.Serializer):
    """
    Serializer for RFC 7009 token revocation requests.

    Validates the token revocation request parameters.
    """

    token = serializers.CharField(required=True)
    token_type_hint = serializers.CharField(required=False, allow_blank=True)

    def validate_token(self, value):
        """Validate that token is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Token cannot be empty")
        return value.strip()
