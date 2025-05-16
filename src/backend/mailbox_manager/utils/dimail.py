# pylint: disable=line-too-long

"""A minimalist client to synchronize with mailbox provisioning API."""

import ast
import json
import smtplib
from email.errors import HeaderParseError, NonASCIILocalPartDefect
from email.headerregistry import Address
from logging import getLogger

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.sites.models import Site
from django.core import exceptions, mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.utils.translation import override

import requests
from rest_framework import status
from urllib3.util import Retry

from mailbox_manager import enums, models

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
    API_TIMEOUT = settings.MAIL_PROVISIONING_API_TIMEOUT

    def get_headers(self):
        """
        Return Bearer token. Requires MAIL_PROVISIONING_API_CREDENTIALS setting,
        to get a token from dimail /token/ endpoint.
        """

        try:
            response = requests.get(
                f"{self.API_URL}/token/",
                headers={"Authorization": f"Basic {self.API_CREDENTIALS}"},
                timeout=self.API_TIMEOUT,
            )
        except requests.exceptions.ConnectionError as error:
            logger.error(
                "Connection error while trying to reach %s.",
                self.API_URL,
                exc_info=error,
            )
            raise error

        if response.status_code == status.HTTP_200_OK:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {response.json()['access_token']}",
            }
            logger.info("Token successfully granted by mail-provisioning API.")
            return headers

        if response.status_code == status.HTTP_403_FORBIDDEN:
            logger.error(
                "[DIMAIL] 403 Forbidden: Could not retrieve a token,"
                "please check 'MAIL_PROVISIONING_API_CREDENTIALS' setting.",
            )
            raise exceptions.PermissionDenied(
                "Token denied. Please check your MAIL_PROVISIONING_API_CREDENTIALS."
            )

        return self.raise_exception_for_unexpected_response(response)

    def create_domain(self, domain_name, request_user):
        """Send a domain creation request to dimail API."""

        payload = {
            "name": domain_name,
            "context_name": domain_name,  # for now, we put each domain on its own context
            "features": ["webmail", "mailbox", "alias"],
            "delivery": "virtual",
        }
        try:
            response = session.post(
                f"{self.API_URL}/domains/",
                json=payload,
                headers={"Authorization": f"Basic {self.API_CREDENTIALS}"},
                verify=True,
                timeout=self.API_TIMEOUT,
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
                "Domain %s successfully created on dimail by user %s",
                domain_name,
                request_user,
            )
            return response

        return self.raise_exception_for_unexpected_response(response)

    def create_mailbox(self, mailbox, request_user=None):
        """Send a CREATE mailbox request to mail provisioning API."""

        payload = {
            # givenName value can be empty
            "givenName": mailbox.first_name,
            # surName value can be empty
            "surName": mailbox.last_name,
            # displayName value has to be unique
            "displayName": f"{mailbox.first_name} {mailbox.last_name}",
        }
        headers = self.get_headers()

        try:
            response = session.post(
                f"{self.API_URL}/domains/{mailbox.domain.name}/mailboxes/{mailbox.local_part}",
                json=payload,
                headers=headers,
                verify=True,
                timeout=self.API_TIMEOUT,
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
                str(mailbox.domain),
                request_user,
            )
            return response

        if response.status_code == status.HTTP_403_FORBIDDEN:
            logger.error(
                "[DIMAIL] 403 Forbidden: you cannot access domain %s",
                str(mailbox.domain),
            )
            raise exceptions.PermissionDenied(
                "Permission denied. Please check your MAIL_PROVISIONING_API_CREDENTIALS."
            )

        return self.raise_exception_for_unexpected_response(response)

    def create_user(self, user_id):
        """Send a request to dimail, to create a new user there. In dimail, user ids are subs."""

        payload = {"name": user_id, "password": "no", "is_admin": "false", "perms": []}

        try:
            response = session.post(
                f"{self.API_URL}/users/",
                headers={"Authorization": f"Basic {self.API_CREDENTIALS}"},
                json=payload,
                verify=True,
                timeout=self.API_TIMEOUT,
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
                '[DIMAIL] User "%s" successfully created on dimail',
                user_id,
            )
            return response

        if response.status_code == status.HTTP_409_CONFLICT:
            logger.info(
                '[DIMAIL] Attempt to create user "%s" which already exists.',
                user_id,
            )
            return response

        return self.raise_exception_for_unexpected_response(response)

    def create_allow(self, user_id, domain_name):
        """Send a request to dimail for a new 'allow' between user and the domain."""

        payload = {
            "user": user_id,
            "domain": domain_name,
        }

        try:
            response = session.post(
                f"{self.API_URL}/allows/",
                headers={"Authorization": f"Basic {self.API_CREDENTIALS}"},
                json=payload,
                verify=True,
                timeout=self.API_TIMEOUT,
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
                '[DIMAIL] Permissions granted for user "%s" on domain %s.',
                user_id,
                domain_name,
            )
            return response

        if response.status_code == status.HTTP_409_CONFLICT:
            logger.info(
                '[DIMAIL] Attempt to create already existing permission between "%s" and "%s".',
                user_id,
                domain_name,
            )
            return response

        return self.raise_exception_for_unexpected_response(response)

    def raise_exception_for_unexpected_response(self, response):
        """Raise error when encountering an unexpected error in dimail."""
        try:
            error_content = json.loads(
                response.content.decode(response.encoding).replace("'", '"')
            )
        except json.decoder.JSONDecodeError:
            error_content = response.content.decode(response.encoding)

        raise requests.exceptions.HTTPError(
            f"[DIMAIL] unexpected error: {response.status_code} {error_content}"
        )

    def notify_mailbox_creation(self, recipient, mailbox_data, issuer=None):
        """
        Send email to confirm mailbox creation
        and send new mailbox information.
        """
        title = _("Your new mailbox information")
        template_name = "new_mailbox"
        self._send_mailbox_related_email(
            title, template_name, recipient, mailbox_data, issuer
        )

    def notify_mailbox_password_reset(self, recipient, mailbox_data, issuer=None):
        """
        Send email to notify of password reset
        and send new password.
        """
        title = _("Your password has been updated")
        template_name = "reset_password"
        self._send_mailbox_related_email(
            title, template_name, recipient, mailbox_data, issuer
        )

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    def _send_mailbox_related_email(
        self, title, template_name, recipient, mailbox_data, issuer=None
    ):
        """
        Send email with new mailbox or password reset information.
        """

        context = {
            "title": title,
            "site": Site.objects.get_current(),
            "webmail_url": settings.WEBMAIL_URL,
            "mailbox_data": mailbox_data,
        }

        try:
            with override(issuer.language if issuer else settings.LANGUAGE_CODE):
                mail.send_mail(
                    context["title"],
                    render_to_string(f"mail/text/{template_name}.txt", context),
                    settings.EMAIL_FROM,
                    [recipient],
                    html_message=render_to_string(
                        f"mail/html/{template_name}.html", context
                    ),
                    fail_silently=False,
                )
        except smtplib.SMTPException as exception:
            logger.error(
                "Failed to send mailbox information to %s was not sent: %s",
                recipient,
                exception,
            )
        else:
            logger.info(
                "Information for mailbox %s sent to %s.",
                mailbox_data["email"],
                recipient,
            )

    def import_mailboxes(self, domain):
        """Import mailboxes from dimail - open xchange in our database.
        This is useful in case of acquisition of a pre-existing mail domain.
        Mailboxes created here are not new mailboxes and will not trigger mail notification."""

        try:
            response = session.get(
                f"{self.API_URL}/domains/{domain.name}/mailboxes/",
                headers=self.get_headers(),
                verify=True,
                timeout=self.API_TIMEOUT,
            )
        except requests.exceptions.ConnectionError as error:
            logger.error(
                "Connection error while trying to reach %s.",
                self.API_URL,
                exc_info=error,
            )
            raise error

        if response.status_code != status.HTTP_200_OK:
            return self.raise_exception_for_unexpected_response(response)

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
                            status=enums.MailboxStatusChoices.ENABLED,
                            password=make_password(None),  # unusable password
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

    def disable_mailbox(self, mailbox, request_user=None):
        """Send a request to disable a mailbox to dimail API"""
        response = session.patch(
            f"{self.API_URL}/domains/{mailbox.domain.name}/mailboxes/{mailbox.local_part}",
            json={"active": "no"},
            headers=self.get_headers(),
            verify=True,
            timeout=self.API_TIMEOUT,
        )
        if response.status_code == status.HTTP_200_OK:
            logger.info(
                "Mailbox %s successfully desactivated on domain %s by user %s",
                str(mailbox),
                str(mailbox.domain),
                request_user,
            )
            return response
        return self.raise_exception_for_unexpected_response(response)

    def enable_mailbox(self, mailbox, request_user=None):
        """Send a request to enable a mailbox to dimail API"""
        response = session.patch(
            f"{self.API_URL}/domains/{mailbox.domain.name}/mailboxes/{mailbox.local_part}",
            json={
                "active": "yes",
                "givenName": mailbox.first_name,
                "surName": mailbox.last_name,
                "displayName": f"{mailbox.first_name} {mailbox.last_name}",
            },
            headers=self.get_headers(),
            verify=True,
            timeout=self.API_TIMEOUT,
        )
        if response.status_code == status.HTTP_200_OK:
            logger.info(
                "Mailbox %s successfully enabled on domain %s by user %s",
                str(mailbox),
                str(mailbox.domain),
                request_user,
            )
            return response
        return self.raise_exception_for_unexpected_response(response)

    def send_pending_mailboxes(self, domain):
        """Send requests for all pending mailboxes of a domain. Returns a list of failed mailboxes for this domain."""
        failed_mailboxes = []

        for mailbox in domain.mailboxes.filter(
            status=enums.MailboxStatusChoices.PENDING
        ):
            try:
                response = self.create_mailbox(mailbox)
            except requests.exceptions.HTTPError:
                failed_mailboxes.append(str(mailbox))
            else:
                mailbox.status = enums.MailDomainStatusChoices.ENABLED
                mailbox.save()

                if mailbox.secondary_email and mailbox.secondary_email != str(mailbox):
                    # send confirmation email
                    self.notify_mailbox_creation(
                        recipient=mailbox.secondary_email,
                        mailbox_data=response.json(),
                    )
                else:
                    logger.warning(
                        "Email notification for %s creation not sent "
                        "because no valid secondary email found",
                        mailbox,
                    )
        return {"failed_mailboxes": failed_mailboxes}

    def check_domain(self, domain):
        """Send a request to dimail to check domain health."""
        try:
            response = session.get(
                f"{self.API_URL}/domains/{domain.name}/check/",
                headers={"Authorization": f"Basic {self.API_CREDENTIALS}"},
                verify=True,
                timeout=self.API_TIMEOUT,
            )
        except requests.exceptions.ConnectionError as error:
            logger.error(
                "Connection error while trying to reach %s.",
                self.API_URL,
                exc_info=error,
            )
            raise error
        if response.status_code == status.HTTP_200_OK:
            return response.json()
        return self.raise_exception_for_unexpected_response(response)

    def fix_domain(self, domain):
        """Send a request to dimail to fix a domain.
        Allow to fix internal checks."""
        response = session.get(
            f"{self.API_URL}/domains/{domain.name}/fix/",
            headers={"Authorization": f"Basic {self.API_CREDENTIALS}"},
            verify=True,
            timeout=self.API_TIMEOUT,
        )
        if response.status_code == status.HTTP_200_OK:
            logger.info(
                "Domain %s successfully fixed by dimail",
                str(domain),
            )
            return response.json()
        return self.raise_exception_for_unexpected_response(response)

    def fetch_domain_status(self, domain):
        """Send a request to check and update status of a domain."""
        dimail_response = self.check_domain(domain)
        if dimail_response:
            dimail_state = dimail_response["state"]
            # if domain is not enabled and dimail returns ok status, enable it
            if (
                domain.status != enums.MailDomainStatusChoices.ENABLED
                and dimail_state == "ok"
            ):
                self.send_pending_mailboxes(domain)
                domain.status = enums.MailDomainStatusChoices.ENABLED
                domain.last_check_details = dimail_response
                domain.save()
            # if dimail returns broken status, we need to extract external and internal checks
            # and manage the case where the domain has to be fixed by support
            elif dimail_state == "broken":
                external_checks = self._get_dimail_checks(
                    dimail_response, internal=False
                )
                internal_checks = self._get_dimail_checks(
                    dimail_response, internal=True
                )
                # manage the case where the domain has to be fixed by support
                if not all(external_checks.values()):
                    domain.status = enums.MailDomainStatusChoices.ACTION_REQUIRED
                    domain.last_check_details = dimail_response
                    domain.save()
                # if all external checks are ok but not internal checks, we need to fix
                # internal checks
                elif all(external_checks.values()) and not all(
                    internal_checks.values()
                ):
                    # a call to fix endpoint is needed because all external checks are ok
                    dimail_response = self.fix_domain(domain)
                    # we need to check again if all internal and external checks are ok
                    external_checks = self._get_dimail_checks(
                        dimail_response, internal=False
                    )
                    internal_checks = self._get_dimail_checks(
                        dimail_response, internal=True
                    )
                    if all(external_checks.values()) and all(internal_checks.values()):
                        domain.status = enums.MailDomainStatusChoices.ENABLED
                        domain.last_check_details = dimail_response
                        domain.save()
                    elif all(external_checks.values()) and not all(
                        internal_checks.values()
                    ):
                        domain.status = enums.MailDomainStatusChoices.FAILED
                        domain.last_check_details = dimail_response
                        domain.save()

            # if no health check data is stored on the domain, we store it now
            if not domain.last_check_details:
                domain.last_check_details = dimail_response
                domain.save()

        return dimail_response

    def _get_dimail_checks(self, dimail_response, internal: bool):
        checks = {
            key: value
            for key, value in dimail_response.items()
            if isinstance(value, dict) and value.get("internal") is internal
        }
        return {key: value.get("ok", False) for key, value in checks.items()}

    def fetch_domain_expected_config(self, domain):
        """Send a request to dimail to get domain specification for DNS configuration."""
        try:
            response = session.get(
                f"{self.API_URL}/domains/{domain.name}/spec/",
                headers={"Authorization": f"Basic {self.API_CREDENTIALS}"},
                verify=True,
                timeout=self.API_TIMEOUT,
            )
        except requests.exceptions.ConnectionError as error:
            logger.exception(
                "Connection error while trying to reach %s.",
                self.API_URL,
                exc_info=error,
            )
            return []
        if response.status_code == status.HTTP_200_OK:
            # format the response to log an error if api response changed
            try:
                dimail_expected_config = [
                    {
                        "target": item["target"],
                        "type": item["type"],
                        "value": item["value"],
                    }
                    for item in response.json()
                ]
                domain.expected_config = dimail_expected_config
                domain.save()
                return dimail_expected_config
            except KeyError as error:
                logger.exception(
                    "[DIMAIL] spec expected response format changed: %s",
                    error,
                )
                return []
        else:
            logger.exception(
                "[DIMAIL] unexpected error : %s %s",
                response.status_code,
                response.content,
                exc_info=False,
            )
            return []

    def reset_password(self, mailbox):
        """Send a request to reset mailbox password."""
        if not mailbox.secondary_email or mailbox.secondary_email == str(mailbox):
            raise exceptions.ValidationError(
                "Password reset requires a secondary email address. Please add a valid secondary email before trying again."
            )

        try:
            response = session.post(
                f"{self.API_URL}/domains/{mailbox.domain.name}/mailboxes/{mailbox.local_part}/reset_password/",
                headers={"Authorization": f"Basic {self.API_CREDENTIALS}"},
                verify=True,
                timeout=self.API_TIMEOUT,
            )
        except requests.exceptions.ConnectionError as error:
            logger.exception(
                "Connection error while trying to reach %s.",
                self.API_URL,
                exc_info=error,
            )
            raise error

        if response.status_code == status.HTTP_200_OK:
            # send new password to secondary email
            self.notify_mailbox_password_reset(
                recipient=mailbox.secondary_email,
                mailbox_data={
                    "email": response.json()["email"],
                    "password": response.json()["password"],
                },
            )
            logger.info(
                "[DIMAIL] Password reset on mailbox %s.",
                mailbox,
            )
            return response
        return self.raise_exception_for_unexpected_response(response)
