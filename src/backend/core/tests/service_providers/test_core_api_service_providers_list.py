"""
Tests for Service Provider API endpoint in People's core app: list
"""

import pytest
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED

from core import factories

pytestmark = pytest.mark.django_db


def test_api_service_providers_list_anonymous(client):
    """Anonymous users should not be allowed to list service providers."""
    factories.ServiceProviderFactory.create_batch(2)

    response = client.get("/api/v1.0/service-providers/")

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_service_providers_list_authenticated(client):
    """
    Authenticated users should be able to list service providers
    of their organization.
    """
    user = factories.UserFactory(with_organization=True)
    client.force_login(user)

    service_provider_1 = factories.ServiceProviderFactory(
        name="A", organizations=[user.organization]
    )
    service_provider_2 = factories.ServiceProviderFactory(
        name="B", organizations=[user.organization]
    )

    # Generate some not fetched data
    factories.ServiceProviderFactory.create_batch(
        2, organizations=[factories.OrganizationFactory(with_registration_id=True)]
    )  # Other service providers
    factories.TeamFactory(
        users=[user], service_providers=[factories.ServiceProviderFactory()]
    )

    response = client.get(
        "/api/v1.0/service-providers/",
    )

    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "count": 2,
        "next": None,
        "previous": None,
        "results": [
            {
                "audience_id": str(service_provider_1.audience_id),
                "id": str(service_provider_1.pk),
                "name": "A",
            },
            {
                "audience_id": str(service_provider_2.audience_id),
                "id": str(service_provider_2.pk),
                "name": "B",
            },
        ],
    }


def test_api_service_providers_order(client):
    """Test that the service providers are sorted as requested."""
    user = factories.UserFactory(with_organization=True)
    factories.ServiceProviderFactory(name="A", organizations=[user.organization])
    factories.ServiceProviderFactory(name="B", organizations=[user.organization])

    client.force_login(user)

    # Test ordering by name descending
    response = client.get("/api/v1.0/service-providers/?ordering=-name")
    assert response.status_code == 200
    response_data = response.json()["results"]
    assert response_data[0]["name"] == "B"
    assert response_data[1]["name"] == "A"

    # Test ordering by creation date ascending
    response = client.get("/api/v1.0/service-providers/?ordering=created_at")
    response_data = response.json()["results"]
    assert response_data[0]["name"] == "A"
    assert response_data[1]["name"] == "B"
