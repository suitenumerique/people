"""
Tests for Teams API endpoint in People's core app: update
"""

import pytest
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)
from rest_framework.test import APIClient

from core import factories
from core.resource_server_api import serializers

pytestmark = pytest.mark.django_db


def test_api_teams_update_anonymous():
    """Anonymous users should not be allowed to update a team."""
    team = factories.TeamFactory()
    old_team_values = serializers.TeamSerializer(instance=team).data

    new_team_values = serializers.TeamSerializer(instance=factories.TeamFactory()).data
    response = APIClient().put(
        f"/resource-server/v1.0/teams/{team.id!s}/",
        new_team_values,
        content_type="application/json",
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }

    team.refresh_from_db()
    team_values = serializers.TeamSerializer(instance=team).data
    assert team_values == old_team_values


def test_api_teams_update_authenticated_unrelated(
    client, force_login_via_resource_server
):
    """
    Authenticated users should not be allowed to update a team to which they are not related.
    """
    user = factories.UserFactory()
    service_provider = factories.ServiceProviderFactory()
    team = factories.TeamFactory(service_providers=[service_provider])

    old_team_values = serializers.TeamSerializer(instance=team).data

    new_team_values = serializers.TeamSerializer(instance=factories.TeamFactory()).data

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.put(
            f"/resource-server/v1.0/teams/{team.id!s}/",
            new_team_values,
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer b64untestedbearertoken",
        )

    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No Team matches the given query."}

    team.refresh_from_db()
    team_values = serializers.TeamSerializer(instance=team).data
    assert team_values == old_team_values


def test_api_teams_update_authenticated(
    client,
    force_login_via_resource_server,
):
    """
    Authenticated users should be allowed to update a team to which they
    are related whatever the role even if the request is authenticated via
    a resource server.
    """
    service_provider = factories.ServiceProviderFactory(
        audience_id="some_service_provider"
    )
    user = factories.UserFactory()
    team = factories.TeamFactory(
        name="Old name",
        users=[(user, "owner")],
        service_providers=[service_provider],
    )

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.put(
            f"/resource-server/v1.0/teams/{team.id!s}/",
            data=serializers.TeamSerializer(instance=team).data
            | {
                "name": "New name",
            },
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer b64untestedbearertoken",
        )

    assert response.status_code == HTTP_200_OK

    team.refresh_from_db()
    assert team.name == "New name"


def test_api_teams_update_authenticated_other_resource_server(
    client, force_login_via_resource_server
):
    """
    Authenticated users should not be able to update a team for which they are directly
    owner, if the request is authenticated via a different service provider.
    """
    user = factories.UserFactory()
    service_provider = factories.ServiceProviderFactory()

    other_service_provider = factories.ServiceProviderFactory(
        audience_id="some_service_provider"
    )
    team = factories.TeamFactory(
        name="Old name",
        users=[(user, "owner")],
        service_providers=[other_service_provider],
    )

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.put(
            f"/resource-server/v1.0/teams/{team.id!s}/",
            data=serializers.TeamSerializer(instance=team).data
            | {
                "name": "New name",
            },
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer b64untestedbearertoken",
        )

    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No Team matches the given query."}

    team.refresh_from_db()
    assert team.name == "Old name"


def test_api_teams_update_authenticated_members(
    client, force_login_via_resource_server
):
    """
    Users who are members of a team but not administrators should
    not be allowed to update it.
    """
    user = factories.UserFactory()
    service_provider = factories.ServiceProviderFactory()

    team = factories.TeamFactory(
        users=[(user, "member")], service_providers=[service_provider]
    )
    old_team_values = serializers.TeamSerializer(instance=team).data

    new_team_values = serializers.TeamSerializer(instance=factories.TeamFactory()).data

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.put(
            f"/resource-server/v1.0/teams/{team.id!s}/",
            new_team_values,
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer b64untestedbearertoken",
        )

    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "You do not have permission to perform this action."
    }

    team.refresh_from_db()
    team_values = serializers.TeamSerializer(instance=team).data
    assert team_values == old_team_values


@pytest.mark.parametrize("role", ["owner", "administrator"])
def test_api_teams_update_authenticated_administrators(
    client, force_login_via_resource_server, role
):
    """Administrators or owners of a team should be allowed to update it."""
    user = factories.UserFactory()
    service_provider = factories.ServiceProviderFactory()

    team = factories.TeamFactory(
        users=[(user, role)],
        service_providers=[service_provider],
        name="old name",
    )
    initial_created_at = team.created_at
    initial_updated_at = team.updated_at
    initial_pk = team.pk

    # generate new random values
    new_values = serializers.TeamSerializer(instance=factories.TeamFactory.build()).data

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.put(
            f"/resource-server/v1.0/teams/{team.id!s}/",
            new_values,
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer b64untestedbearertoken",
        )
    assert response.status_code == HTTP_200_OK

    team.refresh_from_db()
    assert team.pk == initial_pk
    assert team.name == new_values["name"]
    assert team.created_at == initial_created_at
    assert team.updated_at > initial_updated_at


@pytest.mark.parametrize("role", ["owner", "administrator"])
def test_api_teams_update_administrator_or_owner_of_another(
    client, force_login_via_resource_server, role
):
    """
    Being administrator or owner of a team should not grant authorization to update
    another team.
    """
    user = factories.UserFactory()
    service_provider = factories.ServiceProviderFactory()

    factories.TeamFactory(users=[(user, role)], service_providers=[service_provider])

    team = factories.TeamFactory(name="Old name", service_providers=[service_provider])
    old_team_values = serializers.TeamSerializer(instance=team).data

    new_team_values = serializers.TeamSerializer(instance=factories.TeamFactory()).data

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.put(
            f"/resource-server/v1.0/teams/{team.id!s}/",
            new_team_values,
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer b64untestedbearertoken",
        )

    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No Team matches the given query."}

    team.refresh_from_db()
    team_values = serializers.TeamSerializer(instance=team).data
    assert team_values == old_team_values
