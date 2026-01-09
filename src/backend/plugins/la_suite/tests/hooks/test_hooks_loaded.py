"""Test module to check all application hooks are loaded."""

from core.plugins.registry import registry

from plugins.la_suite.apps import LaSuitePluginConfig


def test_hooks_loaded():
    """Test to check all application hooks are loaded."""
    _original_hooks = dict(registry._hooks.items())  # pylint: disable=protected-access
    _original_registered_apps = set(registry._registered_apps)  # pylint: disable=protected-access

    registry.reset()

    assert registry.get_callbacks("organization_created") == []
    assert registry.get_callbacks("organization_access_granted") == []

    # Force the application to run "ready" method
    LaSuitePluginConfig(
        app_name="plugins.la_suite", app_module=__import__("plugins.la_suite")
    ).ready()

    # Check that the hooks are loaded
    organization_created_hook_names = [
        callback.__name__ for callback in registry.get_callbacks("organization_created")
    ]
    assert organization_created_hook_names == [
        "get_organization_name_and_metadata_from_siret_hook",
    ]

    # cleanup the hooks
    registry._hooks = _original_hooks  # pylint: disable=protected-access
    registry._registered_apps = _original_registered_apps  # pylint: disable=protected-access
