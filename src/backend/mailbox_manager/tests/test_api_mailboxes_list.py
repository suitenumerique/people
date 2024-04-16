"""
Unit tests for the mailbox API
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import factories

pytestmark = pytest.mark.django_db


def test_api_mailboxes__list_anonymous():
    """Anonymous users should not be allowed to list mailboxes."""
    mail_domain = factories.MailDomainFactory()
    factories.MailboxFactory.create_batch(2, domain=mail_domain)

    response = APIClient().get(f"/api/v1.0/mail-domains/{mail_domain.id}/mailboxes/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_mailboxes__list_authenticated_no_query():
    """Authenticated users should be able to list mailboxes without applying a query."""
    user = core_factories.UserFactory(admin_email="tester@ministry.fr")
    core_factories.IdentityFactory(user=user, email=user.admin_email, name="john doe")

    client = APIClient()
    client.force_login(user)

    mail_domain = factories.MailDomainFactory()
    mailbox1 = factories.MailboxFactory(domain=mail_domain)
    mailbox2 = factories.MailboxFactory(domain=mail_domain)

    response = client.get(f"/api/v1.0/mail-domains/{mail_domain.id}/mailboxes/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["results"] == [
        {
            "id": str(mailbox1.id),
            "local_part": str(mailbox1.local_part),
            "secondary_email": str(mailbox1.secondary_email),
        },
        {
            "id": str(mailbox2.id),
            "local_part": str(mailbox2.local_part),
            "secondary_email": str(mailbox2.secondary_email),
        },
    ]
