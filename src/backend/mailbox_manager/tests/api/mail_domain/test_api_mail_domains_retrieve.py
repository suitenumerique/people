"""
Tests for MailDomains API endpoint in People's mailbox manager app. Focus on "retrieve" action.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import factories

pytestmark = pytest.mark.django_db


def test_api_mail_domains__retrieve_anonymous():
    """Anonymous users should not be allowed to retrieve a domain."""

    domain = factories.MailDomainEnabledFactory()
    response = APIClient().get(f"/api/v1.0/mail-domains/{domain.slug}/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_domains__retrieve_non_existing():
    """
    Authenticated users should have an explicit error when trying to retrive
    a domain that doesn't exist.
    """
    client = APIClient()
    client.force_login(core_factories.UserFactory())

    response = client.get(
        "/api/v1.0/mail-domains/nonexistent.domain/",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Not found."}


def test_api_mail_domains__retrieve_authenticated_unrelated():
    """
    Authenticated users should not be allowed to retrieve a domain
    to which they have access.
    """
    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    domain = factories.MailDomainEnabledFactory()

    response = client.get(
        f"/api/v1.0/mail-domains/{domain.slug}/",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No MailDomain matches the given query."}


def test_api_mail_domains__retrieve_authenticated_related():
    """
    Authenticated users should be allowed to retrieve a domain
    to which they have access.
    """
    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    domain = factories.MailDomainEnabledFactory()
    factories.MailDomainAccessFactory(domain=domain, user=user)
    factories.MailboxFactory.create_batch(10, domain=domain)

    response = client.get(
        f"/api/v1.0/mail-domains/{domain.slug}/",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(domain.id),
        "name": domain.name,
        "slug": domain.slug,
        "status": domain.status,
        "created_at": domain.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": domain.updated_at.isoformat().replace("+00:00", "Z"),
        "abilities": domain.get_abilities(user),
        "count_mailboxes": 10,
    }
