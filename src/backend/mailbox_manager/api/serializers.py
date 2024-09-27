"""Client serializers for People's mailbox manager app."""

import json

from rest_framework import exceptions, serializers

from core.api.serializers import UserSerializer

from mailbox_manager import models
from mailbox_manager.utils.dimail import DimailAPIClient


class MailboxSerializer(serializers.ModelSerializer):
    """Serialize mailbox."""

    class Meta:
        model = models.Mailbox
        fields = ["id", "first_name", "last_name", "local_part", "secondary_email"]
        # everything is actually read-only as we do not allow update for now
        read_only_fields = ["id"]

    def create(self, validated_data):
        """
        Override create function to fire a request on mailbox creation.
        """
        # send new mailbox request to dimail
        client = DimailAPIClient()
        response = client.send_mailbox_request(
            validated_data, self.context["request"].user.sub
        )

        # fix format to have actual json, and remove uuid
        mailbox_data = json.loads(response.content.decode("utf-8").replace("'", '"'))
        del mailbox_data["uuid"]

        # actually save mailbox on our database
        instance = models.Mailbox.objects.create(**validated_data)

        # send confirmation email
        client.send_new_mailbox_notification(
            recipient=validated_data["secondary_email"], mailbox_data=mailbox_data
        )
        return instance


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
    """Serialize mail domain access."""

    user = UserSerializer(read_only=True, fields=["id", "name", "email"])
    can_set_role_to = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.MailDomainAccess
        fields = [
            "id",
            "user",
            "role",
            "can_set_role_to",
        ]
        read_only_fields = ["id", "user", "can_set_role_to"]

    def get_can_set_role_to(self, access):
        """Return roles available to set for the authenticated user"""
        return access.get_can_set_role_to(self.context.get("request").user)

    def validate(self, attrs):
        """
        Check access rights specific to writing (update)
        """
        request = self.context.get("request")
        authenticated_user = getattr(request, "user", None)
        role = attrs.get("role")

        # Update
        if self.instance:
            can_set_role_to = self.instance.get_can_set_role_to(authenticated_user)

            if role and role not in can_set_role_to:
                message = (
                    f"You are only allowed to set role to {', '.join(can_set_role_to)}"
                    if can_set_role_to
                    else "You are not allowed to modify role for this user."
                )
                raise exceptions.PermissionDenied(message)
        return attrs


class MailDomainAccessReadOnlySerializer(MailDomainAccessSerializer):
    """Serialize mail domain access for list and retrieve actions."""

    class Meta:
        model = models.MailDomainAccess
        fields = [
            "id",
            "user",
            "role",
            "can_set_role_to",
        ]
        read_only_fields = [
            "id",
            "user",
            "role",
            "can_set_role_to",
        ]
