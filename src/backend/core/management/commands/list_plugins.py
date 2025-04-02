"""Management command to list all plugins and their hooks."""

from django.conf import settings
from django.core.management.base import BaseCommand

from core.plugins.registry import registry


class Command(BaseCommand):
    """Management command to list all plugins and their hooks."""

    help = "List all plugins and their hooks"

    def handle(self, *args, **options):
        """Print plugin information."""
        self.stdout.write(self.style.NOTICE("# Listing plugins\n"))
        for plugin_app in settings.INSTALLED_PLUGINS:
            self.stdout.write(self.style.NOTICE(f" - {plugin_app}\n"))

        self.stdout.write(self.style.NOTICE("# Listing loaded hooks\n"))
        for hook_name, callbacks in registry.get_registered_hooks():
            self.stdout.write(self.style.NOTICE(f" - {hook_name}: {callbacks}\n"))
