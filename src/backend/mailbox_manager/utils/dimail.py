"""A minimalist client to synchronize with mailbox provisioning API."""

from logging import getLogger

from django.conf import settings
from django.core import exceptions

import requests
from rest_framework import status
from urllib3.util import Retry

logger = getLogger(__name__)

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


class DimailAPIClient:
    """A dimail-API client."""

    API_URL = settings.MAIL_PROVISIONING_API_URL

    def get_headers(self, domain):
        """Build header dict from domain object."""
        # self.secret is the encoded basic auth, to request a new token from dimail-api
        headers = {"Content-Type": "application/json"}

        response = requests.get(
            f"{self.API_URL}/token/",
            headers={"Authorization": f"Basic {domain.secret}"},
            timeout=status.HTTP_200_OK,
        )

        if response.json() == "{'detail': 'Permission denied'}":
            raise exceptions.PermissionDenied(
                "This secret does not allow for a new token."
            )

        if "access_token" in response.json():
            headers["Authorization"] = f"Bearer {response.json()['access_token']}"
            logger.info("Token succesfully granted by mail-provisioning API.")

        return headers

    def send_mailbox_request(self, mailbox):
        """Send a CREATE mailbox request to mail provisioning API."""

        payload = {
            "givenName": mailbox.first_name,
            "surName": mailbox.last_name,
            "displayName": f"{mailbox.first_name} {mailbox.last_name}",
        }

        try:
            response = session.post(
                f"{self.API_URL}/domains/{mailbox.domain}/mailboxes/{mailbox.local_part}/",
                json=payload,
                headers=self.get_headers(mailbox.domain),
                verify=True,
                timeout=10,
            )
        except requests.exceptions.ConnectionError as error:
            logger.error(
                "Connection error while trying to reach %s.",
                self.API_URL,
                exc_info=error,
            )
            raise error

        if response.status_code == status.HTTP_201_CREATED:
            extra = {"response": response.content.decode("utf-8")}
            # This a temporary broken solution. Password will soon be sent
            # from OX servers but their prod is not ready.
            # In the meantime, we log mailbox info (including password !)
            logger.info(
                "Mailbox successfully created on domain %s",
                mailbox.domain.name,
                extra=extra,
            )
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            logger.error(
                "[DIMAIL] 403 Forbidden: please check the mail domain secret of %s",
                mailbox.domain.name,
            )
            raise exceptions.PermissionDenied(
                f"Please check secret of the mail domain {mailbox.domain.name}"
            )
        else:
            logger.error(
                "Unexpected response: %s",
                response.content.decode("utf-8"),
            )

        return response
