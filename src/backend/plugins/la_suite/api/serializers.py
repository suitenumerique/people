"""API serializers for the la suite plugin."""

from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers


class EmailLocalPartCharField(serializers.RegexField):
    """
    A field that validates an email local part.
    """

    default_error_messages = {
        "invalid": _("Enter a valid email local part ([a-zA-Z0-9.-])."),
    }

    def __init__(self, **kwargs):
        """
        Initialize the EmailLocalPartCharField.
        """
        super().__init__(r"^[a-zA-Z0-9.-]+$", **kwargs)

    def to_internal_value(self, data):
        """
        Override the to_internal_value method to convert the data to lowercase.
        """
        data = super().to_internal_value(data)
        return data.lower()


class OrganizationActivationSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """
    Serializer for organization activation.

    We need enough information to create the organization's first user.
    """

    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email_local_part = EmailLocalPartCharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        Override the validate method to validate password.
        """
        validate_password(attrs["password"])
        return super().validate(attrs)
