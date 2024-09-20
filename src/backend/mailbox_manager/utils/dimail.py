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
    API_CREDENTIALS = settings.MAIL_PROVISIONING_API_CREDENTIALS

    def get_headers(self, user_sub=None):
        """
        Build headers dictionary. Requires MAIL_PROVISIONING_API_CREDENTIALS setting,
        to get a token from dimail /token/ endpoint.
        If provided, request user' sub is used for la regie to log in as this user,
        thus allowing for more precise logs.
        """
        headers = {"Content-Type": "application/json"}
        params = None

        if user_sub:
            params = {"username": str(user_sub)}

        response = requests.get(
            f"{self.API_URL}/token/",
            headers={"Authorization": f"Basic {self.API_CREDENTIALS}"},
            params=params,
            timeout=20,
        )

        if response.status_code == status.HTTP_200_OK:
            headers["Authorization"] = f"Bearer {response.json()['access_token']}"
            logger.info("Token succesfully granted by mail-provisioning API.")
            return headers

        if response.status_code == status.HTTP_403_FORBIDDEN:
            logger.error(
                "[DIMAIL] 403 Forbidden: Could not retrieve a token,\
                please check 'MAIL_PROVISIONING_API_CREDENTIALS' setting.",
            )
            raise exceptions.PermissionDenied(
                "Token denied. Please check your MAIL_PROVISIONING_API_CREDENTIALS."
            )

        return self.pass_dimail_unexpected_response(response)

    def send_mailbox_request(self, mailbox, user_sub=None):
        """Send a CREATE mailbox request to mail provisioning API."""

        payload = {
            "givenName": mailbox["first_name"],
            "surName": mailbox["last_name"],
            "displayName": f"{mailbox['first_name']} {mailbox['last_name']}",
        }
        headers = self.get_headers(user_sub)

        try:
            response = session.post(
                f"{self.API_URL}/domains/{mailbox['domain']}/mailboxes/{mailbox['local_part']}/",
                json=payload,
                headers=headers,
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
                "Mailbox successfully created on domain %s by user %s",
                str(mailbox["domain"]),
                user_sub,
                extra=extra,
            )
            return response

        if response.status_code == status.HTTP_403_FORBIDDEN:
            raise exceptions.PermissionDenied(
                "Permission denied. Please check your MAIL_PROVISIONING_API_CREDENTIALS."
            )

        return self.pass_dimail_unexpected_response(response)

    def pass_dimail_unexpected_response(self, response):
        """Raise error when encountering an unexpected error in dimail."""
        error_content = response.content.decode("utf-8")

        logger.error("[DIMAIL] unexpected error : %s", error_content)
        raise SystemError(f"Unexpected response from dimail: {error_content}")
