"""Helper functions to load and run organization plugins."""

from functools import lru_cache
from typing import List

from django.conf import settings
from django.utils.module_loading import import_string

from core.plugins.base import BaseOrganizationPlugin


@lru_cache(maxsize=None)
def get_organization_plugins() -> List[BaseOrganizationPlugin]:
    """
    Return a list of all organization plugins.
    While the plugins initialization does not depend on the request, we can cache the result.
    """
    return [
        import_string(plugin_path)() for plugin_path in settings.ORGANIZATION_PLUGINS
    ]


def organization_plugins_run_after_create(organization):
    """
    Run the after create method for all organization plugins.

    Each plugin will be called in the order they are listed in the settings.
    Each plugin is responsible to save changes if needed, this is not optimized
    but this could be easily improved later if needed.
    """
    for plugin_instance in get_organization_plugins():
        plugin_instance.run_after_create(organization)


def organization_plugins_run_after_grant_access(organization_access):
    """
    Run the after grant access method for all organization plugins.

    Each plugin will be called in the order they are listed in the settings.
    Each plugin is responsible to save changes if needed, this is not optimized
    but this could be easily improved later if needed.
    """
    for plugin_instance in get_organization_plugins():
        plugin_instance.run_after_grant_access(organization_access)
