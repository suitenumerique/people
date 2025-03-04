"""
Tests for Teams Invitations API endpoint in People's core app: list
"""

import pytest
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
)
from rest_framework.test import APIClient

from core.factories import (
    InvitationFactory,
    ServiceProviderFactory,
    TeamAccessFactory,
    TeamFactory,
    UserFactory,
)

pytestmark = pytest.mark.django_db


def test_api_teams_invitations_list_anonymous():
    """Anonymous users should not be allowed to list team invitations."""
    team = TeamFactory()
    InvitationFactory.create_batch(size=3, team=team)

    response = APIClient().get(
        f"/resource-server/v1.0/teams/{team.id}/invitations/",
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED


def test_api_teams_invitations_list_authenticated_outsider(
    client, force_login_via_resource_server
):
    """Users outside of team should not be permitted to list team invitations."""
    user = UserFactory()
    team = TeamFactory()
    service_provider = ServiceProviderFactory()
    team.service_providers.add(service_provider)
    InvitationFactory.create_batch(size=3, team=team)

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.get(
            f"/resource-server/v1.0/teams/{team.id}/invitations/",
        )

    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "count": 0,
        "next": None,
        "previous": None,
        "results": [],
    }


@pytest.mark.parametrize("role", ["member", "administrator", "owner"])
def test_api_teams_invitations_list_authenticated_team_member(
    client, force_login_via_resource_server, role
):
    """Team members should be able to list invitations."""
    user = UserFactory()
    team = TeamFactory()
    service_provider = ServiceProviderFactory()
    team.service_providers.add(service_provider)
    TeamAccessFactory(team=team, user=user, role=role)

    invitations = InvitationFactory.create_batch(size=3, team=team)

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.get(
            f"/resource-server/v1.0/teams/{team.id}/invitations/",
        )

    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert data["count"] == 3
    assert len(data["results"]) == 3

    # Check invitations are ordered by creation date (most recent first)
    assert [item["id"] for item in data["results"]] == [
        str(invitation.id) for invitation in reversed(invitations)
    ]


def test_api_teams_invitations_list_pagination(client, force_login_via_resource_server):
    """Should properly paginate results."""
    user = UserFactory()
    team = TeamFactory()
    service_provider = ServiceProviderFactory()
    team.service_providers.add(service_provider)
    TeamAccessFactory(team=team, user=user, role="member")

    InvitationFactory.create_batch(size=15, team=team)

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.get(
            f"/resource-server/v1.0/teams/{team.id}/invitations/",
            {"page_size": 10},
        )

    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert data["count"] == 15
    assert len(data["results"]) == 10
    assert data["next"] is not None
    assert data["previous"] is None


def test_api_teams_invitations_list_empty(client, force_login_via_resource_server):
    """Should return empty list when no invitations exist."""
    user = UserFactory()
    team = TeamFactory()
    service_provider = ServiceProviderFactory()
    team.service_providers.add(service_provider)
    TeamAccessFactory(team=team, user=user, role="member")

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.get(
            f"/resource-server/v1.0/teams/{team.id}/invitations/",
        )

    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert data["count"] == 0
    assert len(data["results"]) == 0


def test_api_teams_invitations_list_wrong_service_provider(
    client, force_login_via_resource_server
):
    """Should not list invitations when accessing with wrong service provider."""
    user = UserFactory()
    team = TeamFactory()
    service_provider = ServiceProviderFactory()
    wrong_service_provider = ServiceProviderFactory()
    team.service_providers.add(service_provider)
    TeamAccessFactory(team=team, user=user, role="member")

    InvitationFactory.create_batch(size=3, team=team)

    with force_login_via_resource_server(
        client, user, wrong_service_provider.audience_id
    ):
        response = client.get(
            f"/resource-server/v1.0/teams/{team.id}/invitations/",
        )

    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "count": 0,
        "next": None,
        "previous": None,
        "results": [],
    }
