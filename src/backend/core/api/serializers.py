"""Client serializers for the People core app."""

from rest_framework import exceptions, serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from core import models


class ContactSerializer(serializers.ModelSerializer):
    """Serialize contacts."""

    class Meta:
        model = models.Contact
        fields = [
            "id",
            "base",
            "data",
            "full_name",
            "owner",
            "short_name",
        ]
        read_only_fields = ["id", "owner"]

    def update(self, instance, validated_data):
        """Make "base" field readonly but only for update/patch."""
        validated_data.pop("base", None)
        return super().update(instance, validated_data)


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


class UserSerializer(DynamicFieldsModelSerializer):
    """Serialize users."""

    timezone = TimeZoneSerializerField(use_pytz=False, required=True)
    email = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()

    class Meta:
        model = models.User
        fields = [
            "id",
            "email",
            "language",
            "name",
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

    class Meta:
        model = models.User
        fields = [
            "email",
            "id",
            "is_device",
            "is_staff",
            "language",
            "name",
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


class TeamAccessSerializer(serializers.ModelSerializer):
    """Serialize team accesses."""

    abilities = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.TeamAccess
        fields = ["id", "user", "role", "abilities"]
        read_only_fields = ["id", "abilities"]

    def update(self, instance, validated_data):
        """Make "user" field is readonly but only on update."""
        validated_data.pop("user", None)
        return super().update(instance, validated_data)

    def get_abilities(self, access) -> dict:
        """Return abilities of the logged-in user on the instance."""
        request = self.context.get("request")
        if request:
            return access.get_abilities(request.user)
        return {}

    def validate(self, attrs):
        """
        Check access rights specific to writing (create/update)
        """
        request = self.context.get("request")
        user = getattr(request, "user", None)
        role = attrs.get("role")

        # Update
        if self.instance:
            can_set_role_to = self.instance.get_abilities(user)["set_role_to"]

            if role and role not in can_set_role_to:
                message = (
                    f"You are only allowed to set role to {', '.join(can_set_role_to)}"
                    if can_set_role_to
                    else "You are not allowed to set this role for this team."
                )
                raise exceptions.PermissionDenied(message)

        # Create
        else:
            try:
                team_id = self.context["team_id"]
            except KeyError as exc:
                raise exceptions.ValidationError(
                    "You must set a team ID in kwargs to create a new team access."
                ) from exc

            if not models.TeamAccess.objects.filter(
                team=team_id,
                user=user,
                role__in=[models.RoleChoices.OWNER, models.RoleChoices.ADMIN],
            ).exists():
                raise exceptions.PermissionDenied(
                    "You are not allowed to manage accesses for this team."
                )

            if (
                role == models.RoleChoices.OWNER
                and not models.TeamAccess.objects.filter(
                    team=team_id,
                    user=user,
                    role=models.RoleChoices.OWNER,
                ).exists()
            ):
                raise exceptions.PermissionDenied(
                    "Only owners of a team can assign other users as owners."
                )

        attrs["team_id"] = self.context["team_id"]
        return attrs


class TeamAccessReadOnlySerializer(TeamAccessSerializer):
    """Serialize team accesses for list and retrieve actions."""

    user = UserSerializer(read_only=True, fields=["id", "name", "email"])

    class Meta:
        model = models.TeamAccess
        fields = [
            "id",
            "user",
            "role",
            "abilities",
        ]
        read_only_fields = [
            "id",
            "user",
            "role",
            "abilities",
        ]


class TeamSerializer(serializers.ModelSerializer):
    """Serialize teams."""

    abilities = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Team
        fields = [
            "id",
            "name",
            "accesses",
            "abilities",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "accesses",
            "abilities",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        """Create a new team with organization enforcement."""
        # Note: this is not the purpose of this API to check the user has an organization
        return super().create(
            validated_data=validated_data
            | {"organization_id": self.context["request"].user.organization_id}
        )

    def get_abilities(self, team) -> dict:
        """Return abilities of the logged-in user on the instance."""
        request = self.context.get("request")
        if request:
            return team.get_abilities(request.user)
        return {}


class InvitationSerializer(serializers.ModelSerializer):
    """Serialize invitations."""

    class Meta:
        model = models.Invitation
        fields = ["id", "created_at", "email", "team", "role", "issuer", "is_expired"]
        read_only_fields = ["id", "created_at", "team", "issuer", "is_expired"]

    def validate(self, attrs):
        """Validate and restrict invitation to new user based on email."""

        request = self.context.get("request")
        user = getattr(request, "user", None)

        try:
            team_id = self.context["team_id"]
        except KeyError as exc:
            raise exceptions.ValidationError(
                "You must set a team ID in kwargs to create a new team invitation."
            ) from exc

        if not models.TeamAccess.objects.filter(
            team=team_id,
            user=user,
            role__in=[models.RoleChoices.OWNER, models.RoleChoices.ADMIN],
        ).exists():
            raise exceptions.PermissionDenied(
                "You are not allowed to manage invitation for this team."
            )

        attrs["team_id"] = team_id
        attrs["issuer"] = user
        return attrs
