"""SCIM Importer application"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ScimImporterConfig(AppConfig):
    """Configuration class for the scim_importer app."""

    name = "scim_importer"
    app_label = "scim_importer"
    verbose_name = _("SCIM Importer")
