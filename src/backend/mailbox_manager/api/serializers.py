"""Client serializers for the People mailbox_manager app."""

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
        fields = ["id", "name"]
