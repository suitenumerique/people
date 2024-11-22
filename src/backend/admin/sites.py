"""Custom Django admin site for the People app."""

from django.conf import settings
from django.contrib import admin


class PeopleAdminSite(admin.AdminSite):
    """People custom admin site."""

    def each_context(self, request):
        """Add custom context to the admin site."""
        return super().each_context(request) | {
            "ADMIN_HEADER_BACKGROUND": settings.ADMIN_HEADER_BACKGROUND,
            "ADMIN_HEADER_COLOR": settings.ADMIN_HEADER_COLOR,
        }
