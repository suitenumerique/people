"""La Suite plugin application configuration."""

from django.apps import AppConfig

from core.plugins.base import BasePluginAppConfigMixIn


class LaSuitePluginConfig(BasePluginAppConfigMixIn, AppConfig):
    """Configuration for the La Suite plugin application."""

    name = "plugins.la_suite"
    verbose_name = "La Suite Plugin"
