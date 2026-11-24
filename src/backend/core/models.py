"""
Declare and configure the models for the People core application
"""
# pylint: disable=too-many-lines import-outside-toplevel

import json
import os
import secrets
import uuid
from contextlib import suppress
from functools import lru_cache
from logging import getLogger
from typing import Optional, Tuple

from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.postgres.fields import ArrayField
from django.core import exceptions, mail, validators
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

import jsonschema
from timezone_field import TimeZoneField

from core.plugins.registry import registry as plugin_hooks_registry
from core.validators import get_field_validators_from_setting

logger = getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))

contact_schema_path = os.path.join(current_dir, "jsonschema", "contact_data.json")
with open(contact_schema_path, "r", encoding="utf-8") as contact_schema_file:
    contact_schema = json.load(contact_schema_file)


@lru_cache(maxsize=None)
def get_organization_metadata_schema() -> Optional[dict]:
    """Load the organization metadata schema from the settings."""
    if not settings.ORGANIZATION_METADATA_SCHEMA:
        logger.info("No organization metadata schema specified")
        return None

    organization_metadata_schema_path = os.path.join(
        current_dir,
        "jsonschema",
        settings.ORGANIZATION_METADATA_SCHEMA,
    )
    with open(
        organization_metadata_schema_path,
        "r",
        encoding="utf-8",
    ) as organization_metadata_schema_file:
        organization_metadata_schema = json.load(organization_metadata_schema_file)

    logger.info(
        "Loaded organization metadata schema from %s", organization_metadata_schema_path
    )
    return organization_metadata_schema


class RoleChoices(models.TextChoices):  # pylint: disable=too-many-ancestors
    """Defines the possible roles a user can have in a team."""

    MEMBER = "member", _("Member")
    ADMIN = "administrator", _("Administrator")
    OWNER = "owner", _("Owner")


class OrganizationRoleChoices(models.TextChoices):  # pylint: disable=too-many-ancestors
    """
    Defines the possible roles a user can have in an organization.
    For now, we only have one role, but we might add more in the future.

    administrator: The user can manage the organization: change name, add/remove users.
    """

    ADMIN = "administrator", _("Administrator")


