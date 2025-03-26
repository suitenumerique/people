"""Base Django Application Configuration for plugins."""

from django.apps import AppConfig


class BasePluginAppConfig(AppConfig):
    """Configuration for the La Suite plugin application."""

    def ready(self):
        """
        Initialize the hooks registry when the application is ready.
        This is called by Django when the application is loaded.
        """
        from .registry import registry  # pylint: disable=import-outside-toplevel

        registry.register_app(self.name)
