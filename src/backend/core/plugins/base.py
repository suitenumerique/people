"""Base Django Application Configuration for plugins."""


class BasePluginAppConfigMixIn:
    """
    Configuration for the La Suite plugin application.

    We cannot use the `AppConfig` class directly because it is not compatible with
    the Django way to discover default AppConfig (see `AppConfig.create`).
    We use a mixin then, to be able to list plugins using `plugins.la_suite` instead
    of `plugins.la_suite.apps.LaSuitePluginConfig`.

    Another way would be to force `default` attribute on plugin AppConfig.
    """

    def ready(self):
        """
        Initialize the hooks registry when the application is ready.
        This is called by Django when the application is loaded.
        """
        from .registry import registry  # pylint: disable=import-outside-toplevel

        registry.register_app(self.name)  # pylint: disable=no-member
