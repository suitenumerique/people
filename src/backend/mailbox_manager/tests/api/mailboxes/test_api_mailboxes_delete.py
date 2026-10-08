"""
Unit tests for the mailbox API
"""
# pylint: disable=W0613, C0302


import json
import logging
import re
from logging import Logger
from unittest import mock

from django.test.utils import override_settings

import pytest
import responses
from requests.exceptions import HTTPError
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories, models
from mailbox_manager.api.client import serializers
from mailbox_manager.tests.fixtures import dimail as dimail_responses

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.django_db


def test_api_mailboxes__delete_anonymous_forbidden(mailbox_data):
    """Anonymous users should not be able to delete mailboxes via the API."""
    mailbox = factories.MailboxEnabledFactory()
    response = APIClient().delete(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert models.Mailbox.objects.exists()


def test_api_mailboxes__delete_no_access_forbidden(mailbox_data):
    """Authenticated users with no access to the domain should not be able to delete mailboxes."""
    client = APIClient()
    client.force_login(core_factories.UserFactory())

    mailbox = factories.MailboxEnabledFactory()
    response = client.delete(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert models.Mailbox.objects.exists()


def test_api_mailboxes__delete_viewer_forbidden():
    """Users with viewer role should not be able to delete mailboxes."""
    mailbox = factories.MailboxEnabledFactory()
    access = factories.MailDomainAccessFactory(
        role=enums.MailDomainRoleChoices.VIEWER, domain=mailbox.domain
    )

    client = APIClient()
    client.force_login(access.user)

    response = client.delete(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert models.Mailbox.objects.exists()


@pytest.mark.parametrize(
    "role",
    [enums.MailDomainRoleChoices.OWNER, enums.MailDomainRoleChoices.ADMIN],
)
@responses.activate
def test_api_mailboxes__delete_admins_success(role, dimail_token_ok):
    """Users with owner or admin role should be able to disable mailbox on the mail domain."""
    mailbox = factories.MailboxEnabledFactory()
    access = factories.MailDomainAccessFactory(role=role, domain=mailbox.domain)

    client = APIClient()
    client.force_login(access.user)

    # successful request for dimail token added to responses (via fixtures)
    responses.add(
        responses.DELETE,
        re.compile(
                rf".*/domains/{mailbox.domain.name}/mailboxes/{mailbox.local_part}"
            ),
        body='{"access_token": "domain_owner_token"}',
        status=status.HTTP_204_NO_CONTENT,
        content_type="application/json",
    )

    response = client.delete(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/",
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not models.Mailbox.objects.exists()
