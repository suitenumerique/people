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


def test_api_mailboxes__reset_password_anonymous_unauthorized():
    """Anonymous users should not be able to reset mailboxes password."""
    mailbox = factories.MailboxFactory(status=enums.MailboxStatusChoices.ENABLED)
    response = APIClient().post(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/reset_password/",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_api_mailboxes__reset_password_unrelated_forbidden():
    """Authenticated users not managing the domain
    should not be able to reset its mailboxes password."""
    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    mailbox = factories.MailboxFactory(status=enums.MailboxStatusChoices.ENABLED)

    response = client.post(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/reset_password/"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "You do not have permission to perform this action."
    }


def test_api_mailboxes__reset_password_viewer_forbidden():
    """Domain viewers should not be able to reset passwords on mailboxes."""
    mailbox = factories.MailboxEnabledFactory()
    viewer_access = factories.MailDomainAccessFactory(
        role=enums.MailDomainRoleChoices.VIEWER, domain=mailbox.domain
    )

    client = APIClient()
    client.force_login(viewer_access.user)

    response = client.post(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/reset_password/"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "You do not have permission to perform this action."
    }


def test_api_mailboxes__reset_password_no_secondary_email():
    """Should not try to reset password if no secondary email is specified."""
    mail_domain = factories.MailDomainEnabledFactory()
    access = factories.MailDomainAccessFactory(
        role=enums.MailDomainRoleChoices.OWNER, domain=mail_domain
    )
    client = APIClient()
    client.force_login(access.user)

    error = "Password reset requires a secondary email address. \
Please add a valid secondary email before trying again."

    # Mailbox with no secondary email
    mailbox = factories.MailboxEnabledFactory(domain=mail_domain, secondary_email=None)
    response = client.post(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/{mailbox.pk}/reset_password/"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == [error]

    # Mailbox with empty secondary email
    mailbox = factories.MailboxEnabledFactory(domain=mail_domain, secondary_email="")
    response = client.post(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/{mailbox.pk}/reset_password/"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == [error]

    # Mailbox with primary email as secondary email
    mailbox = factories.MailboxEnabledFactory(domain=mail_domain)
    mailbox.secondary_email = str(mailbox)
    mailbox.save()
    response = client.post(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/{mailbox.pk}/reset_password/"
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
def test_api_mailboxes__reset_password_admin_successful(role):
    """Owner and admin users should be able to reset password on mailboxes.
    New password should be sent to secondary email."""
    mail_domain = factories.MailDomainEnabledFactory()
    mailbox = factories.MailboxEnabledFactory(domain=mail_domain)

    access = factories.MailDomainAccessFactory(role=role, domain=mail_domain)
    client = APIClient()
    client.force_login(access.user)
    dimail_url = settings.MAIL_PROVISIONING_API_URL

    responses.add(
        responses.POST,
        f"{dimail_url}/domains/{mail_domain.name}/mailboxes/{mailbox.local_part}/reset_password/",
        body=dimail.response_mailbox_created(str(mailbox)),
        status=200,
    )
    with mock.patch("django.core.mail.send_mail") as mock_send:
        response = client.post(
            f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/{mailbox.pk}/reset_password/"
        )

        assert mock_send.call_count == 1
        assert "Your password has been updated" in mock_send.mock_calls[0][1][1]
        assert mock_send.mock_calls[0][1][3][0] == mailbox.secondary_email

    assert response.status_code == status.HTTP_200_OK


def test_api_mailboxes__reset_password_non_existing():
    """
    User gets a 404 when trying to reset password of mailbox which does not exist.
    """
    user = core_factories.UserFactory()
    client = APIClient()
    client.force_login(user)

    response = client.get("/api/v1.0/mail-domains/nonexistent.domain/mailboxes/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@responses.activate
def test_api_mailboxes__reset_password_connexion_failed():
    """
    No mail is sent when password reset failed because of connexion error.
    """
    mail_domain = factories.MailDomainEnabledFactory()
    mailbox = factories.MailboxEnabledFactory(domain=mail_domain)

    access = factories.MailDomainAccessFactory(
        role=enums.MailDomainRoleChoices.OWNER, domain=mail_domain
    )
    client = APIClient()
    client.force_login(access.user)

    dimail_url = settings.MAIL_PROVISIONING_API_URL
    responses.add(
        responses.POST,
        f"{dimail_url}/domains/{mail_domain.name}/mailboxes/{mailbox.local_part}/reset_password/",
        body=ConnectionError(),
    )

    with pytest.raises(ConnectionError):
        with mock.patch("django.core.mail.send_mail") as mock_send:
            client.post(
                f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/{mailbox.pk}/reset_password/"
            )
        assert mock_send.call_count == 0
