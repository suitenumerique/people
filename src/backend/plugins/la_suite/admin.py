"""Admin for the la suite plugin."""

from django.contrib import admin

from .models import OrganizationOneTimeToken


class OrganizationOneTimeTokenAdmin(admin.ModelAdmin):
    """Admin for the organization one-time token."""

    list_display = ("key", "organization", "used_at", "enabled")
    search_fields = ("key", "organization__name")
    list_filter = ("enabled", "used_at")
    readonly_fields = ("key", "created_at", "updated_at")


admin.site.register(OrganizationOneTimeToken, OrganizationOneTimeTokenAdmin)
