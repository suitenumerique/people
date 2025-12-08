"""Celery tasks for the token_exchange application."""

from django.core.management import call_command

from celery import Celery
from celery.schedules import crontab

from people.celery_app import app as celery_app


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    """Setup periodic tasks for token_exchange module."""
    # Daily cleanup of expired tokens at 2:00 AM
    sender.add_periodic_task(
        crontab(hour="2", minute="0"),
        cleanup_expired_tokens_task.s(),
        name="cleanup_expired_tokens_daily",
        serializer="json",
    )


@celery_app.task
def cleanup_expired_tokens_task():
    """Task to clean up expired exchanged tokens."""
    call_command("cleanup_expired_tokens")
