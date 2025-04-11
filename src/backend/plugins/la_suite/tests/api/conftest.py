"""Fixtures for the la suite tests."""

from importlib import import_module, reload

from django.urls import clear_url_caches, set_urlconf

import pytest


@pytest.fixture(name="plugin_urls")
def reload_urlconf(settings):
    """Reload the urlconf before"""
    settings.INSTALLED_PLUGINS = ["plugins.la_suite"]
    reload(import_module("core.plugins.urls"))
    reload(import_module(settings.ROOT_URLCONF))

    clear_url_caches()
    set_urlconf(None)

    yield

    settings.INSTALLED_PLUGINS = []
    reload(import_module("core.plugins.urls"))
    reload(import_module(settings.ROOT_URLCONF))

    clear_url_caches()
    set_urlconf(None)
