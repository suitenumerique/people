"""La Suite plugin application configuration."""

from core.plugins.base import BasePluginAppConfig


class LaSuitePluginConfig(BasePluginAppConfig):
    """Configuration for the La Suite plugin application."""

    name = "plugins.la_suite"
    verbose_name = "La Suite Plugin"
