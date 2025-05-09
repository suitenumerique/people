# pylint: disable=too-many-ancestors
"""
Core application enums declaration
"""

from django.conf import global_settings, settings
from django.db import models
from django.utils.translation import gettext_lazy as _

# Django sets `LANGUAGES` by default with all supported languages. We can use it for
# the choice of languages which should not be limited to the few languages active in
# the app.
# pylint: disable=no-member
ALL_LANGUAGES = getattr(
    settings,
    "ALL_LANGUAGES",
    [(language, _(name)) for language, name in global_settings.LANGUAGES],
)


class WebhookStatusChoices(models.TextChoices):
    """Defines the possible statuses in which a webhook can be."""

    FAILURE = "failure", _("Failure")
    PENDING = "pending", _("Pending")
    SUCCESS = "success", _("Success")


class WebhookProtocolChoices(models.TextChoices):
    """Defines the possible protocols of webhook."""

    SCIM = "scim"
    MATRIX = "matrix"
