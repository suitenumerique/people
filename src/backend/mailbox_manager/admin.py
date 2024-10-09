"""Admin classes and registrations for People's mailbox manager app."""

from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from requests import exceptions

from mailbox_manager import models
from mailbox_manager.utils.dimail import DimailAPIClient


@admin.action(description=_("Synchronise from dimail"))
def sync_mailboxes_from_dimail(modeladmin, request, queryset):  # pylint: disable=unused-argument
    """Admin action to synchronize existing mailboxes from dimail to our database."""
    client = DimailAPIClient()

    for domain in queryset:
        try:
            imported_mailboxes = client.synchronize_mailboxes_from_dimail(domain)
        except exceptions.HTTPError as err:
            messages.error(
                request,
                _(f"Synchronisation failed for {domain.name} with message: [{err}]"),
            )
        else:
            messages.success(
                request,
                _(
                    f"Synchronisation succeed for {domain.name}. "
                    f"Imported mailboxes: {', '.join(imported_mailboxes)}"
                ),
            )


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
    actions = (sync_mailboxes_from_dimail,)


@admin.register(models.Mailbox)
class MailboxAdmin(admin.ModelAdmin):
    """Admin for mailbox model."""

    list_display = ("__str__", "first_name", "last_name")


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
