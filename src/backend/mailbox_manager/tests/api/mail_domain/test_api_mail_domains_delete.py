"""
Tests for MailDomains API endpoint, in People's mailbox manager app. Focus on "delete" action.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import factories, models

pytestmark = pytest.mark.django_db


def test_api_mail_domains__delete_anonymous():
    """Anonymous users should not be allowed to destroy a domain."""
    domain = factories.MailDomainFactory()

    response = APIClient().delete(
        f"/api/v1.0/mail-domains/{domain.slug}/",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert models.MailDomain.objects.count() == 1


def test_api_mail_domains__delete_authenticated():
    """
    Delete a domain is not allowed.
    """
    user = core_factories.UserFactory()
    domain = factories.MailDomainFactory()

    client = APIClient()
    client.force_login(user)
    response = client.delete(
        f"/api/v1.0/mail-domains/{domain.slug}/",
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert models.MailDomain.objects.count() == 1
