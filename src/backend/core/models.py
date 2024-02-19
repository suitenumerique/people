"""
Declare and configure the models for the People core application
"""
import json
import os
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.auth.base_user import AbstractBaseUser
from django.core import exceptions, mail, validators
from django.db import models
from django.utils import timezone
from django.utils.functional import lazy
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

import jsonschema
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings
from timezone_field import TimeZoneField

current_dir = os.path.dirname(os.path.abspath(__file__))
contact_schema_path = os.path.join(current_dir, "jsonschema", "contact_data.json")
with open(contact_schema_path, "r", encoding="utf-8") as contact_schema_file:
    contact_schema = json.load(contact_schema_file)


class RoleChoices(models.TextChoices):
    """Defines the possible roles a user can have in a team."""

    MEMBER = "member", _("Member")
    ADMIN = "administrator", _("Administrator")
    OWNER = "owner", _("Owner")


class BaseModel(models.Model):
    """
    Serves as an abstract base model for other models, ensuring that records are validated
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
        super().save(*args, **kwargs)


class Contact(BaseModel):
    """User contacts"""

    base = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="overriding_contacts",
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
    full_name = models.CharField(_("full name"), max_length=150, null=True, blank=True)
    short_name = models.CharField(_("short name"), max_length=30, null=True, blank=True)

    # avatar =
    # notes =
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
        unique_together = ("owner", "base")
        constraints = [
            models.CheckConstraint(
                check=~models.Q(base__isnull=False, owner__isnull=True),
                name="base_owner_constraint",
                violation_error_message="A contact overriding a base contact must be owned.",
            ),
            models.CheckConstraint(
                check=~models.Q(base=models.F("id")),
                name="base_not_self",
                violation_error_message="A contact cannot be based on itself.",
            ),
        ]

    def __str__(self):
        return self.full_name or self.short_name

    def clean(self):
        """Validate fields."""
        super().clean()

        # Check if the contact points to a base contact that itself points to another base contact
        if self.base_id and self.base.base_id:
            raise exceptions.ValidationError(
                "A contact cannot point to a base contact that itself points to a base contact."
            )

        # Validate the content of the "data" field against our jsonschema definition
        try:
            jsonschema.validate(self.data, contact_schema)
        except jsonschema.ValidationError as e:
            # Specify the property in the data in which the error occurred
            field_path = ".".join(map(str, e.path))
            error_message = f"Validation error in '{field_path:s}': {e.message}"
            raise exceptions.ValidationError({"data": [error_message]}) from e


class User(AbstractBaseUser, BaseModel, auth_models.PermissionsMixin):
    """User model to work with OIDC only authentication."""

    email = models.EmailField(_("email address"), unique=True, null=True, blank=True)
    profile_contact = models.OneToOneField(
        Contact,
        on_delete=models.SET_NULL,
        related_name="user",
        blank=True,
        null=True,
    )
    language = models.CharField(
        max_length=10,
        choices=lazy(lambda: settings.LANGUAGES, tuple)(),
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

    objects = auth_models.UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "people_user"
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return (
            str(self.profile_contact)
            if self.profile_contact
            else self.email or str(self.id)
        )

    def clean(self):
        """Validate fields."""
        super().clean()

        if self.profile_contact_id and not self.profile_contact.owner == self:
            raise exceptions.ValidationError(
                "Users can only declare as profile a contact they own."
            )

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Email this user."""
        main_identity = self.identities.get(is_main=True)
        mail.send_mail(subject, message, from_email, [main_identity.email], **kwargs)

    @classmethod
    def get_email_field_name(cls):
        """
        Raise error when trying to get email field name from the user as we are using
        a separate Email model to allow several emails per user.
        """
        raise NotImplementedError(
            "This feature is deactivated to allow several emails per user."
        )


class Identity(BaseModel):
    """User identity"""

    sub_validator = validators.RegexValidator(
        regex=r"^[\w.@+-]+\Z",
        message=_(
            "Enter a valid sub. This value may contain only letters, "
            "numbers, and @/./+/-/_ characters."
        ),
    )

    user = models.ForeignKey(User, related_name="identities", on_delete=models.CASCADE)
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
    is_main = models.BooleanField(
        _("main"),
        default=False,
        help_text=_("Designates whether the email is the main one."),
    )

    class Meta:
        db_table = "people_identity"
        ordering = ("-is_main", "email")
        verbose_name = _("identity")
        verbose_name_plural = _("identities")
        constraints = [
            # Uniqueness
            models.UniqueConstraint(
                fields=["user", "email"],
                name="unique_user_email",
                violation_error_message=_(
                    "This email address is already declared for this user."
                ),
            ),
        ]

    def __str__(self):
        main_str = "[main]" if self.is_main else ""
        id_str = self.email or self.sub
        return f"{id_str:s}{main_str:s}"

    def save(self, *args, **kwargs):
        """Ensure users always have one and only one main identity."""
        super().save(*args, **kwargs)
        if self.is_main is True:
            self.user.identities.exclude(id=self.id).update(is_main=False)

    def clean(self):
        """Normalize the email field and clean the 'is_main' field."""
        if self.email:
            self.email = User.objects.normalize_email(self.email)
        if not self.user.identities.exclude(pk=self.pk).filter(is_main=True).exists():
            if not self.created_at:
                self.is_main = True
            elif not self.is_main:
                raise exceptions.ValidationError(
                    {"is_main": "A user should have one and only one main identity."}
                )
        super().clean()


