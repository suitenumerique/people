"""Client serializers for People's mailbox manager app."""

from logging import getLogger

from django.contrib.auth.hashers import make_password
from django.core import exceptions as django_exceptions

from requests.exceptions import HTTPError
from rest_framework import exceptions, serializers

from core.api.client.serializers import UserSerializer
from core.models import User

from mailbox_manager import enums, models
from mailbox_manager.utils.dimail import DimailAPIClient

logger = getLogger(__name__)


class MailboxSerializer(serializers.ModelSerializer):
    """Serialize mailbox."""

    class Meta:
        model = models.Mailbox
        fields = [
            "id",
            "first_name",
            "last_name",
            "local_part",
            "secondary_email",
            "status",
        ]
        read_only_fields = ["id", "status"]

    def create(self, validated_data):
        """
        Override create function to fire a request on mailbox creation.

        By default, we generate an unusable password for the mailbox, meaning that the mailbox
        will not be able to be used as a login credential until the password is set.
        """
        mailbox = super().create(
            validated_data
            | {
                "password": make_password(None),  # generate an unusable password
            }
        )

        if validated_data["domain"].status == enums.MailDomainStatusChoices.ENABLED:
            # send new mailbox request to dimail
            client = DimailAPIClient()
            try:
                response = client.create_mailbox(
                    mailbox, self.context["request"].user.sub
                )
            except django_exceptions.ValidationError as exc:
                mailbox.delete()
                raise exc

            mailbox.status = enums.MailDomainStatusChoices.ENABLED
            mailbox_data = response.json()
            mailbox.set_password(mailbox_data["password"])
            mailbox.save()

            if mailbox.secondary_email:
                # send confirmation email
                client.notify_mailbox_creation(
                    recipient=mailbox.secondary_email,
                    mailbox_data=response.json(),
                    issuer=self.context["request"].user,
                )
            else:
                logger.warning(
                    "Email notification for %s creation not sent "
                    "because no secondary email found",
                    mailbox,
                )

        return mailbox


class MailboxUpdateSerializer(MailboxSerializer):
    """A more restrictive serializer when updating mailboxes"""

    class Meta:
        model = models.Mailbox
        fields = [
            "id",
            "first_name",
            "last_name",
            "local_part",
            "secondary_email",
            "status",
        ]
        read_only_fields = ("id", "local_part", "status")


class MailDomainSerializer(serializers.ModelSerializer):
    """Serialize mail domain."""

    abilities = serializers.SerializerMethodField(read_only=True)
    count_mailboxes = serializers.SerializerMethodField(read_only=True)
    action_required_details = serializers.SerializerMethodField(read_only=True)

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
            "count_mailboxes",
            "support_email",
            "last_check_details",
            "action_required_details",
            "expected_config",
        ]
        read_only_fields = [
            "id",
            "slug",
            "status",
            "abilities",
            "created_at",
            "updated_at",
            "count_mailboxes",
            "last_check_details",
            "action_required_details",
            "expected_config",
        ]

    def get_action_required_details(self, domain) -> dict:
        """Return last check details of the domain."""
        details = {}
        if domain.last_check_details:
            for check, value in domain.last_check_details.items():
                if (
                    isinstance(value, dict)
                    and value.get("ok") is False
                    and value.get("internal") is False
                ):
                    details[check] = value["errors"][0].get("detail")
        return details

    def get_abilities(self, domain) -> dict:
        """Return abilities of the logged-in user on the instance."""
        request = self.context.get("request")
        if request:
            return domain.get_abilities(request.user)
        return {}

    def get_count_mailboxes(self, domain) -> int:
        """Return count of mailboxes for the domain."""
        return domain.mailboxes.count()

    def create(self, validated_data):
        """
        Override create function to fire a request to dimail upon domain creation.
        """
        # send new domain request to dimail
        client = DimailAPIClient()
        client.create_domain(validated_data["name"], self.context["request"].user.sub)
        domain = super().create(validated_data)
        # check domain status and update it
        try:
            client.fetch_domain_status(domain)
            client.fetch_domain_expected_config(domain)
        except HTTPError as e:
            logger.exception(
                "[DIMAIL] domain status fetch after creation failed %s with error %s",
                domain.name,
                e,
            )
        return domain


