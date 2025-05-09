"""Matrix client for interoperability to synchronize with remote service providers."""

import logging

from django.conf import settings

import requests
from urllib3.util import Retry

logger = logging.getLogger(__name__)

adapter = requests.adapters.HTTPAdapter(
    max_retries=Retry(
        total=4,
        backoff_factor=0.1,
        status_forcelist=[500, 502],
        allowed_methods=["PATCH"],
    )
)

session = requests.Session()
session.mount("http://", adapter)
session.mount("https://", adapter)


class MatrixAPIClient:
    """A client to interact with Matrix API"""

    secret = settings.MATRIX_ACCESS_TOKEN

    def _get_room_id(self, webhook_url):
        """Returns room id from webhook url."""
        room_id = webhook_url.split("/room/")[1]
        home_server = room_id.split(":")[1]
        return room_id, home_server

    def get_user_id(self, user):
        """Returns user id from email."""
        if user.email is None:
            raise ValueError("You must first set an email for the user.")

        return f"@{user.email.replace('@', ':')}"

    def join_room(self, webhook):
        """Accept invitation to the room. As of today, it is a mandatory step to make sure our account will be able to invite/remove users."""
        room_id, room_server = self._get_room_id(webhook.url)

        if webhook.secret is None:
            raise ValueError("Cannot join room without secret access token.")

        return session.post(
            f"https://matrix.{room_server}/_matrix/client/v3/rooms/{room_id}/join",
            json={},
            headers=webhook.get_headers(),
            verify=False,
            timeout=3,
        )

    def invite_user_to_room(self, webhook, user):
        """Send request to invite an user to a room or space."""
        self.join_room(webhook)

        room_id, room_server = self._get_room_id(webhook.url)
        user_id = self.get_user_id(user)
        url = f"https://matrix.{room_server}/_matrix/client/v3/rooms/{room_id}/invite"
        return session.post(
            url,
            json={
                "user_id": user_id,
                "reason": f"User added to team {webhook.team} on People",
            },
            headers=webhook.get_headers(),
            verify=False,
            timeout=3,
        )

    def kick_user_from_room(self, webhook, user):
        """Send request to kick an user from a room or space."""
        self.join_room(webhook)

        room_id, room_server = self._get_room_id(webhook.url)
        user_id = self.get_user_id(user)
        url = f"https://matrix.{room_server}/_matrix/client/v3/rooms/{room_id}/kick"
        return session.post(
            url,
            json={
                "user_id": user_id,
                "reason": f"User removed from team {webhook.team} on People",
            },
            headers=webhook.get_headers(),
            verify=False,
            timeout=3,
        )
