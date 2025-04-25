"""Admin interface for SCIM importer models."""

from django.contrib import admin

from . import models


@admin.register(models.ScimClient)
class ScimClientAdmin(admin.ModelAdmin):
    """Admin for SCIM client model."""

    list_display = (
        "name",
        "is_active",
    )
    search_fields = ("name",)


@admin.register(models.ScimImportedUser)
class ScimImportedUserAdmin(admin.ModelAdmin):
    """Admin for SCIM imported user model."""

    list_display = ("scim_username", "client")
    list_filter = ("client",)
    list_select_related = ("client",)
    autocomplete_fields = ("user", "client", "scim_groups")


@admin.register(models.ScimImportedGroup)
class ScimImportedGroupAdmin(admin.ModelAdmin):
    """Admin for SCIM imported group model."""

    list_display = ("scim_display_name", "client")
    list_filter = ("client",)
    list_select_related = ("client",)
    autocomplete_fields = ("team", "client")
    search_fields = ("scim_display_name",)
