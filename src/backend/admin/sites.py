"""Custom Django admin site for the People app."""

from django.conf import settings
from django.contrib import admin
from django.urls import path

from .registry import view_registry


class PeopleAdminSite(admin.AdminSite):
    """People custom admin site."""

    def each_context(self, request):
        """Add custom context to the admin site."""
        return super().each_context(request) | {
            "ADMIN_HEADER_BACKGROUND": settings.ADMIN_HEADER_BACKGROUND,
            "ADMIN_HEADER_COLOR": settings.ADMIN_HEADER_COLOR,
        }

    def get_urls(self):
        """Add custom URLs to the admin site."""
        urls = super().get_urls()

        # Add all registered views from the registry
        selftest_urls = [
            path(
                f"selftest/{view_info['path']}",
                self.admin_view(view_info["view_class"].as_view()),
                name=f"selftest_{view_info['name']}",
            )
            for view_info in view_registry.get_views()
        ]

        return selftest_urls + urls
