"""Client serializers for People's mailbox manager app."""

from rest_framework import serializers

from mailbox_manager import models


class MailboxSerializer(serializers.ModelSerializer):
    """Serialize mailbox."""

    class Meta:
        model = models.Mailbox
        fields = ["id", "local_part", "secondary_email"]


class MailDomainSerializer(serializers.ModelSerializer):
    """Serialize mail domain."""

    class Meta:
        model = models.MailDomain
        fields = [
            "id",
            "name",
            "created_at",
            "updated_at",
        ]


class MailDomainAccessSerializer(serializers.ModelSerializer):
    """Serialize mail domain accesses."""

    class Meta:
        model = models.MailDomainAccess
        fields = [
            "id",
            "user",
            "role",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id"]
