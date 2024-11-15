"""
Tests for Service Provider API endpoint in People's core app: retrieve
"""

import pytest
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND

from core import factories

pytestmark = pytest.mark.django_db


def test_api_service_providers_retrieve_anonymous(client):
    """Anonymous users should not be allowed to retrieve service providers."""
    service_provider = factories.ServiceProviderFactory()

    response = client.get(f"/api/v1.0/service-providers/{service_provider.pk}/")

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_service_providers_retrieve_authenticated_allowed(client):
    """
    Authenticated users should be able to retrieve service providers
    of their organization.
    """
    user = factories.UserFactory(with_organization=True)
    client.force_login(user)

    service_provider = factories.ServiceProviderFactory(
        organizations=[user.organization]
    )

    response = client.get(f"/api/v1.0/service-providers/{service_provider.pk}/")

    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "audience_id": str(service_provider.audience_id),
        "id": str(service_provider.pk),
        "name": service_provider.name,
    }


def test_api_service_providers_retrieve_authenticated_other_organization(client):
    """
    Authenticated users should not be able to retrieve service providers
    of other organization.
    """
    user = factories.UserFactory(with_organization=True)
    client.force_login(user)

    service_provider = factories.ServiceProviderFactory(
        organizations=[factories.OrganizationFactory(with_registration_id=True)]
    )

    response = client.get(f"/api/v1.0/service-providers/{service_provider.pk}/")

    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No ServiceProvider matches the given query."}


def test_api_service_providers_retrieve_authenticated_on_teams(client):
    """
    Authenticated users should not be able to retrieve service providers
    just because it is related to one of their teams if it is not related
    to their organization (might change later if needed).
    """
    user = factories.UserFactory(with_organization=True)
    client.force_login(user)

    other_organization = factories.OrganizationFactory(with_registration_id=True)
    service_provider = factories.ServiceProviderFactory()
    factories.TeamFactory(
        users=[user],
        organization=other_organization,
        service_providers=[service_provider],
    )

    response = client.get(f"/api/v1.0/service-providers/{service_provider.pk}/")

    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No ServiceProvider matches the given query."}
