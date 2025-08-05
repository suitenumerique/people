"""
Declare and configure the models for the scim_importer application
"""

from logging import getLogger

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_scim.models import (
    AbstractSCIMCommonAttributesMixin,
    AbstractSCIMGroupMixin,
    AbstractSCIMUserMixin,
)
from django_scim.models import (
    SCIMServiceProviderConfig as BaseSCIMServiceProviderConfig,
)

from core.models import BaseModel, Organization, Team

logger = getLogger(__name__)


class ScimClient(BaseModel):
    """SCIM client model."""

    # XXX: should allow OAuth2 connection for this model?
    name = models.CharField(_("name"), max_length=100, null=True, blank=True)
    token = models.CharField(  # XXX: should stored as a hash?
        _("Token"),
        max_length=100,
        unique=True,
        help_text=_("Authentication token for the SCIM client"),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Whether this client should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="scim_clients",
        verbose_name=_("organization"),
    )

    @property
    def is_authenticated(self):
        return True


# XXX: implement the case when a ScimImportedUser exists but not the user,
#      and the user is created via OIDC (update ScimImportedUser and create
#      Team (?) and add UserTeamAccess).
class ScimImportedUser(
    AbstractSCIMUserMixin,
    BaseModel,
):
    """SCIM imported user model."""

    client = models.ForeignKey(
        ScimClient,
        on_delete=models.CASCADE,
        related_name="users",
        verbose_name=_("client"),
    )

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scim_users",
    )

    first_name = models.CharField(
        _("first name"), max_length=100, null=True, blank=True
    )
    last_name = models.CharField(_("last name"), max_length=100, null=True, blank=True)
    email = models.EmailField(_("email address"), null=True, blank=True)

    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    scim_groups = models.ManyToManyField(
        "ScimImportedGroup",
        related_name="user_set",
    )

    class Meta:
        db_table = "people_scim_importer_user"
        verbose_name = _("SCIM imported user")
        verbose_name_plural = _("SCIM imported users")
        unique_together = (("client", "scim_username"),)

    @property
    def display_name(self):
        """Return the display name of the user."""
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        """Disable the django_scim save method."""
        super(AbstractSCIMCommonAttributesMixin, self).save(*args, **kwargs)
        # XXX: What should we do when a user is linked? at creation, at update?


class ScimImportedGroup(AbstractSCIMGroupMixin, BaseModel):
    """SCIM imported group model."""

    client = models.ForeignKey(
        ScimClient,
        on_delete=models.CASCADE,
        related_name="groups",
        verbose_name=_("client"),
    )

    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scim_groups",
    )

    class Meta:
        db_table = "people_scim_importer_group"
        verbose_name = _("SCIM imported group")
        verbose_name_plural = _("SCIM imported groups")

    def __str__(self):
        return self.scim_display_name or str(self.pk)

    def save(self, *args, **kwargs):
        """Disable the django_scim save method."""
        super(AbstractSCIMCommonAttributesMixin, self).save(*args, **kwargs)
        # XXX: What should we do when a team is linked? at creation, at update?
        #      Should we create the team if it does not exist? Only if there is at least one user
        #      we already know about (ScimImportedUser.user)?


class SCIMServiceProviderConfig(BaseSCIMServiceProviderConfig):
    """
    SCIM Service Provider Config for SCIM compatibility mode.

    Password is not supported in this mode.
    """

    def to_dict(self):
        return (
            super()
            .to_dict()
            .update(
                {
                    "changePassword": {
                        "supported": False,
                    },
                }
            )
        )
