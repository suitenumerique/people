"""Admin classes and registrations for People's mailbox manager app."""

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html_join, mark_safe
from django.utils.translation import gettext_lazy as _

from requests import exceptions

from mailbox_manager import enums, models
from mailbox_manager.utils.dimail import DimailAPIClient


@admin.action(description=_("Import emails from dimail"))
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
                _("Synchronisation failed for %(domain)s with message: %(err)s")
                % {"domain": domain.name, "err": err},
            )
        else:
            messages.success(
                request,
                _(
                    "Synchronisation succeed for %(domain)s. Imported mailboxes: %(mailboxes)s"
                )
                % {"domain": domain.name, "mailboxes": ", ".join(imported_mailboxes)},
            )
    if excluded_domains:
        messages.warning(
            request,
            _("Sync require enabled domains. Excluded domains: %(domains)s")
            % {"domains": ", ".join(excluded_domains)},
        )


@admin.action(description=_("Import aliases from dimail"))
def sync_aliases_from_dimail(modeladmin, request, queryset):  # pylint: disable=unused-argument
    """
    Admin action to import existing aliases from dimail.
    Checks alias is not a duplicate and that usernames don't clash with existing mailboxes.
    """
    excluded_domains = []

    client = DimailAPIClient()

    for domain in queryset:
        if domain.status != enums.MailDomainStatusChoices.ENABLED:
            excluded_domains.append(domain.name)
            continue

        try:
            imported_aliases = client.import_aliases(domain)
        except exceptions.HTTPError as err:
            messages.error(
                request,
                _("Synchronisation failed for %(domain)s with message: %(err)s")
                % {"domain": domain.name, "err": err},
            )
        else:
            messages.success(
                request,
                _(
                    "Synchronisation succeed for %(domain)s. %(imported_aliases)\
imported aliases: %(mailboxes)s"
                )
                % {
                    "domain": domain.name,
                    "number_imported": len(imported_aliases),
                    "mailboxes": ", ".join(imported_aliases),
                },
            )
    if excluded_domains:
        messages.warning(
            request,
            _("Sync require enabled domains. Excluded domains: %(domains)s")
            % {"domains": ", ".join(excluded_domains)},
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
            msg_error.append(
                _("- %(domain)s with message: %(err)s")
                % {"domain": domain.name, "err": err},
            )
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
            _("Domains updated: %(domains)s") % {"domains": ", ".join(domains_updated)}
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
            _("Domains disabled are excluded from check: %(domains)s")
            % {"domains": ", ".join(excluded_domains)},
        )


@admin.action(description=_("Fetch domain expected config from dimail"))
def fetch_domain_expected_config_from_dimail(modeladmin, request, queryset):  # pylint: disable=unused-argument
    """Admin action to fetch domain expected config from dimail."""
    client = DimailAPIClient()
    excluded_domains = []
    for domain in queryset:
        # do not check disabled domains
        if domain.status == enums.MailDomainStatusChoices.DISABLED:
            excluded_domains.append(domain.name)
            continue
        response = client.fetch_domain_expected_config(domain)
        if response:
            messages.success(
                request,
                _("Domain expected config fetched with success for %(domain)s.")
                % {"domain": domain.name},
            )
        else:
            messages.error(
                request,
                _("Failed to fetch domain expected config for %(domain)s.")
                % {"domain": domain.name},
            )
    if excluded_domains:
        messages.warning(
            request,
            _("Domains disabled are excluded from fetch: %(domains)s")
            % {"domains": ", ".join(excluded_domains)},
        )


@admin.action(description=_("Send pending mailboxes to dimail"))
def send_pending_mailboxes(modeladmin, request, queryset):  # pylint: disable=unused-argument
    """Send pending mailboxes"""
    client = DimailAPIClient()

    excluded_domains = []
    for domain in queryset:
        # do not check disabled domains
        if domain.status != enums.MailDomainStatusChoices.ENABLED:
            excluded_domains.append(domain.name)
            continue

        results = client.send_pending_mailboxes(domain)
        if failed_mailboxes := results["failed_mailboxes"]:
            messages.error(
                request,
                _("Failed to send the following mailboxes : %(mailboxes)s.")
                % {"mailboxes": ", ".join(failed_mailboxes)},
            )
        else:
            messages.success(
                request,
                _("Pending mailboxes successfully sent for %(domain)s.")
                % {"domain": domain.name},
            )
    if excluded_domains:
        messages.warning(
            request,
            _("Domains disabled are excluded from : %(domains)s")
            % {"domains": ", ".join(excluded_domains)},
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
        "organization",
        "created_at",
        "updated_at",
        "slug",
        "status",
    )
    search_fields = ("name", "organization__name")
    readonly_fields = ["created_at", "slug"]
    list_filter = ("status",)
    inlines = (UserMailDomainAccessInline,)
    actions = (
        sync_mailboxes_from_dimail,
        fetch_domain_status_from_dimail,
        fetch_domain_expected_config_from_dimail,
        send_pending_mailboxes,
    )
    autocomplete_fields = ["organization"]


@admin.register(models.Mailbox)
class MailboxAdmin(UserAdmin):
    """Admin for mailbox model."""

    list_display = ("__str__", "domain", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("local_part", "domain__name", "first_name", "last_name")
    readonly_fields = ["updated_at"]

    fieldsets = None
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "first_name",
                    "last_name",
                    "local_part",
                    "domain",
                    "secondary_email",
                    "status",
                    "usable_password",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    ordering = ("local_part", "domain")
    filter_horizontal = ()


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


@admin.register(models.MailDomainInvitation)
class MailDomainInvitationAdmin(admin.ModelAdmin):
    """Admin for mail domain invitation model."""

    list_display = ("email", "domain", "created_at", "updated_at", "is_expired")
    search_fields = ("email", "domain__name")
    readonly_fields = ("created_at", "updated_at", "is_expired")

    def is_expired(self, obj):
        """Return the expiration date of the invitation."""
        return obj.is_expired
