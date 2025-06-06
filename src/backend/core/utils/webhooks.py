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
                response = self._get_response(name, webhook, user)
                if response is not None:
                    extra = {"response": response.content}
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

    def _get_client(self, webhook):
        """Get client depending on the protocol."""
        if webhook.protocol == enums.WebhookProtocolChoices.MATRIX:
            return MatrixAPIClient()

        return SCIMClient()

    def _get_response(self, name, webhook, user):
        """Get response from webhook outside party."""
        client = self._get_client(webhook)

        if webhook.protocol == enums.WebhookProtocolChoices.MATRIX:
            if name == "add_user_to_group":
                name = "invite_user_to_room"
            elif name == "remove_user_from_group":
                name = "kick_user_from_room"
            else:
                pass

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

        return response


webhooks_synchronizer = WebhookClient()
