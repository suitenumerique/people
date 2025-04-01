from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from django.utils.translation import gettext_lazy as _

from mailbox_manager.models import Mailbox


class EmailLocalPartCharField(serializers.RegexField):
    default_error_messages = {
        'invalid': _('Enter a valid email local part ([a-zA-Z0-9.-]).'),
    }

    def __init__(self, **kwargs):
        super().__init__(r'^[a-zA-Z0-9.-]+$', **kwargs)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return data.lower()


class OrganizationActivationSerializer(serializers.Serializer):
    """
    Serializer for organization activation.

    We need enough information to create the organization's first user.
    """
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email_local_part = EmailLocalPartCharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        password = attrs['password']

        mailbox = Mailbox(
            first_name=attrs['first_name'],
            last_name=attrs['last_name'],
            local_part=attrs['email_local_part']
        )

        validate_password(password, mailbox)

        return attrs
