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
        crontab(hour="3", minute="45", day_of_week="1"),
        fetch_domains_status_task.s(status=enums.MailDomainStatusChoices.ENABLED),
        name="fetch_enabled_domains_every_monday_at_3_45",
        serializer="json",
    )
    sender.add_periodic_task(
        crontab(minute="0"),  # Run at the start of every hour
        fetch_domains_status_task.s(status=enums.MailDomainStatusChoices.PENDING),
        name="fetch_pending_domains_every_hour",
        serializer="json",
    )
    sender.add_periodic_task(
        crontab(minute="30"),  # Run at the 30th minute of every hour
        fetch_domains_status_task.s(
            status=enums.MailDomainStatusChoices.ACTION_REQUIRED
        ),
        name="fetch_action_required_domains_every_hour",
        serializer="json",
    )
    sender.add_periodic_task(
        crontab(minute="45"),  # Run at the 45th minute of every hour
        fetch_domains_status_task.s(status=enums.MailDomainStatusChoices.FAILED),
        name="fetch_failed_domains_every_hour",
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
