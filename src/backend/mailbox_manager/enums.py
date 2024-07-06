"""
Application enums declaration
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class MailDomainStatusChoices(models.TextChoices):
    """Defines the possible statuses in which a mail domain can be."""

    PENDING = "pending", _("Pending")
    ENABLED = "enabled", _("Enabled")
    FAILED = "failed", _("Failed")
    DISABLED = "disabled", _("Disabled")
