"""
Declare and configure the models for the People additional application : mailbox_manager
"""

import logging
import smtplib

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.sites.models import Site
from django.core import exceptions, mail, validators
from django.db import models
from django.template.loader import render_to_string
from django.utils.text import slugify
from django.utils.translation import get_language, gettext, override
from django.utils.translation import gettext_lazy as _

from core.models import BaseInvitation, BaseModel, Organization, User

from mailbox_manager.enums import (
    MailboxStatusChoices,
    MailDomainRoleChoices,
    MailDomainStatusChoices,
)

logger = logging.getLogger(__name__)


STATUS_NOTIFICATION_MAILS = {
    # new status domain: (mail subject, mail template html, mail template text)
    MailDomainStatusChoices.ENABLED: (
        _("[La Suite] Your domain is ready"),
        "mail/html/maildomain_enabled.html",
        "mail/text/maildomain_enabled.txt",
    ),
    MailDomainStatusChoices.ACTION_REQUIRED: (
        _("[La Suite] Your domain requires action"),
        "mail/html/maildomain_action_required.html",
        "mail/text/maildomain_action_required.txt",
    ),
    MailDomainStatusChoices.FAILED: (
        _("[La Suite] Your domain has failed"),
        "mail/html/maildomain_failed.html",
        "mail/text/maildomain_failed.txt",
    ),
}


class MailDomain(BaseModel):
    """Domain names from which we will create email addresses (mailboxes)."""

    name = models.CharField(
        _("name"), max_length=150, null=False, blank=False, unique=True
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="mail_domains",
        null=True,
        blank=True,
    )
    slug = models.SlugField(null=False, blank=False, unique=True, max_length=80)
    status = models.CharField(
        max_length=20,
        default=MailDomainStatusChoices.PENDING,
        choices=MailDomainStatusChoices.choices,
    )
    support_email = models.EmailField(_("support email"), null=False, blank=False)
    last_check_details = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_("last check details"),
        help_text=_("A JSON object containing the last health check details"),
    )
    expected_config = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_("expected config"),
        help_text=_("A JSON object containing the expected config"),
    )

    class Meta:
        db_table = "people_mail_domain"
        verbose_name = _("Mail domain")
        verbose_name_plural = _("Mail domains")
        ordering = ["-created_at"]

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

    def is_identity_provider_ready(self) -> bool:
        """
        Check if the identity provider is ready to manage the domain.
        """
        return (
            bool(self.organization) and self.status == MailDomainStatusChoices.ENABLED
        )

    def notify_status_change(self, recipients=None, language=None):
        """
        Notify the support team that the domain status has changed.
        """
        subject, template_html, template_text = STATUS_NOTIFICATION_MAILS.get(
            self.status, (None, None, None)
        )
        if not subject:
            return
        context = {
            "title": subject,
            "domain_name": self.name,
            "manage_domain_url": (
                f"{Site.objects.get_current().domain}/mail-domains/{self.slug}/"
            ),
        }
        try:
            with override(language or get_language()):
                mail.send_mail(
                    subject,
                    render_to_string(template_text, context),
                    settings.EMAIL_FROM,
                    recipients or [self.support_email],
                    html_message=render_to_string(template_html, context),
                    fail_silently=False,
                )
        except smtplib.SMTPException as exception:
            logger.error(
                "Notification email to %s was not sent: %s",
                self.support_email,
                exception,
            )
        else:
            logger.info(
                "Information about domain %s sent to %s.",
                self.name,
                self.support_email,
            )


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
        ordering = ["-created_at"]

    def __str__(self):
        return f"Access of user {self.user} on domain {self.domain}."

    def get_can_set_role_to(self, user):
        """Return roles available to set"""
        if not user.is_authenticated:
            return []
        roles = list(MailDomainRoleChoices)
        authenticated_user_role = None

        # get role of authenticated user
        if hasattr(self, "user_role"):
            authenticated_user_role = self.user_role
        else:
            try:
                authenticated_user_role = user.mail_domain_accesses.get(
                    domain=self.domain
                ).role
            except (MailDomainAccess.DoesNotExist, IndexError):
                return []

        # only an owner can set an owner role
        if authenticated_user_role != MailDomainRoleChoices.OWNER:
            roles.remove(MailDomainRoleChoices.OWNER)

        # if the user authenticated is a viewer, they can't modify role
        # and only an owner can change role of an owner
        if authenticated_user_role == MailDomainRoleChoices.VIEWER or (
            authenticated_user_role != MailDomainRoleChoices.OWNER
            and self.role == MailDomainRoleChoices.OWNER
        ):
            return []
        # we only want to return other roles available to change,
        # so we remove the current role of current access.
        roles.remove(self.role)
        return sorted(roles)

    def get_abilities(self, user):
        """
        Compute and return abilities for a given user on the domain access.
        """
        role = None

        if user.is_authenticated:
            try:
                role = user.mail_domain_accesses.filter(domain=self.domain).get().role
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
            "delete": is_owner_or_admin,
        }


