"""Admin classes and registrations for People's mailbox manager app."""

from django.contrib import admin, messages
from django.utils.html import format_html_join, mark_safe
from django.utils.translation import gettext_lazy as _

from requests import exceptions

from mailbox_manager import enums, models
from mailbox_manager.utils.dimail import DimailAPIClient

# Prevent Ruff complaining about mark_safe below
# ruff: noqa: S308


@admin.action(description=_("Synchronise from dimail"))
def sync_mailboxes_from_dimail(modeladmin, request, queryset):  # pylint: disable=unused-argument
    """Admin action to synchronize existing mailboxes from dimail to our database.
    Only works on enabled domains."""
    excluded_domains = []

    client = DimailAPIClient()

    for domain in queryset:
        if domain.status != enums.MailDomainStatusChoices.ENABLED:
            excluded_domains.append(domain.name)
            continue

        try:
            imported_mailboxes = client.import_mailboxes(domain)
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
    if excluded_domains:
        messages.warning(
            request,
            _(
                f"Sync require enabled domains. Excluded domains: {', '.join(excluded_domains)}"
            ),
        )


@admin.action(description=_("Check and update status from dimail"))
def fetch_domain_status_from_dimail(modeladmin, request, queryset):  # pylint: disable=unused-argument
    """Admin action to check domain health with dimail and update domain status."""
    client = DimailAPIClient()
    domains_updated, excluded_domains, msg_error = [], [], []
    success = False
    for domain in queryset:
        # do not check disabled domains
        if domain.status == enums.MailDomainStatusChoices.DISABLED:
            excluded_domains.append(domain.name)
            continue

        old_status = domain.status
        try:
            response = client.fetch_domain_status(domain)
        except exceptions.HTTPError as err:
            msg_error.append(_(f"- {domain.name} with message: '{err}'"))
        else:
            success = True
            # temporary (or not?) display content of the dimail response to debug broken state
            if domain.status == enums.MailDomainStatusChoices.FAILED:
                messages.info(request, response.json())
            if old_status != domain.status:
                domains_updated.append(domain.name)

    if success:
        msg_success = [
            _("Check domains done with success."),
            _(f"Domains updated: {', '.join(domains_updated)}")
            if domains_updated
            else _("No domain updated."),
        ]
        messages.success(
            request,
            format_html_join(mark_safe("<br> "), "{}", ([str(m)] for m in msg_success)),
        )
    if msg_error:
        msg_error.insert(0, _("Check domain failed for:"))
        messages.error(
            request,
            format_html_join(mark_safe("<br> "), "{}", ([str(m)] for m in msg_error)),
        )
    if excluded_domains:
        messages.warning(
            request,
            _(
                f"Domains disabled are excluded from check: {', '.join(excluded_domains)}"
            ),
        )


class UserMailDomainAccessInline(admin.TabularInline):
    """Inline admin class for mail domain accesses."""

    extra = 0
    model = models.MailDomainAccess
    readonly_fields = ("created_at", "updated_at", "domain")


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
    list_filter = ("status",)
    inlines = (UserMailDomainAccessInline,)
    actions = (sync_mailboxes_from_dimail, fetch_domain_status_from_dimail)


@admin.register(models.Mailbox)
class MailboxAdmin(admin.ModelAdmin):
    """Admin for mailbox model."""

    list_display = ("__str__", "domain", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("local_part", "domain__name")
    readonly_fields = ["updated_at", "local_part", "domain"]


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