class Team(BaseModel):
    """
    Represents the link between teams and users, specifying the role a user has in a team.
    """

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, null=False, editable=False)

    users = models.ManyToManyField(
        User,
        through="TeamAccess",
        through_fields=("team", "user"),
        related_name="teams",
    )

    class Meta:
        db_table = "people_team"
        ordering = ("name",)
        verbose_name = _("Team")
        verbose_name_plural = _("Teams")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Overriding save function to compute the slug."""
        self.slug = self.get_slug()
        return super().save(*args, **kwargs)

    def get_slug(self):
        """Compute slug value from name."""
        return slugify(self.name)

    def get_abilities(self, user):
        """
        Compute and return abilities for a given user on the team.
        """
        is_owner_or_admin = False
        role = None

        if user.is_authenticated:
            try:
                role = self.user_role
            except AttributeError:
                try:
                    role = self.accesses.filter(user=user).values("role")[0]["role"]
                except (TeamAccess.DoesNotExist, IndexError):
                    role = None

            is_owner_or_admin = role in [RoleChoices.OWNER, RoleChoices.ADMIN]

        return {
            "get": True,
            "patch": is_owner_or_admin,
            "put": is_owner_or_admin,
            "delete": role == RoleChoices.OWNER,
            "manage_accesses": is_owner_or_admin,
        }


class TeamAccess(BaseModel):
    """Link table between teams and contacts."""

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="accesses",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="accesses",
    )
    role = models.CharField(
        max_length=20, choices=RoleChoices.choices, default=RoleChoices.MEMBER
    )

    class Meta:
        db_table = "people_team_access"
        verbose_name = _("Team/user relation")
        verbose_name_plural = _("Team/user relations")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "team"],
                name="unique_team_user",
                violation_error_message=_("This user is already in this team."),
            ),
        ]

    def __str__(self):
        return f"{self.user!s} is {self.role:s} in team {self.team!s}"

    def get_abilities(self, user):
        """
        Compute and return abilities for a given user taking into account
        the current state of the object.
        """
        is_team_owner_or_admin = False
        role = None

        if user.is_authenticated:
            try:
                role = self.user_role
            except AttributeError:
                try:
                    role = self._meta.model.objects.filter(
                        team=self.team_id, user=user
                    ).values("role")[0]["role"]
                except (self._meta.model.DoesNotExist, IndexError):
                    role = None

            is_team_owner_or_admin = role in [RoleChoices.OWNER, RoleChoices.ADMIN]

        if self.role == RoleChoices.OWNER:
            can_delete = (
                user.id == self.user_id
                and self.team.accesses.filter(role=RoleChoices.OWNER).count() > 1
            )
            set_role_to = [RoleChoices.ADMIN, RoleChoices.MEMBER] if can_delete else []
        else:
            can_delete = is_team_owner_or_admin
            set_role_to = []
            if role == RoleChoices.OWNER:
                set_role_to.append(RoleChoices.OWNER)
            if is_team_owner_or_admin:
                set_role_to.extend([RoleChoices.ADMIN, RoleChoices.MEMBER])

        # Remove the current role as we don't want to propose it as an option
        try:
            set_role_to.remove(self.role)
        except ValueError:
            pass

        return {
            "delete": can_delete,
            "get": bool(role),
            "patch": bool(set_role_to),
            "put": bool(set_role_to),
            "set_role_to": set_role_to,
        }


class Invitation(BaseModel):
    """User invitation to teams."""

    email = models.EmailField(_("email address"), null=False, blank=False)
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="invitations",
    )
    role = models.CharField(
        max_length=20, choices=RoleChoices.choices, default=RoleChoices.MEMBER
    )
    issuer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="invitations",
    )

    def __str__(self):
        return f"{self.email} invited to {self.team}"

    @property
    def is_expired(self):
        """Calculate if invitation is still valid or has expired."""
        validity_duration = timedelta(seconds=settings.INVITATION_VALIDITY_DURATION)
        return timezone.now() > (self.created_at + validity_duration)


def oidc_user_getter(validated_token):
    """
    Given a valid OIDC token , retrieve, create or update corresponding user/contact/email from db.

    The token is expected to have the following fields in payload:
        - sub
        - email
        - ...
    """
    try:
        user_id = validated_token[api_settings.USER_ID_CLAIM]
    except KeyError as exc:
        raise InvalidToken(
            _("Token contained no recognizable user identification")
        ) from exc

    try:
        email_param = {"email": validated_token["email"]}
    except KeyError:
        email_param = {}

    user = (
        User.objects.filter(identities__sub=user_id)
        .annotate(identity_email=models.F("identities__email"))
        .distinct()
        .first()
    )

    if user is None:
        user = User.objects.create(password="!", **email_param)  # noqa: S106
        Identity.objects.create(user=user, sub=user_id, **email_param)
    elif email_param and validated_token["email"] != user.identity_email:
        Identity.objects.filter(sub=user_id).update(email=validated_token["email"])

    return user
