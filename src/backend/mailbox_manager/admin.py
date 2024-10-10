"""Admin classes and registrations for People's mailbox manager app."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from mailbox_manager import models


class UserMailDomainAccessInline(admin.TabularInline):
    """Inline admin class for mail domain accesses."""

    extra = 0
    model = models.MailDomainAccess
    readonly_fields = ("created_at", "updated_at", "domain", "user")


@admin.register(models.MailDomain)
class MailDomainAdmin(admin.ModelAdmin):
    """Mail domain admin interface declaration."""

    list_display = (
        "name",
        "created_at",
        "updated_at",
        "slug",
        "status",
    )
    search_fields = ("name",)
    readonly_fields = ["created_at", "slug"]
    inlines = (UserMailDomainAccessInline,)


@admin.register(models.MailDomainAccess)
class MailDomainAccessAdmin(admin.ModelAdmin):
    """Admin for mail domain accesses model."""

    list_display = (
        "user",
        "domain",
        "role",
        "created_at",
        "updated_at",
    )


class MailDomainAccessInline(admin.TabularInline):
    """Inline admin class for mail domain accesses."""

    extra = 0
    autocomplete_fields = ["user", "domain"]
    model = models.MailDomainAccess
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.Mailbox)
class MailboxAdmin(admin.ModelAdmin):
    """Admin for mailbox model."""

    list_display = ("__str__", "first_name", "last_name")
