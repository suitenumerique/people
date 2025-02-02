# pylint: disable=too-many-ancestors
"""
Application enums declaration
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class MailDomainRoleChoices(models.TextChoices):
    """Defines the possible roles a user can have to access to a mail domain."""

    VIEWER = "viewer", _("Viewer")
    ADMIN = "administrator", _("Administrator")
    OWNER = "owner", _("Owner")


class MailDomainStatusChoices(models.TextChoices):
    """Defines the possible statuses in which a mail domain can be."""

    PENDING = "pending", _("Pending")
    ENABLED = "enabled", _("Enabled")
    FAILED = "failed", _("Failed")
    DISABLED = "disabled", _("Disabled")
    ACTION_REQUIRED = "action_required", _("Action required")


class MailboxStatusChoices(models.TextChoices):
    """Lists the possible statuses in which a mailbox can be."""

    PENDING = "pending", _("Pending")
    ENABLED = "enabled", _("Enabled")
    FAILED = "failed", _("Failed")
    DISABLED = "disabled", _("Disabled")
