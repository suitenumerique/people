"""URLs for plugins"""

from django.conf import settings
from django.urls import include, path

plugins_urlpatterns = []

# Try to import and include URLs from each installed plugin
for app in settings.INSTALLED_PLUGINS:
    try:
        plugins_urlpatterns.append(path("", include(f"{app}.urls")))
    except ImportError, AttributeError:
        # Skip if app doesn't have urls.py
        continue

urlpatterns = plugins_urlpatterns
