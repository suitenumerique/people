"""A minimalist SCIM client to synchronize with remote service providers."""

import logging

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


class SCIMClient:
    """A minimalist SCIM client for our needs."""

    def add_user_to_group(self, webhook, user):
        """Add a user to a group from its ID or email."""
        payload = {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
            "Operations": [
                {
                    "op": "add",
                    "path": "members",
                    "value": [
                        {"value": str(user.id), "email": user.email, "type": "User"}
                    ],
                }
            ],
        }

        response = session.patch(
            webhook.url,
            json=payload,
            headers=webhook.get_headers(),
            verify=False,
            timeout=3,
        )

        return response, response.ok

    def remove_user_from_group(self, webhook, user):
        """Remove a user from a group by its ID or email."""
        payload = {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
            "Operations": [
                {
                    "op": "remove",
                    "path": "members",
                    "value": [
                        {"value": str(user.id), "email": user.email, "type": "User"}
                    ],
                }
            ],
        }
        response = session.patch(
            webhook.url,
            json=payload,
            headers=webhook.get_headers(),
            verify=False,
            timeout=3,
        )

        return response, response.ok
