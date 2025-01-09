"""Management command to check and update domain status"""

import logging

from django.core.management.base import BaseCommand

import requests

from mailbox_manager.enums import MailDomainStatusChoices
from mailbox_manager.models import MailDomain
from mailbox_manager.utils.dimail import DimailAPIClient

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Management command to check and update domains status from dimail
    """

    help = (
        "This command calls dimail to get and update the status of domains."
        "All domains without a disabled status will be checked and updated if status"
        "sent by dimail does not match our status saved in our database."
    )

    def handle(self, *args, **options):
        """Handling of the management command."""

        self.stdout.write("Start fetching domain status from dimail...")
        client = DimailAPIClient()
        # do not fetch status of disabled domains
        domains = MailDomain.objects.exclude(status=MailDomainStatusChoices.DISABLED)
        for domain in domains:
            old_status = domain.status
            try:
                client.fetch_domain_status(domain)
            except requests.exceptions.HTTPError as err:
                self.stdout.write(
                    self.style.ERROR(
                        f"Fetch failed for {domain.name} with message: '{err}'"
                    )
                )
            else:
                action = "UPDATED" if old_status != domain.status else "CHECKED"
                domain_name = (
                    f"{domain.name[:40]}..." if len(domain.name) > 40 else domain.name
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        (
                            f"Domain {domain_name}"
                            + "." * (50 - len(domain_name))
                            + action
                        )
                    )
                )
        self.stdout.write("Done", ending="\n")
