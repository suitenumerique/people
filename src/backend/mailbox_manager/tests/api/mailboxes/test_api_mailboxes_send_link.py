"""
Unit tests for the login link endpoint
"""

import logging
from unittest import mock

from django.conf import settings
from django.test import override_settings

import pytest
import responses
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories
from mailbox_manager.tests.fixtures import dimail as dimail_responses

pytestmark = pytest.mark.django_db


def test_api_mailboxes__login_link_anonymous_unauthorized():
    """Anonymous users should not be able to ask for a login link."""
    mailbox = factories.MailboxFactory(status=enums.MailboxStatusChoices.ENABLED)
    response = APIClient().post(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/login_link/",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_api_mailboxes__login_link_no_access_forbidden_not_found():
    """Authenticated users not managing the domain
    should not be able to get login link for any mailbox."""
    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    mailbox = factories.MailboxFactory(status=enums.MailboxStatusChoices.ENABLED)

    response = client.post(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/login_link/"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "No MailDomain matches the given query.",
    }


def test_api_mailboxes__login_link_viewer_forbidden():
    """Domain viewers should not be able to get login link on mailboxes."""
    viewer_access = factories.MailDomainAccessFactory(
        role=enums.MailDomainRoleChoices.VIEWER
    )

    client = APIClient()
    client.force_login(viewer_access.user)

    # another user's mailbox
    mailbox = factories.MailboxEnabledFactory(domain=viewer_access.domain)
    response = client.post(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/login_link/"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "You do not have permission to perform this action."
    }


def test_api_mailboxes__login_link_no_secondary_email():
    """Should not try to get login link if no secondary email is specified."""
    mail_domain = factories.MailDomainEnabledFactory()
    access = factories.MailDomainAccessFactory(
        role=enums.MailDomainRoleChoices.OWNER, domain=mail_domain
    )
    client = APIClient()
    client.force_login(access.user)

    error = "Logging in with a link requires a secondary email address. \
Please add a valid secondary email before trying again."

    # Mailbox with no secondary email
    mailbox = factories.MailboxEnabledFactory(domain=mail_domain, secondary_email=None)
    response = client.post(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/{mailbox.pk}/login_link/"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == [error]

    # Mailbox with empty secondary email
    mailbox = factories.MailboxEnabledFactory(domain=mail_domain, secondary_email="")
    response = client.post(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/{mailbox.pk}/login_link/"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == [error]

    # Mailbox with primary email as secondary email
    mailbox = factories.MailboxEnabledFactory(domain=mail_domain)
    mailbox.secondary_email = str(mailbox)
    mailbox.save()
    response = client.post(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/{mailbox.pk}/login_link/"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == [error]


@pytest.mark.parametrize(
    "role",
    [
        enums.MailDomainRoleChoices.OWNER,
        enums.MailDomainRoleChoices.ADMIN,
    ],
)
@responses.activate
@override_settings(WEBMAIL_URL="https://webmail.fr")
def test_api_mailboxes__login_link_admin_successful(role, dimail_token_ok, caplog):  # pylint: disable=W0613
    """Owner and admin users should be able to request login link for any mailboxes.
    Login links should be sent to secondary email."""
    caplog.set_level(logging.INFO)
    mailbox = factories.MailboxEnabledFactory()

    access = factories.MailDomainAccessFactory(role=role, domain=mailbox.domain)
    client = APIClient()
    client.force_login(access.user)

    dimail_responses.response_login_code_ok(mailbox.domain, mailbox.local_part)
    with mock.patch("django.core.mail.send_mail") as mock_send:
        response = client.post(
            f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/login_link/"
        )

    assert mock_send.call_count == 1
    assert "Here is your login link" in mock_send.mock_calls[0][1][1]
    assert "https://webmail.fr/code/OneTimeCode" in mock_send.mock_calls[0][1][1]
    assert mailbox.password not in mock_send.mock_calls[0][1][1]
    assert mock_send.mock_calls[0][1][3][0] == mailbox.secondary_email
    assert response.status_code == status.HTTP_200_OK


def test_api_mailboxes__login_link_non_existing():
    """
    User gets a 404 when trying to get login link of a mailbox which does not exist.
    """
    user = core_factories.UserFactory()
    client = APIClient()
    client.force_login(user)

    response = client.get("/api/v1.0/mail-domains/nonexistent.domain/mailboxes/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@responses.activate
def test_api_mailboxes__login_link_connexion_failed(dimail_token_ok):  # pylint: disable=W0613
    """
    No mail is sent when login link request failed because of connexion error.
    """
    mail_domain = factories.MailDomainEnabledFactory()
    mailbox = factories.MailboxEnabledFactory(domain=mail_domain)

    access = factories.MailDomainAccessFactory(
        role=enums.MailDomainRoleChoices.OWNER, domain=mail_domain
    )
    client = APIClient()
    client.force_login(access.user)

    dimail_url = settings.MAIL_PROVISIONING_API_URL
    # token response in fixtures
    responses.add(
        responses.POST,
        f"{dimail_url}/domains/{mail_domain.name}/mailboxes/{mailbox.local_part}/code/",
        body=ConnectionError(),
    )

    with mock.patch("django.core.mail.send_mail") as mock_send:
        with pytest.raises(ConnectionError):
            client.post(
                f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/{mailbox.pk}/login_link/"
            )
        assert mock_send.call_count == 0
