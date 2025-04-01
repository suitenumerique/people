"""URLs for plugins"""

from django.apps import config
from django.conf import settings
from django.urls import include, path

import logging
logger = logging.getLogger(__name__)
logger.warning("_"*100)
logger.warning("core.plugins.urls")
logger.warning("settings.INSTALLED_PLUGINS %s", settings.INSTALLED_PLUGINS)
logger.warning("settings.INSTALLED_APPS %s", settings.INSTALLED_APPS)

plugins_urlpatterns = []
installed_plugins_configs = [
    config.AppConfig.create(plugin) for plugin in settings.INSTALLED_PLUGINS
]
installed_plugins = [app_config.name for app_config in installed_plugins_configs]

# Try to import and include URLs from each installed plugin
for app in installed_plugins:
    try:
        plugins_urlpatterns.append(path("", include(f"{app}.urls")))
    except (ImportError, AttributeError):
        # Skip if app doesn't have urls.py
        continue

logger.warning("plugins_urlpatterns %s", plugins_urlpatterns)
logger.warning("_"*100)
urlpatterns = plugins_urlpatterns
