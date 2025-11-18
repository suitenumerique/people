"""
Unit tests for the mailbox API
"""

import re

import pytest
import responses
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories, models

pytestmark = pytest.mark.django_db


def test_api_mailboxes__enable_anonymous_forbidden():
    """Anonymous users should not be able to enable a mailbox via the API."""
    mailbox = factories.MailboxFactory(status=enums.MailboxStatusChoices.DISABLED)
    response = APIClient().post(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/enable/",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert models.Mailbox.objects.get().status == enums.MailboxStatusChoices.DISABLED


def test_api_mailboxes__enable_unrelated_not_found():
    """Unrelated users should not be able to enable mailbox."""
    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    mailbox = factories.MailboxFactory(status=enums.MailboxStatusChoices.DISABLED)
    response = client.post(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/enable/",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert models.Mailbox.objects.get().status == enums.MailboxStatusChoices.DISABLED


def test_api_mailboxes__enable_viewer_failure():
    """Users with viewer role should not be able to enable mailbox on the mail domain."""
    mailbox = factories.MailboxFactory(status=enums.MailboxStatusChoices.DISABLED)
    access = factories.MailDomainAccessFactory(
        role=enums.MailDomainRoleChoices.VIEWER, domain=mailbox.domain
    )

    client = APIClient()
    client.force_login(access.user)

    response = client.post(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/enable/",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert models.Mailbox.objects.get().status == enums.MailboxStatusChoices.DISABLED


@pytest.mark.parametrize(
    "role",
    [enums.MailDomainRoleChoices.OWNER, enums.MailDomainRoleChoices.ADMIN],
)
def test_api_mailboxes__enable_roles_success(role):
    """Users with owner or admin role should be able to enable mailbox on the mail domain."""
    mailbox = factories.MailboxFactory(status=enums.MailboxStatusChoices.DISABLED)
    access = factories.MailDomainAccessFactory(role=role, domain=mailbox.domain)

    client = APIClient()
    client.force_login(access.user)

    with responses.RequestsMock() as rsps:
        # Ensure successful response using "responses":
        rsps.add(
            rsps.GET,
            re.compile(r".*/token/"),
            body='{"access_token": "domain_owner_token"}',
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        rsps.add(
            rsps.PATCH,
            re.compile(
                rf".*/domains/{mailbox.domain.name}/mailboxes/{mailbox.local_part}"
            ),
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        response = client.post(
            f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/enable/",
        )
    assert response.status_code == status.HTTP_200_OK
    mailbox = models.Mailbox.objects.get()

    assert mailbox.status == enums.MailboxStatusChoices.ENABLED
