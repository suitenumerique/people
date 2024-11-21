"""
Tests for Organizations API endpoint in People's core app: update
"""

import pytest
from rest_framework import status

from core import factories

pytestmark = pytest.mark.django_db


def test_api_organizations_update_anonymous(client):
    """Anonymous users should not be allowed to update an organization."""
    organization = factories.OrganizationFactory(with_registration_id=True)
    response = client.patch(
        f"/api/v1.0/organizations/{organization.pk}/",
        {"name": "New Name"},
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_organizations_update_authenticated_unrelated(client):
    """
    Authenticated users should not be allowed to update an organization to which they are
    not related.
    """
    user = factories.UserFactory()
    organization = factories.OrganizationFactory(with_registration_id=True)

    client.force_login(user)

    response = client.patch(
        f"/api/v1.0/organizations/{organization.pk}/",
        {"name": "New Name"},
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No Organization matches the given query."}


def test_api_organizations_update_authenticated_belong_to_organization(client):
    """
    Authenticated users should NOT be allowed to update an organization to which they
    belong to.
    """
    organization = factories.OrganizationFactory(with_registration_id=True)
    user = factories.UserFactory(organization=organization)

    client.force_login(user)

    response = client.patch(
        f"/api/v1.0/organizations/{organization.pk}/",
        {"name": "New Name"},
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "You do not have permission to perform this action."
    }


def test_api_organizations_update_authenticated_administrator(client):
    """
    Authenticated users should be allowed to update an organization
    which they administrate.
    """
    organization = factories.OrganizationFactory(
        registration_id_list=["56618615316840", "31561861231231", "98781236231482"],
        domain_list=["example.com", "example.org"],
    )
    organization_access = factories.OrganizationAccessFactory(organization=organization)
    user = organization_access.user

    client.force_login(user)

    response = client.patch(
        f"/api/v1.0/organizations/{organization.pk}/",
        {"name": "New Name"},
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(organization.pk),
        "name": "New Name",
        "abilities": {"delete": False, "get": True, "patch": True, "put": True},
        "domain_list": ["example.com", "example.org"],
        "registration_id_list": ["56618615316840", "31561861231231", "98781236231482"],
    }
