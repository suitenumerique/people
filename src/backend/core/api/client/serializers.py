"""Client serializers for the People core app."""

from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from core import models


class ContactSerializer(serializers.ModelSerializer):
    """Serialize contacts."""

    abilities = serializers.SerializerMethodField()

    class Meta:
        model = models.Contact
        fields = [
            "id",
            "abilities",
            "override",
            "data",
            "full_name",
            "notes",
            "owner",
            "short_name",
        ]
        read_only_fields = ["id", "owner", "abilities"]
        extra_kwargs = {
            "override": {"required": False},
        }

    def update(self, instance, validated_data):
        """Make "override" field readonly but only for update/patch."""
        validated_data.pop("override", None)
        return super().update(instance, validated_data)

    def get_abilities(self, contact) -> dict:
        """Return abilities of the logged-in user on the instance."""
        request = self.context.get("request")
        if request:
            return contact.get_abilities(request.user)
        return {}


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        """Pass arguments to superclass except 'fields', then drop fields not listed therein."""

        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop("fields", None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class OrganizationSerializer(serializers.ModelSerializer):
    """Serialize organizations."""

    abilities = serializers.SerializerMethodField()

    class Meta:
        model = models.Organization
        fields = ["id", "name", "registration_id_list", "domain_list", "abilities"]
        read_only_fields = ["id", "registration_id_list", "domain_list"]

    def get_abilities(self, organization) -> dict:
        """Return abilities of the logged-in user on the instance."""
        request = self.context.get("request")
        if request:
            return organization.get_abilities(request.user)
        return {}


class UserOrganizationSerializer(serializers.ModelSerializer):
    """Serialize organizations for users."""

    class Meta:
        model = models.Organization
        fields = ["id", "name", "registration_id_list"]
        read_only_fields = ["id", "name", "registration_id_list"]


class UserSerializer(DynamicFieldsModelSerializer):
    """Serialize users."""

    timezone = TimeZoneSerializerField(use_pytz=False, required=True)
    email = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    organization = UserOrganizationSerializer(read_only=True)

    class Meta:
        model = models.User
        fields = [
            "id",
            "email",
            "language",
            "name",
            "organization",
            "timezone",
            "is_device",
            "is_staff",
        ]
        read_only_fields = ["id", "name", "email", "is_device", "is_staff"]


class UserMeSerializer(UserSerializer):
    """
    Serialize the current user.

    Same as the `UserSerializer` but with abilities.
    """

    abilities = serializers.SerializerMethodField()
    organization = UserOrganizationSerializer(read_only=True)

    class Meta:
        model = models.User
        fields = [
            "email",
            "id",
            "is_device",
            "is_staff",
            "language",
            "name",
            "organization",
            "timezone",
            # added fields
            "abilities",
        ]
        read_only_fields = ["id", "name", "email", "is_device", "is_staff"]

    def get_abilities(self, user: models.User) -> dict:
        """Return abilities of the logged-in user on the instance."""
        if user != self.context["request"].user:  # Should not happen
            raise RuntimeError(
                "UserMeSerializer.get_abilities: user is not the same as the request user",
            )
        return user.get_abilities()


class ServiceProviderSerializer(serializers.ModelSerializer):
    """Serialize service providers."""

    class Meta:
        model = models.ServiceProvider
        fields = ["id", "audience_id", "name"]
        read_only_fields = ["id", "audience_id"]
