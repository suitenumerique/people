"""Admin classes and registrations for People's core app."""

from django.contrib import admin, messages
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _

from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from mailbox_manager.admin import MailDomainAccessInline

from . import models
from .plugins.registry import registry as plugin_hooks_registry


class TeamAccessInline(admin.TabularInline):
    """Inline admin class for team accesses."""

    extra = 0
    autocomplete_fields = ["user", "team"]
    model = models.TeamAccess
    readonly_fields = ("created_at", "updated_at")


class OrganizationAccessInline(admin.TabularInline):
    """Inline admin class for organization accesses."""

    autocomplete_fields = ["user", "organization"]
    extra = 0
    model = models.OrganizationAccess
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

    autocomplete_fields = ["organization"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "sub",
                    "password",
                    "organization",
                )
            },
        ),
        (
            _("Personal info"),
            {
                "fields": (
                    "name",
                    "email",
                    "language",
                    "timezone",
                )
            },
        ),
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
    inlines = (TeamAccessInline, MailDomainAccessInline, OrganizationAccessInline)
    list_display = (
        "get_user",
        "organization",
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
    search_fields = ("id", "email", "sub", "name")

    def get_readonly_fields(self, request, obj=None):
        """The sub should only be editable for a create, not for updates."""
        if obj:
            return self.readonly_fields + ["sub"]
        return self.readonly_fields

    def get_user(self, obj):
        """Provide a nice display for user"""
        return (
            obj.name if obj.name else (obj.email if obj.email else f"[sub] {obj.sub}")
        )

    get_user.short_description = _("User")


class TeamServiceProviderInline(admin.TabularInline):
    """Inline admin class for service providers."""

    can_delete = False
    model = models.Team.service_providers.through
    extra = 0


@admin.register(models.Team)
class TeamAdmin(TreeAdmin):
    """Team admin interface declaration."""

    form = movenodeform_factory(models.Team)
    inlines = (TeamAccessInline, TeamWebhookInline, TeamServiceProviderInline)
    exclude = ("service_providers",)  # Handled by the inline
    list_display = (
        "name",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)
    readonly_fields = ("path", "depth", "numchild")


@admin.register(models.TeamAccess)
class TeamAccessAdmin(admin.ModelAdmin):
    """Team access admin interface declaration."""

    list_display = (
        "user",
        "team",
        "role",
        "created_at",
        "updated_at",
    )


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
        """Mark all fields read only, i.e. disable update."""
        if obj:
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
        """Fill in current logged-in user as issuer."""
        obj.issuer = request.user
        obj.save()


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    """Contact admin interface declaration."""

    list_display = (
        "full_name",
        "owner",
        "override",
    )


class OrganizationServiceProviderInline(admin.TabularInline):
    """Inline admin class for service providers."""

    can_delete = False
    model = models.Organization.service_providers.through
    extra = 0


@admin.action(description=_("Run post creation plugins"), permissions=["change"])
def run_post_creation_plugins(modeladmin, request, queryset):  # pylint: disable=unused-argument
    """Run the post creation plugins for the selected organizations."""
    for organization in queryset:
        plugin_hooks_registry.execute_hook("organization_created", organization)

    messages.success(
        request,
        _("Post creation plugins have been run for the selected organizations."),
    )


@admin.register(models.Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin interface for organizations."""

    actions = [run_post_creation_plugins]
    list_display = (
        "name",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)
    inlines = (OrganizationAccessInline, OrganizationServiceProviderInline)
    exclude = ("service_providers",)  # Handled by the inline

    def get_actions(self, request):
        """Adapt actions list to the context."""
        actions = super().get_actions(request)
        if not plugin_hooks_registry.get_callbacks("organization_created"):
            actions.pop("run_post_creation_plugins", None)
        return actions


@admin.register(models.OrganizationAccess)
class OrganizationAccessAdmin(admin.ModelAdmin):
    """Organization access admin interface declaration."""

    autocomplete_fields = ("user", "organization")
    list_display = (
        "user",
        "organization",
        "role",
        "created_at",
        "updated_at",
    )


@admin.register(models.ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    """Admin interface for service providers."""

    list_display = (
        "name",
        "audience_id",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "audience_id")
    readonly_fields = ("created_at", "updated_at")