class BaseModel(models.Model):
    """
    Serves as an abstract base model for otfget_her models, ensuring that records are validated
    before saving as Django doesn't do it by default.

    Includes fields common to all models: a UUID primary key and creation/update timestamps.
    """

    id = models.UUIDField(
        verbose_name=_("id"),
        help_text=_("primary key for the record as UUID"),
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    created_at = models.DateTimeField(
        verbose_name=_("created at"),
        help_text=_("date and time at which a record was created"),
        auto_now_add=True,
        editable=False,
    )
    updated_at = models.DateTimeField(
        verbose_name=_("updated at"),
        help_text=_("date and time at which a record was last updated"),
        auto_now=True,
        editable=False,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Call `full_clean` before saving."""
        self.full_clean()
        return super().save(*args, **kwargs)


class Contact(BaseModel):
    """User contacts"""

    override = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="overridden_by",
        null=True,
        blank=True,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contacts",
        null=True,
        blank=True,
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="profile_contact",
        blank=True,
        null=True,
    )

    full_name = models.CharField(_("full name"), max_length=150)
    short_name = models.CharField(_("short name"), max_length=30, null=True, blank=True)

    # avatar =
    notes = models.TextField(_("notes"), blank=True, default="")
    data = models.JSONField(
        _("contact information"),
        help_text=_("A JSON object containing the contact information"),
        blank=True,
    )

    class Meta:
        db_table = "people_contact"
        # indexes = [
        #     GinIndex(
        #         fields=["full_name", "short_name"],
        #         name="names_gin_trgm_idx",
        #         opclasses=['gin_trgm_ops', 'gin_trgm_ops']
        #     ),
        # ]
        ordering = ("full_name", "short_name")
        verbose_name = _("contact")
        verbose_name_plural = _("contacts")
        unique_together = ("owner", "override")
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(override__isnull=False, owner__isnull=True),
                name="override_owner_constraint",
                violation_error_message="A contact overriding a base contact must be owned.",
            ),
            models.CheckConstraint(
                condition=~models.Q(override=models.F("id")),
                name="override_not_self",
                violation_error_message="A contact cannot override itself.",
            ),
            # When a user is set, the owner must be the user
            models.CheckConstraint(
                condition=models.Q(user__isnull=True)
                | models.Q(owner=models.F("user"), owner__isnull=False),
                name="profile_contact_owner_constraint",
                violation_error_message="Users can only declare as profile a contact they own.",
            ),
        ]

    def __str__(self):
        return self.full_name

    def clean(self):
        """Validate fields."""
        super().clean()

        # Check if the contact overrides a contact that itself overrides another base contact
        if self.override_id and self.override.override_id:
            raise exceptions.ValidationError(
                "A contact cannot override a contact that itself overrides a contact."
            )

        # Validate the content of the "data" field against our jsonschema definition
        try:
            jsonschema.validate(self.data, contact_schema)
        except jsonschema.ValidationError as e:
            # Specify the property in the data in which the error occurred
            field_path = ".".join(map(str, e.path))
            error_message = f"Validation error in '{field_path:s}': {e.message}"
            raise exceptions.ValidationError({"data": [error_message]}) from e

    def get_abilities(self, user):
        """
        Compute and return abilities for a given user on the contact.

        Beware that the model allows owner to be None, we are still not
        sure about the use case for this and the API does not allow this.
        For now, we still consider here, a contact without owner is "public"
        so we allow access to it.
        """
        is_owner = user.pk == self.owner_id
        is_profile_member_or_same_organization = bool(self.user_id) and (
            self.user.organization_id == user.organization_id
        )

        return {
            "get": is_owner or is_profile_member_or_same_organization or not self.owner,
            "patch": is_owner,
            "put": is_owner,
            "delete": is_owner and not self.user,  # Can't delete a profile contact
        }


class ServiceProvider(BaseModel):
    """
    Represents a service provider that will consume our information.

    Organization uses this model to define the list of SP available to their users.
    """

    name = models.CharField(_("name"), max_length=256, unique=True)
    audience_id = models.CharField(
        _("audience id"), max_length=256, unique=True, db_index=True
    )

    class Meta:
        db_table = "people_service_provider"
        verbose_name = _("service provider")
        verbose_name_plural = _("service providers")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Enforce name (even if ugly) from the `audience_id` field."""
        if not self.name:
            self.name = self.audience_id  # ok, same length
        return super().save(*args, **kwargs)


class OrganizationManager(models.Manager):
    """
    Custom manager for the Organization model, to manage complexity/automation.
    """

    def get_or_create_from_user_claims(
        self, registration_id: str = None, domain: str = None, **kwargs
    ) -> Tuple["Organization", bool]:
        """
        Get or create an organization using the most fitting information from the user's claims.

        We expect to have only one organization per registration_id, but
        the registration_id might not be provided.
        When the registration_id is not provided, we use the domain to identify the organization.

        If both are provided, we use the registration_id first to create missing organization.

        Dev note: When a registration_id is provided by the Identity Provider, we don't want
        to use the domain to create the organization, because it is less reliable: for example,
        a professional user, may have a personal email address, and the domain would be gmail.com
        which is not a good identifier for an organization. The domain email is just a fallback
        when the registration_id is not provided by the Identity Provider. We can use the domain
        to create the organization manually when we are sure about the "safety" of it.
        """
        if not any([registration_id, domain]):
            raise ValueError("You must provide either a registration_id or a domain.")

        filters = models.Q()
        if registration_id:
            filters |= models.Q(registration_id_list__contains=[registration_id])
        if domain:
            filters |= models.Q(domain_list__contains=[domain.lower()])

        with suppress(self.model.DoesNotExist):
            # If there are several organizations, we must raise an error and fix the data
            # If there is an organization, we return it
            return self.get(filters, **kwargs), False

        # Manage the case where the organization does not exist: we create one
        if registration_id:
            return self.create(
                name=registration_id, registration_id_list=[registration_id], **kwargs
            ), True

        if domain:
            return (
                self.create(name=domain, domain_list=[domain.lower()], **kwargs),
                True,
            )

        raise ValueError("Should never reach this point.")

    def create(self, **kwargs):
        """
        Create an organization with the given kwargs.

        This method is overridden to call the Organization plugins.
        """
        instance = super().create(**kwargs)
        plugin_hooks_registry.execute_hook("organization_created", instance)
        return instance


class OrganizationAccessManager(models.Manager):
    """
    Custom manager for the OrganizationAccess model, to manage complexity/automation.
    """

    def create(self, **kwargs):
        """
        Create an organization access with the given kwargs.

        This method is overridden to call the Organization plugins.
        """
        instance = super().create(**kwargs)
        plugin_hooks_registry.execute_hook("organization_access_granted", instance)
        return instance


class Organization(BaseModel):
    """
    Organization model used to regroup the (now obsolete) Teams.

    Each User have an Organization, which corresponds actually to a default organization
    because a user can belong to a Team from another organization.
    Each Team have an Organization, which is the Organization from the User who created
    the Team.

    Organization is managed automatically, the User should never choose their Organization.
    When creating a User, you must use the `get_or_create` method from the
    OrganizationManager to find the proper Organization.

    An Organization can have several registration IDs and domains but during automatic
    creation process, only one will be used. We may want to allow (manual) organization merge
    later, to regroup several registration IDs or domain in the same Organization.
    """

    name = models.CharField(_("name"), max_length=100)
    registration_id_list = ArrayField(
        models.CharField(
            max_length=128,
            validators=get_field_validators_from_setting(
                "ORGANIZATION_REGISTRATION_ID_VALIDATORS"
            ),
        ),
        verbose_name=_("registration ID list"),
        default=list,
        blank=True,
        # list overlap validation is done in the validate_unique method
    )
    domain_list = ArrayField(
        models.CharField(max_length=256),
        verbose_name=_("domain list"),
        default=list,
        blank=True,
        # list overlap validation is done in the validate_unique method
    )

    metadata = models.JSONField(
        _("metadata"),
        help_text=_("A JSON object containing the organization metadata"),
        blank=True,
        default=dict,
    )

    service_providers = models.ManyToManyField(
        ServiceProvider,
        related_name="organizations",
        blank=True,
    )
    is_active = models.BooleanField(verbose_name=_("active"), default=True)

    objects = OrganizationManager()

    class Meta:
        db_table = "people_organization"
        verbose_name = _("organization")
        verbose_name_plural = _("organizations")
        constraints = [
            models.CheckConstraint(
                name="registration_id_or_domain",
                condition=models.Q(registration_id_list__len__gt=0)
                | models.Q(domain_list__len__gt=0),
                violation_error_message=_(
                    "An organization must have at least a registration ID or a domain."
                ),
            ),
            # Check a registration ID str can only be present in one
            # organization registration ID list
            # Check a domain str can only be present in one organization domain list
            # Those checks cannot be done with Django constraints
        ]

    def __str__(self):
        return f"{self.name} (# {self.pk})"

    def clean(self):
        """Validate fields."""
        super().clean()

        organization_metadata_schema = get_organization_metadata_schema()
        if not organization_metadata_schema:
            return

        try:
            jsonschema.validate(self.metadata, organization_metadata_schema)
        except jsonschema.ValidationError as e:
            # Specify the property in the data in which the error occurred
            field_path = ".".join(map(str, e.path))
            error_message = f"Validation error in '{field_path:s}': {e.message}"
            raise exceptions.ValidationError({"metadata": [error_message]}) from e

    def validate_unique(self, exclude=None):
        """
        Validate Registration/Domain values in an array field are unique
        across all instances.

        This can't be done in the field validator because we need to
        exclude the current object if already in database.
        """
        super().validate_unique(exclude=exclude)

        if self.pk:
            organization_qs = Organization.objects.exclude(pk=self.pk)
        else:
            organization_qs = Organization.objects.all()

        # Check a registration ID can only be present in one organization
        if (
            self.registration_id_list
            and organization_qs.filter(
                registration_id_list__overlap=self.registration_id_list
            ).exists()
        ):
            raise ValidationError(
                "registration_id_list value must be unique across all instances."
            )

        # Check a domain can only be present in one organization
        if (
            self.domain_list
            and organization_qs.filter(domain_list__overlap=self.domain_list).exists()
        ):
            raise ValidationError(
                "domain_list value must be unique across all instances."
            )

    def get_abilities(self, user):
        """
        Compute and return abilities for a given user on the organization.
        """
        # Use the role from queryset annotation will raise on purpose if not used properly
        is_admin = self.user_role == OrganizationRoleChoices.ADMIN  # pylint: disable=no-member

        return {
            "get": user.organization_id == self.pk,
            "patch": is_admin,
            "put": is_admin,
            "delete": False,
        }


class User(AbstractBaseUser, BaseModel, auth_models.PermissionsMixin):
    """User model to work with OIDC only authentication."""

    sub_validator = validators.RegexValidator(
        regex=r"^[\w.@+-]+\Z",
        message=_(
            "Enter a valid sub. This value may contain only letters, "
            "numbers, and @/./+/-/_ characters."
        ),
    )

    sub = models.CharField(
        _("sub"),
        help_text=_(
            "Required. 255 characters or fewer. Letters, numbers, and @/./+/-/_ characters only."
        ),
        max_length=255,
        unique=True,
        validators=[sub_validator],
    )
    email = models.EmailField(_("email address"), null=True, blank=True)
    name = models.CharField(_("name"), max_length=100, null=True, blank=True)
    language = models.CharField(
        max_length=10,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
        verbose_name=_("language"),
        help_text=_("The language in which the user wants to see the interface."),
    )
    timezone = TimeZoneField(
        choices_display="WITH_GMT_OFFSET",
        use_pytz=False,
        default=settings.TIME_ZONE,
        help_text=_("The timezone in which the user wants to see times."),
    )
    is_device = models.BooleanField(
        _("device"),
        default=False,
        help_text=_("Whether the user is a device or a real user."),
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="users",
        null=True,  # Need to be set to False when everything is migrated
        blank=True,  # Need to be set to False when everything is migrated
    )
    is_public_servant = models.BooleanField(
        default=False,
    )

    objects = auth_models.UserManager()

    USERNAME_FIELD = "sub"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "people_user"
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.name if self.name else self.email or f"User {self.sub}"

    def clean(self):
        """Validate fields."""
        super().clean()
        if self.email:
            self.email = User.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Email this user."""
        if not self.email:
            raise ValueError("You must first set an email for the user.")
        mail.send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_abilities(self):
        """
        Return the user permissions at the application level (ie feature availability).

        Note: this is for display purposes only for now.

        - Contacts view and creation is globally available (or not) for now.
        - Mailboxes view is available if the user has access to at least one
        MailDomain for now. It allows to restrict users knowing the existence of
        this feature.
        - Mailboxes creation is globally available (or not) for now.
        """
        user_info = (
            self._meta.model.objects.filter(pk=self.pk)
            .annotate(
                mailboxes_can_view=models.Exists(
                    self.mail_domain_accesses.model.objects.filter(  # pylint: disable=no-member
                        user=models.OuterRef("pk")
                    )
                ),
            )
            .only("id")
            .get()
        )

        mailboxes_can_view = user_info.mailboxes_can_view

        return {
            "contacts": {
                "can_view": settings.FEATURES["CONTACTS_DISPLAY"],
                "can_create": (
                    settings.FEATURES["CONTACTS_DISPLAY"]
                    and settings.FEATURES["CONTACTS_CREATE"]
                ),
            },
            "mailboxes": {
                "can_view": mailboxes_can_view,
                "can_create": mailboxes_can_view
                and settings.FEATURES["MAILBOXES_CREATE"],
            },
        }


class OrganizationAccess(BaseModel):
    """
    Link table between organization and users,
    only for user with specific rights on Organization.
    """

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="organization_accesses",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="organization_accesses",
    )
    role = models.CharField(
        max_length=20,
        choices=OrganizationRoleChoices.choices,
        default=OrganizationRoleChoices.ADMIN,
    )

    objects = OrganizationAccessManager()

    class Meta:
        db_table = "people_organization_access"
        verbose_name = _("Organization/user relation")
        verbose_name_plural = _("Organization/user relations")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organization"],
                name="unique_organization_user",
                violation_error_message=_("This user is already in this organization."),
            ),
        ]

    def __str__(self):
        return f"{self.user!s} is {self.role:s} in organization {self.organization!s}"


def validate_account_service_scope(scope):
    """Validate the scope of the account service."""
    if scope not in settings.ACCOUNT_SERVICE_SCOPES:
        raise ValidationError(f"Invalid scope: {scope}")


class AccountService(BaseModel):
    """Account service model."""

    name = models.CharField(_("name"), max_length=255)
    api_key = models.CharField(
        _("api key"),
        max_length=255,
    )
    scopes = ArrayField(
        models.CharField(max_length=255, validators=[validate_account_service_scope]),
        verbose_name=_("allowed scopes"),
        help_text=_("Allowed scopes for this service"),
    )

    class Meta:
        db_table = "people_account_service"
        verbose_name = _("Account service")
        verbose_name_plural = _("Account services")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Override save method to generate a new api_key if it is not set.
        """
        if not self.api_key:
            self.api_key = secrets.token_urlsafe(32)
        return super().save(*args, **kwargs)

    @property
    def is_authenticated(self):
        """Indicate if the account service is authenticated."""
        return True
