"""Mailbox manager tasks."""

import time

from django.conf import settings

import requests
from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger

from mailbox_manager import enums
from mailbox_manager.models import MailDomain
from mailbox_manager.utils.dimail import DimailAPIClient
from people.celery_app import app as celery_app

logger = get_task_logger(__name__)


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    """Setup periodic tasks."""
    sender.add_periodic_task(
        crontab(hour="1", minute="00"),
        fetch_domains_status_task.s(
            status=enums.MailDomainStatusChoices.ACTION_REQUIRED
        ),
        name="fetch_action_required_domains_every_night",
        serializer="json",
    )
    sender.add_periodic_task(
        crontab(hour="1", minute="20"),
        fetch_domains_status_task.s(status=enums.MailDomainStatusChoices.FAILED),
        name="fetch_failed_domains_every_night",
        serializer="json",
    )
    sender.add_periodic_task(
        crontab(hour="1", minute="40", day_of_week="1"),
        fetch_domains_status_task.s(status=enums.MailDomainStatusChoices.ENABLED),
        name="fetch_enabled_domains_every_monday_night",
        serializer="json",
    )
    sender.add_periodic_task(
        crontab(hour="2", minute="00"),
        import_missing_dimail_mailboxes.s(),
        name="import mailboxes from dimail every night",
        serializer="json",
    )


@celery_app.task
def fetch_domains_status_task(status: str):
    """Celery task to call dimail to check and update domains status."""
    client = DimailAPIClient()
    changed_domains = []
    for domain in MailDomain.objects.filter(status=status):
        old_status = domain.status
        # wait 10 seconds between each domain treatment to avoid overloading dimail
        time.sleep(settings.MAIL_CHECK_DOMAIN_INTERVAL)
        try:
            client.fetch_domain_status(domain)
        except requests.exceptions.HTTPError as err:
            logger.error("Failed to fetch status for domain %s: %s", domain.name, err)
        else:
            if old_status != domain.status:
                domain.notify_status_change()
                changed_domains.append(f"{domain.name} ({domain.status})")
    return changed_domains


@celery_app.task
def import_missing_dimail_mailboxes():
    """Celery task to import missing mailboxes from dimail."""
    client = DimailAPIClient()

    for domain in MailDomain.objects.filter(
        status=enums.MailDomainStatusChoices.ENABLED
    ):
        client.import_mailboxes(domain)
