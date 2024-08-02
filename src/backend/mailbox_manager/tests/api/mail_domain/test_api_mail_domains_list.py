"""
Tests for MailDomains API endpoint in People's mailbox manager app. Focus on "list" action.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import factories

pytestmark = pytest.mark.django_db


def test_api_mail_domains__list_anonymous():
    """Anonymous users should not be allowed to list mail domains."""

    factories.MailDomainFactory.create_batch(3)

    response = APIClient().get("/api/v1.0/mail-domains/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_mail_domains__list_authenticated():
    """
    Authenticated users should be able to list domains
    to which they have access.
    """

    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    expected_ids = {
        str(access.domain.id)
        for access in factories.MailDomainAccessFactory.create_batch(5, user=user)
    }
    factories.MailDomainFactory.create_batch(2)  # Other domains
    factories.MailDomainAccessFactory.create_batch(2)  # Other domains and accesses

    response = client.get(
        "/api/v1.0/mail-domains/",
    )

    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 5
    results_id = {result["id"] for result in results}
    assert expected_ids == results_id
