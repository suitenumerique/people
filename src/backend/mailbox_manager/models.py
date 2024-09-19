"""
Declare and configure the models for the People additional application : mailbox_manager
"""

from django.conf import settings
from django.core import exceptions, validators
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel

from mailbox_manager.enums import MailDomainRoleChoices, MailDomainStatusChoices


class MailDomain(BaseModel):
    """Domain names from which we will create email addresses (mailboxes)."""

    name = models.CharField(
        _("name"), max_length=150, null=False, blank=False, unique=True
    )
    slug = models.SlugField(null=False, blank=False, unique=True, max_length=80)
    status = models.CharField(
        max_length=10,
        default=MailDomainStatusChoices.PENDING,
        choices=MailDomainStatusChoices.choices,
    )

    class Meta:
        db_table = "people_mail_domain"
        verbose_name = _("Mail domain")
        verbose_name_plural = _("Mail domains")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Override save function to compute the slug."""
        self.slug = self.get_slug()
        return super().save(*args, **kwargs)

    def get_slug(self):
        """Compute slug value from name."""
        return slugify(self.name)

    def get_abilities(self, user):
        """
        Compute and return abilities for a given user on the domain.
        """
        is_owner_or_admin = False
        role = None

        if user.is_authenticated:
            try:
                role = self.accesses.filter(user=user).values("role")[0]["role"]
            except (MailDomainAccess.DoesNotExist, IndexError):
                role = None

        is_owner_or_admin = role in [
            MailDomainRoleChoices.OWNER,
            MailDomainRoleChoices.ADMIN,
        ]

        return {
            "get": bool(role),
            "patch": is_owner_or_admin,
            "put": is_owner_or_admin,
            "post": is_owner_or_admin,
            "delete": role == MailDomainRoleChoices.OWNER,
            "manage_accesses": is_owner_or_admin,
        }


class MailDomainAccess(BaseModel):
    """Allow to manage users' accesses to mail domains."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mail_domain_accesses",
        null=False,
        blank=False,
    )
    domain = models.ForeignKey(
        MailDomain,
        on_delete=models.CASCADE,
        related_name="accesses",
        null=False,
        blank=False,
    )
    role = models.CharField(
        max_length=20,
        choices=MailDomainRoleChoices.choices,
        default=MailDomainRoleChoices.VIEWER,
    )

    class Meta:
        db_table = "people_mail_domain_accesses"
        verbose_name = _("User/mail domain relation")
        verbose_name_plural = _("User/mail domain relations")
        unique_together = ("user", "domain")

    def __str__(self):
        return f"Access of user {self.user} on domain {self.domain}."


class Mailbox(BaseModel):
    """Mailboxes for users from mail domain."""

    first_name = models.CharField(max_length=200, blank=False)
    last_name = models.CharField(max_length=200, blank=False)
    local_part = models.CharField(
        _("local_part"),
        max_length=150,
        null=False,
        blank=False,
        validators=[validators.RegexValidator(regex="^[a-zA-Z0-9_.-]+$")],
    )
    domain = models.ForeignKey(
        MailDomain,
        on_delete=models.CASCADE,
        related_name="mail_domain",
        null=False,
        blank=False,
    )
    secondary_email = models.EmailField(
        _("secondary email address"), null=False, blank=False
    )

    class Meta:
        db_table = "people_mail_box"
        verbose_name = _("Mailbox")
        verbose_name_plural = _("Mailboxes")
        unique_together = ("local_part", "domain")

    def __str__(self):
        return f"{self.local_part!s}@{self.domain.name:s}"

    def clean(self):
        """
        Mailboxes can only be created on enabled domains.
        Also, mail-provisioning API credentials must be set for dimail to allow auth.
        """
        if self.domain.status != MailDomainStatusChoices.ENABLED:
            raise exceptions.ValidationError(
                "You can create mailbox only for a domain enabled"
            )

        # Won't be able to query user token if MAIL_PROVISIONING_API_CREDENTIALS are not set
        if not settings.MAIL_PROVISIONING_API_CREDENTIALS:
            raise exceptions.ValidationError(
                "Please configure MAIL_PROVISIONING_API_CREDENTIALS before creating any mailbox."
            )

    def save(self, *args, **kwargs):
        """
        Modification is forbidden for now.
        """
        self.full_clean()

        if self._state.adding:
            return super().save(*args, **kwargs)

        # Update is not implemented for now
        raise NotImplementedError()
