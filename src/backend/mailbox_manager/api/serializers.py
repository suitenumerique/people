"""Client serializers for People's mailbox manager app."""

from rest_framework import serializers

from mailbox_manager import models


class MailboxSerializer(serializers.ModelSerializer):
    """Serialize mailbox."""

    class Meta:
        model = models.Mailbox
        fields = ["id", "first_name", "last_name", "local_part", "secondary_email"]
        # everything is actually read-only as we do not allow update for now
        read_only_fields = ["id"]


class MailDomainSerializer(serializers.ModelSerializer):
    """Serialize mail domain."""

    abilities = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.MailDomain
        lookup_field = "slug"
        fields = [
            "id",
            "name",
            "slug",
            "status",
            "abilities",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "status",
            "abilities",
            "created_at",
            "updated_at",
        ]

    def get_abilities(self, domain) -> dict:
        """Return abilities of the logged-in user on the instance."""
        request = self.context.get("request")
        if request:
            return domain.get_abilities(request.user)
        return {}


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
