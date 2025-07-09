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
