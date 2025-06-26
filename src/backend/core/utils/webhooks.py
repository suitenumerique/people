"""Fire webhooks with synchronous retries"""

import logging

import requests

from core import enums
from core.enums import WebhookStatusChoices

from .matrix import MatrixAPIClient
from .scim import SCIMClient

logger = logging.getLogger(__name__)


class WebhookClient:
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

                status = WebhookStatusChoices.FAILURE
                response, webhook_succeeded = self._get_response_and_status(
                    name, webhook, user
                )
                if response is not None:
                    extra = {"response": response.content}
                    # pylint: disable=no-member
                    if webhook_succeeded:
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

    def _get_client(self, webhook):
        """Get client depending on the protocol."""
        if webhook.protocol == enums.WebhookProtocolChoices.MATRIX:
            return MatrixAPIClient()

        return SCIMClient()

    def _get_response_and_status(self, name, webhook, user):
        """Get response from webhook outside party."""
        client = self._get_client(webhook)

        try:
            response, webhook_succeeded = getattr(client, name)(webhook, user)
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
            return response, webhook_succeeded

        return None, False


webhooks_synchronizer = WebhookClient()