class Mailbox(AbstractBaseUser, BaseModel):
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
        related_name="mailboxes",
        null=False,
        blank=False,
    )
    secondary_email = models.EmailField(
        _("secondary email address"), null=True, blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=MailboxStatusChoices.choices,
        default=MailboxStatusChoices.PENDING,
    )

    # Store the denormalized email address to allow Django admin to work (USERNAME_FIELD)
    # This field *must* not be used for authentication (or anything sensitive),
    # use the `local_part` and `domain__name` fields
    dn_email = models.EmailField(_("email"), blank=True, unique=True, editable=False)

    USERNAME_FIELD = "dn_email"

    class Meta:
        db_table = "people_mail_box"
        verbose_name = _("Mailbox")
        verbose_name_plural = _("Mailboxes")
        constraints = [
            models.UniqueConstraint(
                fields=["local_part", "domain"], name="unique_username"
            ),
            models.UniqueConstraint(
                fields=["first_name", "last_name", "domain"],
                name="unique_ox_display_name",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.local_part!s}@{self.domain.name:s}"

    def clean(self):
        """
        Mail-provisioning API credentials must be set for dimail to allow auth.
        """
        # Won't be able to query user token if MAIL_PROVISIONING_API_CREDENTIALS are not set
        if not settings.MAIL_PROVISIONING_API_CREDENTIALS:
            raise exceptions.ValidationError(
                "Please configure MAIL_PROVISIONING_API_CREDENTIALS before creating any mailbox."
            )

    def save(self, *args, **kwargs):
        """
        Override save function to not allow to create or update mailbox of a disabled domain.
        """
        self.full_clean()
        self.dn_email = self.get_email()

        if self.domain.status == MailDomainStatusChoices.DISABLED:
            raise exceptions.ValidationError(
                _("You can't create or update a mailbox for a disabled domain.")
            )
        return super().save(*args, **kwargs)

    @property
    def is_active(self):
        """Return True if the mailbox is enabled."""
        return self.status == MailboxStatusChoices.ENABLED

    def get_email(self):
        """Return the email address of the mailbox."""
        return f"{self.local_part}@{self.domain.name}"

    def get_abilities(self, user):
        """Compute and return abilities for a given user."""
        role = user.mail_domain_accesses.get(domain=self.domain).role

        is_owner_or_admin = role in [
            MailDomainRoleChoices.OWNER,
            MailDomainRoleChoices.ADMIN,
        ]

        is_self = self.get_email() == user.email

        return {
            "get": bool(role),
            "post": is_owner_or_admin,
            "patch": is_owner_or_admin or is_self,
            "put": is_owner_or_admin or is_self,
            "delete": False,
        }


class MailDomainInvitation(BaseInvitation):
    """User invitation to mail domains."""

    issuer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="mail_domain_invitations",
    )
    domain = models.ForeignKey(
        MailDomain,
        on_delete=models.CASCADE,
        related_name="mail_domain_invitations",
    )
    role = models.CharField(
        max_length=20,
        choices=MailDomainRoleChoices.choices,
        default=MailDomainRoleChoices.VIEWER,
    )

    MAIL_TEMPLATE_HTML = "mail/html/maildomain_invitation.html"
    MAIL_TEMPLATE_TXT = "mail/text/maildomain_invitation.txt"

    class Meta:
        db_table = "people_mail_domain_invitation"
        verbose_name = _("Mail domain invitation")
        verbose_name_plural = _("Mail domain invitations")
        constraints = [
            models.UniqueConstraint(
                fields=["email", "domain"], name="email_and_domain_unique_together"
            )
        ]

    def __str__(self):
        return f"{self.email} invited to {self.domain}"

    def _get_mail_subject(self):
        """Get the subject of the invitation."""
        return gettext("[La Suite] You have been invited to join La Régie")

    def _get_mail_context(self):
        """Get the template variables for the invitation."""
        return {
            **super()._get_mail_context(),
            "domain": self.domain.name,
            "role": self.get_role_display(),
        }

    def get_abilities(self, user):
        """Compute and return abilities for a given user."""
        can_delete = False
        role = None

        if user.is_authenticated:
            try:
                role = self.user_role
            except AttributeError:
                try:
                    role = self.domain.accesses.filter(user=user).values("role")[0][
                        "role"
                    ]
                except (self._meta.model.DoesNotExist, IndexError):
                    role = None

            can_delete = role in [
                MailDomainRoleChoices.OWNER,
                MailDomainRoleChoices.ADMIN,
            ]

        return {
            "delete": can_delete,
            "get": bool(role),
            "patch": False,
            "put": False,
        }
