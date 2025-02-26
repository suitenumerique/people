"""Mailbox manager tasks."""

import logging

import requests
from celery.schedules import crontab

from mailbox_manager.models import MailDomain, MailDomainStatusChoices
from mailbox_manager.utils.dimail import DimailAPIClient
from people.celery_app import app as celery_app

logger = logging.getLogger(__name__)


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Setup periodic tasks.
    """
    sender.add_periodic_task(
        crontab(minute="*/5"), fetch_domains_status.s(), name="Fetch domains status"
    )


@celery_app.task
def fetch_domains_status():
    """
    Call dimail to check and update domains status.
    """
    client = DimailAPIClient()
    # do not fetch status of disabled domains
    domains = MailDomain.objects.exclude(status=MailDomainStatusChoices.DISABLED)
    update_count, check_count = 0, 0
    for domain in domains:
        old_status = domain.status
        try:
            client.fetch_domain_status(domain)
        except requests.exceptions.HTTPError as err:
            logger.error("Failed to fetch status for domain %s: %s", domain.name, err)
        else:
            if old_status != domain.status:
                update_count += 1
                # Send notification to owners and admins of the domain
                # when its status changes to failed or enabled
                if domain.status == MailDomainStatusChoices.FAILED:
                    domain.send_notification(
                        subject="Domain status changed",
                        message=f"Domain {domain.name} is down",
                    )
                elif domain.status == MailDomainStatusChoices.ENABLED:
                    domain.send_notification(
                        subject="Domain status changed",
                        message=f"Domain {domain.name} is up",
                    )
            else:
                check_count += 1
    return f"Domains processed: {update_count} updated, {check_count} checked"
