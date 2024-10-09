"""A minimalist client to synchronize with mailbox provisioning API."""

import ast
import smtplib
from email.errors import HeaderParseError, NonASCIILocalPartDefect
from email.headerregistry import Address
from logging import getLogger

from django.conf import settings
from django.contrib.sites.models import Site
from django.core import exceptions, mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

import requests
from rest_framework import status
from urllib3.util import Retry

from mailbox_manager import models

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
                f"{self.API_URL}/domains/{mailbox['domain']}/mailboxes/{mailbox['local_part']}",
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
            logger.info(
                "Mailbox successfully created on domain %s by user %s",
                str(mailbox["domain"]),
                user_sub,
            )
            return response

        if response.status_code == status.HTTP_403_FORBIDDEN:
            logger.error(
                "[DIMAIL] 403 Forbidden: you cannot access domain %s",
                str(mailbox["domain"]),
            )
            raise exceptions.PermissionDenied(
                "Permission denied. Please check your MAIL_PROVISIONING_API_CREDENTIALS."
            )

        return self.pass_dimail_unexpected_response(response)

    def pass_dimail_unexpected_response(self, response):
        """Raise error when encountering an unexpected error in dimail."""
        error_content = response.content.decode("utf-8")

        logger.error(
            "[DIMAIL] unexpected error : %s %s", response.status_code, error_content
        )
        raise requests.exceptions.HTTPError(
            f"Unexpected response from dimail: {response.status_code} {error_content}"
        )

    def send_new_mailbox_notification(self, recipient, mailbox_data):
        """
        Send email to confirm mailbox creation
        and send new mailbox information.
        """

        template_vars = {
            "title": _("Your new mailbox information"),
            "site": Site.objects.get_current(),
            "webmail_url": settings.WEBMAIL_URL,
            "mailbox_data": mailbox_data,
        }

        msg_html = render_to_string("mail/html/new_mailbox.html", template_vars)
        msg_plain = render_to_string("mail/text/new_mailbox.txt", template_vars)

        try:
            mail.send_mail(
                template_vars["title"],
                msg_plain,
                settings.EMAIL_FROM,
                [recipient],
                html_message=msg_html,
                fail_silently=False,
            )
            logger.info(
                "Information for mailbox %s sent to %s.",
                mailbox_data["email"],
                recipient,
            )
        except smtplib.SMTPException as exception:
            logger.error(
                "Mailbox confirmation email to %s was not sent: %s",
                recipient,
                exception,
            )

    def synchronize_mailboxes_from_dimail(self, domain):
        """Synchronize mailboxes from dimail - open xchange to our database.
        This is useful in case of acquisition of a pre-existing mail domain.
        Mailboxes created here are not new mailboxes and will not trigger mail notification."""

        try:
            response = session.get(
                f"{self.API_URL}/domains/{domain.name}/mailboxes/",
                headers=self.get_headers(),
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

        if response.status_code != status.HTTP_200_OK:
            return self.pass_dimail_unexpected_response(response)

        dimail_mailboxes = ast.literal_eval(
            response.content.decode("utf-8")
        )  # format output str to proper list

        people_mailboxes = models.Mailbox.objects.filter(domain=domain)
        imported_mailboxes = []
        for dimail_mailbox in dimail_mailboxes:
            if not dimail_mailbox["email"] in [
                str(people_mailbox) for people_mailbox in people_mailboxes
            ]:
                try:
                    # sometimes dimail api returns email from another domain,
                    # so we decide to exclude this kind of email
                    address = Address(addr_spec=dimail_mailbox["email"])
                    if address.domain == domain.name:
                        # creates a mailbox on our end
                        mailbox = models.Mailbox.objects.create(
                            first_name=dimail_mailbox["givenName"],
                            last_name=dimail_mailbox["surName"],
                            local_part=address.username,
                            domain=domain,
                            secondary_email=dimail_mailbox[
                                "email"
                            ],  # secondary email is mandatory. Unfortunately, dimail doesn't
                            # store any. We temporarily give current email as secondary email.
                        )
                        imported_mailboxes.append(str(mailbox))
                    else:
                        logger.warning(
                            "Import of email %s failed because of a wrong domain",
                            dimail_mailbox["email"],
                        )
                except (HeaderParseError, NonASCIILocalPartDefect) as err:
                    logger.warning(
                        "Import of email %s failed with error %s",
                        dimail_mailbox["email"],
                        err,
                    )
        return imported_mailboxes
