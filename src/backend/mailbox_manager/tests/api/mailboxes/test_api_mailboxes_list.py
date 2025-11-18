"""
Unit tests for the mailbox API
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories

pytestmark = pytest.mark.django_db


def test_api_mailboxes__list_anonymous():
    """Anonymous users should not be allowed to list mailboxes."""
    mail_domain = factories.MailDomainEnabledFactory()
    factories.MailboxFactory.create_batch(2, domain=mail_domain)

    response = APIClient().get(f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_mailboxes__list_unrelated_not_found():
    """Unrelated users should not be able to list mailboxes"""
    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    mail_domain = factories.MailDomainEnabledFactory()
    factories.MailboxFactory.create_batch(2, domain=mail_domain)

    response = client.get(f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No MailDomain matches the given query."}


@pytest.mark.parametrize(
    "role",
    [
        enums.MailDomainRoleChoices.OWNER,
        enums.MailDomainRoleChoices.ADMIN,
        enums.MailDomainRoleChoices.VIEWER,
    ],
)
def test_api_mailboxes__list_roles(role):
    """Owner, admin and viewer users should be able to list mailboxes"""
    mail_domain = factories.MailDomainEnabledFactory()
    mailbox1 = factories.MailboxEnabledFactory(domain=mail_domain)
    mailbox2 = factories.MailboxEnabledFactory(domain=mail_domain)

    access = factories.MailDomainAccessFactory(role=role, domain=mail_domain)
    client = APIClient()
    client.force_login(access.user)

    response = client.get(f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["results"] == [
        {
            "id": str(mailbox2.id),
            "first_name": str(mailbox2.first_name),
            "last_name": str(mailbox2.last_name),
            "local_part": str(mailbox2.local_part),
            "secondary_email": str(mailbox2.secondary_email),
            "status": enums.MailboxStatusChoices.ENABLED,
        },
        {
            "id": str(mailbox1.id),
            "first_name": str(mailbox1.first_name),
            "last_name": str(mailbox1.last_name),
            "local_part": str(mailbox1.local_part),
            "secondary_email": str(mailbox1.secondary_email),
            "status": enums.MailboxStatusChoices.ENABLED,
        },
    ]


def test_api_mailboxes__list_non_existing():
    """
    User gets a 404 when trying to list mailboxes of a domain which does not exist.
    """
    user = core_factories.UserFactory()
    client = APIClient()
    client.force_login(user)

    factories.MailboxFactory.create_batch(5)

    response = client.get("/api/v1.0/mail-domains/nonexistent.domain/mailboxes/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
