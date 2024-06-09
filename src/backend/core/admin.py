"""Admin classes and registrations for People's core app."""

from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _

from . import models


class TeamAccessInline(admin.TabularInline):
    """Inline admin class for team accesses."""

    extra = 0
    autocomplete_fields = ["user", "team"]
    model = models.TeamAccess
    readonly_fields = ("created_at", "updated_at")


class TeamWebhookInline(admin.TabularInline):
    """Inline admin class for team webhooks."""

    extra = 0
    autocomplete_fields = ["team"]
    model = models.TeamWebhook
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.User)
class UserAdmin(auth_admin.UserAdmin):
    """Admin class for the User model"""

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "sub",
                    "password",
                )
            },
        ),
        (_("Personal info"), {"fields": ("email", "language", "timezone")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_device",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("sub", "email", "password1", "password2"),
            },
        ),
    )
    inlines = (TeamAccessInline,)
    list_display = (
        "sub",
        "email",
        "created_at",
        "updated_at",
        "is_active",
        "is_device",
        "is_staff",
        "is_superuser",
    )
    list_filter = ("is_staff", "is_superuser", "is_device", "is_active")
    ordering = ("is_active", "-is_superuser", "-is_staff", "-is_device", "-updated_at")
    readonly_fields = ["id", "created_at", "updated_at"]
    search_fields = ("id", "email", "sub")

    def get_readonly_fields(self, request, obj=None):
        """The sub should only be editable for a create, not for updates."""
        if obj:
            return self.readonly_fields + ["sub"]
        return self.readonly_fields


@admin.register(models.Team)
class TeamAdmin(admin.ModelAdmin):
    """Team admin interface declaration."""

    inlines = (TeamAccessInline, TeamWebhookInline)
    list_display = (
        "name",
        "slug",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)


@admin.register(models.Invitation)
class InvitationAdmin(admin.ModelAdmin):
    """Admin interface to handle invitations."""

    fields = (
        "email",
        "team",
        "role",
        "created_at",
        "issuer",
    )
    readonly_fields = (
        "created_at",
        "is_expired",
        "issuer",
    )
    list_display = (
        "email",
        "team",
        "created_at",
        "is_expired",
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            # all fields read only = disable update
            return self.fields
        return self.readonly_fields

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """Custom edit form. Remove 'save' buttons."""
        extra_context = extra_context or {}
        extra_context["show_save_and_continue"] = False
        extra_context["show_save"] = False
        extra_context["show_save_and_add_another"] = False
        return super().change_view(request, object_id, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        obj.issuer = request.user
        obj.save()
