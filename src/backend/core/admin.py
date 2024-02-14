"""Admin classes and registrations for People's core app."""
from django import forms
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _

from . import models


class IdentityFormSet(forms.BaseInlineFormSet):
    """
    Make the "is_main" field readonly when it is True so that declaring another identity
    works in the admin.
    """

    def add_fields(self, form, index):
        """Disable the "is_main" field when it is set to True"""
        super().add_fields(form, index)
        is_main_value = form.instance.is_main if form.instance else False
        form.fields["is_main"].disabled = is_main_value


class IdentityInline(admin.TabularInline):
    """Inline admin class for user identities."""

    fields = (
        "sub",
        "email",
        "is_main",
        "created_at",
        "updated_at",
    )
    formset = IdentityFormSet
    model = models.Identity
    extra = 0
    readonly_fields = ("email", "created_at", "sub", "updated_at")

    def has_add_permission(self, request, obj):
        """
        Identities are automatically created on successful OIDC logins.
        Disable creating identities via the admin.
        """
        return False


class TeamAccessInline(admin.TabularInline):
    """Inline admin class for team accesses."""

    extra = 0
    autocomplete_fields = ["user", "team"]
    model = models.TeamAccess
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
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    inlines = (IdentityInline, TeamAccessInline)
    list_display = (
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
    readonly_fields = ("id", "created_at", "updated_at")
    search_fields = ("id", "email", "identities__sub", "identities__email")


@admin.register(models.Team)
class TeamAdmin(admin.ModelAdmin):
    """Team admin interface declaration."""

    inlines = (TeamAccessInline,)
    list_display = (
        "name",
        "slug",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)
