"""SCIM serializers for resource server API."""

from django.urls import reverse

from rest_framework import serializers

from core import models


class SCIMUserSerializer(serializers.ModelSerializer):
    """Serialize users in SCIM format."""

    schemas = serializers.SerializerMethodField()
    userName = serializers.CharField(source="sub")
    displayName = serializers.CharField(source="name")
    emails = serializers.SerializerMethodField()
    meta = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    active = serializers.BooleanField(source="is_active")

    class Meta:
        model = models.User
        fields = [
            "id",
            "schemas",
            "active",
            "userName",
            "displayName",
            "emails",
            "groups",
            "meta",
        ]
        read_only_fields = [
            "id",
            "schemas",
            "active",
            "userName",
            "displayName",
            "emails",
            "groups",
            "meta",
        ]

    def get_schemas(self, _obj):
        """Return the SCIM schemas for the user."""
        return ["urn:ietf:params:scim:schemas:core:2.0:User"]

    def get_emails(self, obj):
        """Return the user's email as a list of email objects."""
        if obj.email:
            return [
                {
                    "value": obj.email,
                    "primary": True,
                    "type": "work",
                }
            ]
        return []

    def get_groups(self, obj):
        """
        Return the groups the user belongs to.

        WARNING: you need to prefetch the team accesses in the
        viewset to avoid N+1 queries.
        """
        return [
            {
                "value": str(team_access.team.external_id),
                "display": team_access.team.name,
                "type": "direct",
            }
            for team_access in obj.accesses.all()
        ]

    def get_meta(self, obj):
        """Return metadata about the user."""
        request = self.context.get("request")
        location = (
            f"{request.build_absolute_uri('/').rstrip('/')}{reverse('scim-me-list')}"
            if request
            else None
        )

        return {
            "resourceType": "User",
            "created": obj.created_at.isoformat(),
            "lastModified": obj.updated_at.isoformat(),
            "location": location,
        }
