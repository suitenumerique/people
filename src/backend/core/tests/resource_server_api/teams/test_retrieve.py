"""
Tests for Teams API endpoint in People's core app: retrieve
"""

import pytest
from rest_framework import status
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.test import APIClient

from core import factories
from core.factories import TeamAccessFactory, UserFactory

pytestmark = pytest.mark.django_db


def test_api_teams_retrieve_anonymous():
    """Anonymous users should not be allowed to retrieve a team."""
    team = factories.TeamFactory()
    response = APIClient().get(f"/resource-server/v1.0/teams/{team.id}/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_teams_retrieve_authenticated_unrelated(
    client, force_login_via_resource_server
):
    """
    Authenticated users should not be allowed to retrieve a team to which they are
    not related.
    """
    user = factories.UserFactory()
    service_provider = factories.ServiceProviderFactory()

    team = factories.TeamFactory(service_providers=[service_provider])

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.get(
            f"/resource-server/v1.0/teams/{team.id!s}/",
        )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No Team matches the given query."}


def test_api_teams_retrieve_authenticated_related(
    client, force_login_via_resource_server
):
    """
    Authenticated users should be allowed to retrieve a team to which they
    are related whatever the role even if the request is authenticated via
    a resource server.
    """
    service_provider = factories.ServiceProviderFactory(
        audience_id="some_service_provider"
    )
    user = factories.UserFactory()
    team = factories.TeamFactory(users=[user], service_providers=[service_provider])

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.get(
            f"/resource-server/v1.0/teams/{team.id!s}/",
            HTTP_AUTHORIZATION="Bearer b64untestedbearertoken",
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "created_at": team.created_at.isoformat().replace("+00:00", "Z"),
        "depth": 1,
        "id": str(team.id),
        "is_visible_all_services": False,
        "name": team.name,
        "numchild": 0,
        "path": team.path,
        "updated_at": team.updated_at.isoformat().replace("+00:00", "Z"),
    }


def test_api_teams_retrieve_authenticated_other_service_provider(
    client, force_login_via_resource_server
):
    """
    Authenticated users should not be able to retrieve a team
    if the request is authenticated via a different resource server.
    """
    user = UserFactory()
    service_provider = factories.ServiceProviderFactory()

    other_service_provider = factories.ServiceProviderFactory(
        audience_id="some_service_provider"
    )
    team = factories.TeamFactory(
        users=[user], service_providers=[other_service_provider]
    )

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.get(
            f"/resource-server/v1.0/teams/{team.id!s}/",
            HTTP_AUTHORIZATION="Bearer b64untestedbearertoken",
        )

    assert response.status_code == HTTP_404_NOT_FOUND


def test_api_teams_retrieve_authenticated_related_parent_same_organization(
    client, force_login_via_resource_server
):
    """
    Authenticated users should be allowed to retrieve a parent team
    of a team to which they are related, only if they belong to the
    same organization.
    """
    organization = factories.OrganizationFactory(with_registration_id=True)
    user = factories.UserFactory(organization=organization)
    service_provider = factories.ServiceProviderFactory()

    root_team = factories.TeamFactory(
        name="Root",
        organization=organization,
    )
    first_team = factories.TeamFactory(
        name="First",
        parent_id=root_team.pk,
        organization=organization,
        service_providers=[service_provider],
    )
    second_team = factories.TeamFactory(
        name="Second",
        parent_id=first_team.pk,
        service_providers=[service_provider],
        organization=organization,
    )
    TeamAccessFactory(user=user, team=second_team, role="member")

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.get(
            f"/resource-server/v1.0/teams/{first_team.pk}/",
            HTTP_AUTHORIZATION="Bearer b64untestedbearertoken",
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "created_at": first_team.created_at.isoformat().replace("+00:00", "Z"),
        "depth": 2,
        "id": str(first_team.pk),
        "is_visible_all_services": False,
        "name": first_team.name,
        "numchild": 1,
        "path": first_team.path,
        "updated_at": first_team.updated_at.isoformat().replace("+00:00", "Z"),
    }


def test_api_teams_retrieve_authenticated_related_parent_other_organization(
    client, force_login_via_resource_server
):
    """
    Authenticated users should be allowed to retrieve a parent team
    of a team to which they are related, only if they belong to the
    same organization.
    """
    organization = factories.OrganizationFactory(with_registration_id=True)
    user = factories.UserFactory(organization=organization)
    service_provider = factories.ServiceProviderFactory()

    other_organization = factories.OrganizationFactory(with_registration_id=True)
    root_team = factories.TeamFactory(
        name="Root",
        organization=other_organization,
    )
    first_team = factories.TeamFactory(
        name="First",
        parent_id=root_team.pk,
        organization=other_organization,
        service_providers=[service_provider],
    )
    second_team = factories.TeamFactory(
        name="Second",
        parent_id=first_team.pk,
        service_providers=[service_provider],
        organization=other_organization,
    )
    TeamAccessFactory(user=user, team=second_team, role="member")

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.get(
            f"/resource-server/v1.0/teams/{first_team.pk}/",
            HTTP_AUTHORIZATION="Bearer b64untestedbearertoken",
        )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No Team matches the given query."}


def test_api_teams_retrieve_authenticated_related_child_same_organization(
    client, force_login_via_resource_server
):
    """
    Authenticated users should NOT be allowed to retrieve a child team
    of a team to which they are related, even if they belong to the
    same organization.
    """
    organization = factories.OrganizationFactory(with_registration_id=True)
    user = factories.UserFactory(organization=organization)
    service_provider = factories.ServiceProviderFactory()

    root_team = factories.TeamFactory(
        name="Root",
        organization=organization,
    )
    first_team = factories.TeamFactory(
        name="First",
        parent_id=root_team.pk,
        organization=organization,
        service_providers=[service_provider],
    )
    second_team = factories.TeamFactory(
        name="Second",
        parent_id=first_team.pk,
        service_providers=[service_provider],
        organization=organization,
    )
    TeamAccessFactory(user=user, team=first_team, role="member")

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.get(
            f"/resource-server/v1.0/teams/{second_team.pk}/",
            HTTP_AUTHORIZATION="Bearer b64untestedbearertoken",
        )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No Team matches the given query."}


def test_api_teams_retrieve_is_visible_all_services_team(
    client, force_login_via_resource_server
):
    """
    Authenticated users should be able to retrieve teams even
    if associated with the another requesting service provider.
    """
    user = factories.UserFactory()
    service_provider = factories.ServiceProviderFactory()
    other_service_provider = factories.ServiceProviderFactory()

    public_team = factories.TeamFactory(
        is_visible_all_services=True,
        service_providers=[other_service_provider],
    )
    TeamAccessFactory(user=user, team=public_team, role="member")

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.get(f"/resource-server/v1.0/teams/{public_team.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == str(public_team.id)
