"""
Unit tests for the mailbox API
"""

import json
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
from mailbox_manager.tests.fixtures.dimail import (
    TOKEN_OK,
    response_mailbox_created,
)

pytestmark = pytest.mark.django_db


def test_api_mailboxes__update_anonymous_forbidden():
    """Anonymous users should not be able to update a mailbox via the API."""
    mailbox = factories.MailboxFactory()
    saved_secondary = mailbox.secondary_email
    import pdb

    pdb.set_trace()
    APIClient().get(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/"
    )
    response = APIClient().patch(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/",
        {"secondary_email": "new_secondary@newdomain.fr"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    mailbox.refresh_from_db()
    assert mailbox.secondary_email == saved_secondary


def test_api_mailboxes__update_authenticated_failure():
    """Authenticated but unauthoriezd users should not be able to update mailbox."""
    client = APIClient()
    client.force_login(core_factories.UserFactory())

    mailbox = factories.MailboxFactory()
    saved_secondary = mailbox.secondary_email
    response = client.patch(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/",
        {"secondary_email": "new_secondary@newdomain.fr"},
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mailbox.refresh_from_db()
    assert mailbox.secondary_email == saved_secondary
