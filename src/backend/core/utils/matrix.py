"""Matrix client for interoperability to synchronize with remote service providers."""

import logging

from django.conf import settings

import requests
from rest_framework.status import (
    HTTP_200_OK,
)
from urllib3.util import Retry

logger = logging.getLogger(__name__)

adapter = requests.adapters.HTTPAdapter(
    max_retries=Retry(
        total=4,
        backoff_factor=0.1,
        status_forcelist=[500, 502],
        allowed_methods=["POST"],
    )
)

session = requests.Session()
session.mount("http://", adapter)
session.mount("https://", adapter)


class MatrixAPIClient:
    """A client to interact with Matrix API"""

    secret = settings.TCHAP_ACCESS_TOKEN

    def get_headers(self, webhook):
        """Build header dict from webhook object."""
        headers = {"Content-Type": "application/json"}
        if "tchap.gouv.fr" in webhook.url:
            token = settings.TCHAP_ACCESS_TOKEN
        elif webhook.secret:
            token = webhook.secret
        else:
            raise ValueError("Please configure this webhook's secret access token.")
        headers["Authorization"] = f"Bearer {token}"
        return headers

    def _get_room_url(self, webhook_url):
        """Returns room id from webhook url."""
        room_id = webhook_url.split("/room/")[1]
        base_url = room_id.split(":")[1]
        if "tchap.gouv.fr" in webhook_url:
            base_url = f"matrix.{base_url}"
        return f"https://{base_url}/_matrix/client/v3/rooms/{room_id}"

    def get_user_id(self, user):
        """Returns user id from email."""
        if user.email is None:
            raise ValueError("You must first set an email for the user.")

        return f"@{user.email.replace('@', ':')}"

    def join_room(self, webhook):
        """Accept invitation to the room. As of today, it is a mandatory step
        to make sure our account will be able to invite/remove users."""
        return session.post(
            f"{self._get_room_url(webhook.url)}/join",
            json={},
            headers=self.get_headers(webhook),
            verify=True,
            timeout=3,
        )

    def add_user_to_group(self, webhook, user):
        """Send request to invite an user to a room or space upon adding them to group.."""
        join_response = self.join_room(webhook)
        if join_response.status_code != HTTP_200_OK:
            logger.error(
                "Synchronization failed (cannot join room) %s",
                webhook.url,
            )
            return join_response, False

        user_id = self.get_user_id(user)
        response = session.post(
            f"{self._get_room_url(webhook.url)}/invite",
            json={
                "user_id": user_id,
                "reason": f"User added to team {webhook.team} on People",
            },
            headers=self.get_headers(webhook),
            verify=True,
            timeout=3,
        )

        # Checks for false negative
        # (i.e. trying to invite user already in room)
        webhook_succeeded = False
        if (
            response.status_code == HTTP_200_OK
            or b"is already in the room." in response.content
        ):
            webhook_succeeded = True

        return response, webhook_succeeded

    def remove_user_from_group(self, webhook, user):
        """Send request to kick an user from a room or space upon removing them from group."""
        join_response = self.join_room(webhook)
        if join_response.status_code != HTTP_200_OK:
            logger.error(
                "Synchronization failed (cannot join room) %s",
                webhook.url,
            )
            return join_response, False

        user_id = self.get_user_id(user)
        response = session.post(
            f"{self._get_room_url(webhook.url)}/kick",
            json={
                "user_id": user_id,
                "reason": f"User removed from team {webhook.team} on People",
            },
            headers=self.get_headers(webhook),
            verify=True,
            timeout=3,
        )

        # Checks for false negative
        # (i.e. trying to remove user who already left the room)
        webhook_succeeded = False
        if (
            response.status_code == HTTP_200_OK
            or b"The target user is not in the room" in response.content
        ):
            webhook_succeeded = True

        return response, webhook_succeeded
