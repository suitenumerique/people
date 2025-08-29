"""
Unit tests for the mailbox API
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import factories

pytestmark = pytest.mark.django_db


def test_api_mailboxes__retrieve_anonymous_forbidden():
    """Anonymous users should not be able to retrieve a new mailbox via the API."""
    mailbox = factories.MailboxFactory()
    response = APIClient().get(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_api_mailboxes__retrieve_unauthorized_failure():
    """Authenticated but unauthorized users should not be able to
    retrieve mailbox."""
    client = APIClient()
    client.force_login(core_factories.UserFactory())

    mailbox = factories.MailboxFactory()
    response = client.get(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/"
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    # 403 or 404 for confidentiality/security purposes ?

    # response should be the same whether the mailbox exists or not, so that
    # unauthorized users can't deduce mailbox existence or nonexistence
    response = client.get(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/thismailboxdoesntexist/"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_api_mailboxes__retrieve_authorized_ok():
    """Authorized users should be able to retrieve mailboxes."""

    access = factories.MailDomainAccessFactory()
    mailbox = factories.MailboxFactory(domain=access.domain)

    client = APIClient()
    client.force_login(access.user)
    response = client.get(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(mailbox.id),
        "first_name": mailbox.first_name,
        "last_name": mailbox.last_name,
        "local_part": mailbox.local_part,
        "secondary_email": mailbox.secondary_email,
        "status": mailbox.status,
    }


def test_api_mailboxes__owner_not_authorized():
    """Unauthorized mailbox owner should not be able to retrieve their mailbox."""
    mailbox = factories.MailboxFactory()
    user = core_factories.UserFactory(email=str(mailbox))

    client = APIClient()
    client.force_login(user)
    response = client.get(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/"
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
