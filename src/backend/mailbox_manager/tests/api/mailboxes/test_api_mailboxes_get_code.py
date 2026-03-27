"""
Unit tests for the reset password mailbox API
"""

from unittest import mock

from django.conf import settings

import pytest
import responses
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories
from mailbox_manager.tests.fixtures import dimail

pytestmark = pytest.mark.django_db


def test_api_mailboxes__get_code_anonymous_unauthorized():
    """Anonymous users should not be able to ask for a connexion code."""
    mailbox = factories.MailboxFactory(status=enums.MailboxStatusChoices.ENABLED)
    response = APIClient().post(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/get_code/",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_api_mailboxes__get_code_no_access_forbidden_not_found():
    """Authenticated users not managing the domain
    should not be able to get connexion code from any mailbox."""
    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    mailbox = factories.MailboxFactory(status=enums.MailboxStatusChoices.ENABLED)

    response = client.post(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/get_code/"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "No MailDomain matches the given query.",
    }


def test_api_mailboxes__get_code_viewer_forbidden():
    """Domain viewers should not be able to get connexion code on mailboxes,
    except on their own mailbox."""
    viewer_access = factories.MailDomainAccessFactory(
        role=enums.MailDomainRoleChoices.VIEWER
    )

    client = APIClient()
    client.force_login(viewer_access.user)

    # another user's mailbox
    mailbox = factories.MailboxEnabledFactory(domain=viewer_access.domain)
    response = client.post(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/get_code/"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "You do not have permission to perform this action."
    }

    # viewer's own mailbox
    import pdb

    pdb.set_trace()
    self_mailbox = factories.MailboxEnabledFactory(
        domain=viewer_access.domain, local_part=viewer_access.user.email.split("@")[0]
    )
    response = client.post(
        f"/api/v1.0/mail-domains/{self_mailbox.domain.slug}/mailboxes/{self_mailbox.pk}/get_code/"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "detail": "You do not have permission to perform this action."
    }


def test_api_mailboxes__get_code_no_secondary_email():
    """Should not try to get connexion code if no secondary email is specified."""
    mail_domain = factories.MailDomainEnabledFactory()
    access = factories.MailDomainAccessFactory(
        role=enums.MailDomainRoleChoices.OWNER, domain=mail_domain
    )
    client = APIClient()
    client.force_login(access.user)

    error = "Login by code requires a secondary email address. \
Please add a valid secondary email before trying again."

    # Mailbox with no secondary email
    mailbox = factories.MailboxEnabledFactory(domain=mail_domain, secondary_email=None)
    response = client.post(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/{mailbox.pk}/get_code/"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == [error]

    # Mailbox with empty secondary email
    mailbox = factories.MailboxEnabledFactory(domain=mail_domain, secondary_email="")
    response = client.post(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/{mailbox.pk}/get_code/"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == [error]

    # Mailbox with primary email as secondary email
    mailbox = factories.MailboxEnabledFactory(domain=mail_domain)
    mailbox.secondary_email = str(mailbox)
    mailbox.save()
    response = client.post(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/{mailbox.pk}/get_code/"
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
def test_api_mailboxes__get_code_admin_successful(role, dimail_token_ok):  # pylint: disable=W0613
    """Owner and admin users should be able to get connexion code on mailboxes.
    Connexion code should be sent to secondary email."""
    mail_domain = factories.MailDomainEnabledFactory()
    mailbox = factories.MailboxEnabledFactory(domain=mail_domain)

    access = factories.MailDomainAccessFactory(role=role, domain=mail_domain)
    client = APIClient()
    client.force_login(access.user)
    dimail_url = settings.MAIL_PROVISIONING_API_URL

    # token response in fixtures
    responses.add(
        responses.POST,
        f"{dimail_url}/domains/{mail_domain.name}/mailboxes/{mailbox.local_part}/get_code/",
        body=dimail.response_mailbox_created(str(mailbox)),
        status=200,
    )
    with mock.patch("django.core.mail.send_mail") as mock_send:
        response = client.post(
            f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/{mailbox.pk}/get_code/"
        )

        assert mock_send.call_count == 1
        assert "Your password has been updated" in mock_send.mock_calls[0][1][1]
        assert mock_send.mock_calls[0][1][3][0] == mailbox.secondary_email

    assert response.status_code == status.HTTP_200_OK


def test_api_mailboxes__get_code_non_existing():
    """
    User gets a 404 when trying to get connexion code of mailbox which does not exist.
    """
    user = core_factories.UserFactory()
    client = APIClient()
    client.force_login(user)

    response = client.get("/api/v1.0/mail-domains/nonexistent.domain/mailboxes/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@responses.activate
def test_api_mailboxes__get_code_connexion_failed(dimail_token_ok):  # pylint: disable=W0613
    """
    No mail is sent when connexion code request failed because of connexion error.
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
        f"{dimail_url}/domains/{mail_domain.name}/mailboxes/{mailbox.local_part}/get_code/",
        body=ConnectionError(),
    )

    with pytest.raises(ConnectionError):
        with mock.patch("django.core.mail.send_mail") as mock_send:
            client.post(
                f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/{mailbox.pk}/get_code/"
            )
        assert mock_send.call_count == 0
