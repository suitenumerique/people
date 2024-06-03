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

    domain = factories.MailDomainFactory()
    response = APIClient().get(f"/api/v1.0/mail-domains/{domain.slug}/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_mail_domains__retrieve_authenticated_unrelated():
    """
    Authenticated users should not be allowed to retrieve a domain
    to which they have access.
    """
    identity = core_factories.IdentityFactory()

    client = APIClient()
    client.force_login(identity.user)

    domain = factories.MailDomainFactory()

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
    identity = core_factories.IdentityFactory()
    user = identity.user

    client = APIClient()
    client.force_login(user)

    domain = factories.MailDomainFactory()
    factories.MailDomainAccessFactory(domain=domain, user=user)

    response = client.get(
        f"/api/v1.0/mail-domains/{domain.slug}/",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(domain.id),
        "name": domain.name,
        "created_at": domain.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": domain.updated_at.isoformat().replace("+00:00", "Z"),
    }
