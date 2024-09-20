"""Client serializers for People's mailbox manager app."""

import json

from rest_framework import serializers

from core.api.serializers import UserSerializer

from mailbox_manager import enums, models
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
        """Return roles available to set"""
        roles = list(enums.MailDomainRoleChoices)
        # get role of authenticated user
        authenticated_user_role = access.user_role
        if authenticated_user_role != enums.MailDomainRoleChoices.OWNER:
            roles.remove(enums.MailDomainRoleChoices.OWNER)
        # if the user authenticated is a viewer, they can't modify role
        # and only an owner can change role of an owner
        if authenticated_user_role == enums.MailDomainRoleChoices.VIEWER or (
            authenticated_user_role != enums.MailDomainRoleChoices.OWNER
            and access.role == enums.MailDomainRoleChoices.OWNER
        ):
            return []
        # we only want to return other roles available to change,
        # so we remove the current role of current access.
        roles.remove(access.role)
        return sorted(roles)


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
