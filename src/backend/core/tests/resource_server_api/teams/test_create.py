"""
Tests for Teams API endpoint in People's core app: create
"""

import pytest
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_401_UNAUTHORIZED,
)
from rest_framework.test import APIClient

from core.factories import OrganizationFactory, ServiceProviderFactory, UserFactory
from core.models import ServiceProvider, Team

pytestmark = pytest.mark.django_db


def test_api_teams_create_anonymous():
    """Anonymous users should not be allowed to create teams."""
    response = APIClient().post(
        "/resource-server/v1.0/teams/",
        {
            "name": "my team",
        },
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert not Team.objects.exists()


def test_api_teams_create_authenticated_new_service_provider(
    client, force_login_via_resource_server
):
    """
    Authenticated users should be able to create teams and should automatically be declared
    as the owner of the newly created team and a new service provider should be created and
    associated to the team.
    """
    organization = OrganizationFactory(with_registration_id=True)
    user = UserFactory(organization=organization)
    assert ServiceProvider.objects.count() == 0

    with force_login_via_resource_server(client, user, "some_service_provider"):
        response = client.post(
            "/resource-server/v1.0/teams/",
            {
                "name": "my team",
            },
            format="json",
            HTTP_AUTHORIZATION="Bearer b64untestedbearertoken",
        )

    assert response.status_code == HTTP_201_CREATED

    team = Team.objects.get()
    team_access = team.accesses.get()
    service_provider = ServiceProvider.objects.get()  # service provider created

    assert response.json() == {
        "created_at": team.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "id": str(team.pk),
        "is_visible_all_services": False,
        "depth": team.depth,
        "name": "my team",
        "numchild": team.numchild,
        "path": team.path,
        "updated_at": team.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }

    # check team data
    assert team.name == "my team"
    assert team.organization == organization

    # check team access data
    assert team_access.role == "owner"
    assert team_access.user == user

    # check service provider data
    assert service_provider.audience_id == "some_service_provider"


def test_api_teams_create_authenticated_existing_service_provider(
    client,
    force_login_via_resource_server,
):
    """
    Authenticated users should be able to create teams and should automatically be declared
    as the owner of the newly created team and an existing service provider should be associated
    to the team.
    """
    user = UserFactory()
    service_provider = ServiceProviderFactory()
    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.post(
            "/resource-server/v1.0/teams/",
            {
                "name": "my team",
            },
            format="json",
            HTTP_AUTHORIZATION="Bearer b64untestedbearertoken",
        )

    assert response.status_code == HTTP_201_CREATED

    assert ServiceProvider.objects.count() == 1  # no object created
    team = Team.objects.get()  # team created
    assert team.service_providers.get().audience_id == service_provider.audience_id
    assert team.name == "my team"
    assert team.accesses.filter(role="owner", user=user).exists()


def test_api_teams_create_cannot_override_organization(
    client, force_login_via_resource_server
):
    """
    Authenticated users should be able to create teams and not
    be able to set the organization manually (for now).
    """
    organization = OrganizationFactory(with_registration_id=True)
    user = UserFactory(organization=organization)
    service_provider = ServiceProviderFactory()

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.post(
            "/resource-server/v1.0/teams/",
            {
                "name": "my team",
                "organization": OrganizationFactory(
                    with_registration_id=True
                ).pk,  # ignored
            },
            format="json",
        )

    assert response.status_code == HTTP_201_CREATED
    team = Team.objects.get()
    assert team.name == "my team"
    assert team.organization == organization
    assert team.accesses.filter(role="owner", user=user).exists()


def test_api_teams_create_cannot_override_service_provider(
    client, force_login_via_resource_server
):
    """
    Authenticated users should be able to create teams and not
    be able to set the team service provider manually.
    """
    user = UserFactory(with_organization=True)
    service_provider = ServiceProviderFactory()

    other_service_provider = ServiceProviderFactory()
    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.post(
            "/resource-server/v1.0/teams/",
            {
                "name": "my team",
                "service_providers": [str(other_service_provider.pk)],  # ignored
            },
            format="json",
        )

    assert response.status_code == HTTP_201_CREATED

    team = Team.objects.get()
    assert team.name == "my team"
    assert team.service_providers.get().audience_id == service_provider.audience_id


def test_api_teams_create_is_visible_all_services_team(
    client, force_login_via_resource_server
):
    """
    Authenticated users should be able to create teams visible in all service providers.
    """
    user = UserFactory()
    service_provider = ServiceProviderFactory()

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.post(
            "/resource-server/v1.0/teams/",
            {
                "name": "my team",
                "is_visible_all_services": True,
            },
            format="json",
        )

    assert response.status_code == HTTP_201_CREATED
    team = Team.objects.get()
    assert team.is_visible_all_services is True


def test_api_teams_create_restricted_team(client, force_login_via_resource_server):
    """Authenticated users should be able to create teams restricted to some service providers."""
    user = UserFactory()
    service_provider = ServiceProviderFactory()

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.post(
            "/resource-server/v1.0/teams/",
            {
                "name": "my team",
            },
            format="json",
        )

    assert response.status_code == HTTP_201_CREATED
    team = Team.objects.get()
    assert team.is_visible_all_services is False