class MailDomainAccessSerializer(serializers.ModelSerializer):
    """Serialize mail domain access."""

    user = UserSerializer(read_only=True, fields=["id", "name", "email"])
    can_set_role_to = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.MailDomainAccess
        fields = ["id", "user", "role", "can_set_role_to"]
        read_only_fields = ["id", "can_set_role_to"]

    def update(self, instance, validated_data):
        """Make "user" field is readonly but only on update."""
        validated_data.pop("user", None)
        return super().update(instance, validated_data)

    def get_can_set_role_to(self, access):
        """Return roles available to set for the authenticated user"""
        return access.get_can_set_role_to(self.context.get("request").user)

    def validate(self, attrs):
        """
        Check access rights specific to writing (update/create)
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
        # Create
        else:
            # A domain slug has to be set to create a new access
            try:
                domain_slug = self.context["domain_slug"]
            except KeyError as exc:
                raise exceptions.ValidationError(
                    "You must set a domain slug in kwargs to create a new domain access."
                ) from exc

            try:
                access = authenticated_user.mail_domain_accesses.get(
                    domain__slug=domain_slug
                )
            except models.MailDomainAccess.DoesNotExist as exc:
                raise exceptions.PermissionDenied(
                    "You are not allowed to manage accesses for this domain."
                ) from exc

            # Authenticated user must be owner or admin of current domain to set new roles
            if access.role not in [
                enums.MailDomainRoleChoices.OWNER,
                enums.MailDomainRoleChoices.ADMIN,
            ]:
                raise exceptions.PermissionDenied(
                    "You are not allowed to manage accesses for this domain."
                )

            # only an owner can set an owner role to another user
            if (
                role == enums.MailDomainRoleChoices.OWNER
                and access.role != enums.MailDomainRoleChoices.OWNER
            ):
                raise exceptions.PermissionDenied(
                    "Only owners of a domain can assign other users as owners."
                )
            attrs["user"] = User.objects.get(pk=self.initial_data["user"])
            attrs["domain"] = models.MailDomain.objects.get(
                slug=self.context["domain_slug"]
            )
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


class MailDomainInvitationSerializer(serializers.ModelSerializer):
    """Serialize invitations."""

    class Meta:
        model = models.MailDomainInvitation
        fields = ["id", "created_at", "email", "domain", "role", "issuer", "is_expired"]
        read_only_fields = ["id", "created_at", "domain", "issuer", "is_expired"]

    def validate(self, attrs):
        """Validate and restrict invitation to new user based on email."""

        request = self.context.get("request")
        user = getattr(request, "user", None)

        try:
            domain_slug = self.context["domain_slug"]
        except KeyError as exc:
            raise exceptions.ValidationError(
                "You must set a domain slug in kwargs to create a new domain management invitation."
            ) from exc

        domain = models.MailDomain.objects.get(slug=domain_slug)
        if not domain.get_abilities(user)["manage_accesses"]:
            raise exceptions.PermissionDenied(
                "You are not allowed to manage invitations for this domain."
            )

        attrs["domain"] = domain
        attrs["issuer"] = user
        return attrs


class AliasSerializer(serializers.ModelSerializer):
    """Serialize mailbox."""

    class Meta:
        model = models.Alias
        fields = [
            "id",
            "local_part",
            "destination",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        """
        Override create function to fire a request to dimail on alias creation.
        """
        if validated_data["domain"].status == enums.MailDomainStatusChoices.ENABLED:
            alias = models.Alias(**validated_data)

            # send new alias request to dimail
            client = DimailAPIClient()
            client.create_alias(alias, self.context["request"].user.sub)
            return super().create(validated_data)

        return None

    def validate_local_part(self, value):
        """Validate this local part does not match a mailbox."""
        if models.Mailbox.objects.filter(
            local_part=value, domain__slug=self.context["domain_slug"]
        ).exists():
            raise exceptions.ValidationError(
                f'Local part "{value}" already used for a mailbox.'
            )

        return value
