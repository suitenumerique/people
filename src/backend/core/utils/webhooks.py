"""Fire webhooks with synchronous retries"""

import logging

import requests

from core.enums import WebhookStatusChoices

from .scim import SCIMClient

logger = logging.getLogger(__name__)


class WebhookSCIMClient:
    """Wraps the SCIM client to record call results on webhooks."""

    def __getattr__(self, name):
        """Handle calls from webhooks to synchronize a team access with a distant application."""

        def wrapper(team, user):
            """
            Wrap SCIMClient calls to handle retries, error handling and storing result in the
            calling Webhook instance.
            """
            for webhook in team.webhooks.all():
                if not webhook.url:
                    continue

                client = SCIMClient()
                status = WebhookStatusChoices.FAILURE
                try:
                    response = getattr(client, name)(webhook, user)

                except requests.exceptions.RetryError as exc:
                    logger.error(
                        "%s synchronization failed due to max retries exceeded with url %s",
                        name,
                        webhook.url,
                        exc_info=exc,
                    )
                except requests.exceptions.RequestException as exc:
                    logger.error(
                        "%s synchronization failed with %s.",
                        name,
                        webhook.url,
                        exc_info=exc,
                    )
                else:
                    extra = {
                        "response": response.content,
                    }
                    # pylint: disable=no-member
                    if response.status_code == requests.codes.ok:
                        logger.info(
                            "%s synchronization succeeded with %s",
                            name,
                            webhook.url,
                            extra=extra,
                        )

                        status = WebhookStatusChoices.SUCCESS
                    else:
                        logger.error(
                            "%s synchronization failed with %s",
                            name,
                            webhook.url,
                            extra=extra,
                        )

                webhook._meta.model.objects.filter(id=webhook.id).update(status=status)  # noqa

        return wrapper


scim_synchronizer = WebhookSCIMClient()
