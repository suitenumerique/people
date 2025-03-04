"""
Tests for Teams Invitations API endpoint in People's core app: retrieve
"""

import pytest
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
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


def test_api_teams_invitations_retrieve_anonymous():
    """Anonymous users should not be allowed to retrieve team invitations."""
    invitation = InvitationFactory()
    team = invitation.team

    response = APIClient().get(
        f"/resource-server/v1.0/teams/{team.id}/invitations/{invitation.id}/",
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED


def test_api_teams_invitations_retrieve_authenticated_outsider(
    client, force_login_via_resource_server
):
    """Users outside of team should not be permitted to retrieve team invitations."""
    user = UserFactory()
    invitation = InvitationFactory()
    team = invitation.team
    service_provider = ServiceProviderFactory()
    team.service_providers.add(service_provider)

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.get(
            f"/resource-server/v1.0/teams/{team.id}/invitations/{invitation.id}/",
        )

    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No Invitation matches the given query."}


@pytest.mark.parametrize("role", ["member", "administrator", "owner"])
def test_api_teams_invitations_retrieve_authenticated_team_member(
    client, force_login_via_resource_server, role
):
    """Team members should be able to retrieve invitations."""
    user = UserFactory()
    invitation = InvitationFactory()
    team = invitation.team
    service_provider = ServiceProviderFactory()
    team.service_providers.add(service_provider)
    TeamAccessFactory(team=team, user=user, role=role)

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.get(
            f"/resource-server/v1.0/teams/{team.id}/invitations/{invitation.id}/",
        )

    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "id": str(invitation.id),
        "created_at": invitation.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "email": invitation.email,
        "team": str(team.id),
        "role": invitation.role,
        "issuer": str(invitation.issuer.id),
        "is_expired": invitation.is_expired,
    }


def test_api_teams_invitations_retrieve_nonexistent(
    client, force_login_via_resource_server
):
    """Should return 404 when trying to retrieve non-existent invitation."""
    user = UserFactory()
    team = TeamFactory()
    service_provider = ServiceProviderFactory()
    team.service_providers.add(service_provider)
    TeamAccessFactory(team=team, user=user, role="member")

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.get(
            f"/resource-server/v1.0/teams/{team.id}/invitations/nonexistent-uuid/",
        )

    assert response.status_code == HTTP_404_NOT_FOUND


def test_api_teams_invitations_retrieve_wrong_team(
    client, force_login_via_resource_server
):
    """Should return 404 when trying to retrieve invitation from wrong team."""
    user = UserFactory()
    invitation = InvitationFactory()
    wrong_team = TeamFactory()
    service_provider = ServiceProviderFactory()
    wrong_team.service_providers.add(service_provider)
    TeamAccessFactory(team=wrong_team, user=user, role="member")

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.get(
            f"/resource-server/v1.0/teams/{wrong_team.id}/invitations/{invitation.id}/",
        )

    assert response.status_code == HTTP_404_NOT_FOUND


def test_api_teams_invitations_retrieve_wrong_service_provider(
    client, force_login_via_resource_server
):
    """Should not retrieve invitation when accessing with wrong service provider."""
    user = UserFactory()
    invitation = InvitationFactory()
    team = invitation.team
    service_provider = ServiceProviderFactory()
    wrong_service_provider = ServiceProviderFactory()
    team.service_providers.add(service_provider)
    TeamAccessFactory(team=team, user=user, role="member")

    with force_login_via_resource_server(
        client, user, wrong_service_provider.audience_id
    ):
        response = client.get(
            f"/resource-server/v1.0/teams/{team.id}/invitations/{invitation.id}/",
        )

    assert response.status_code == HTTP_404_NOT_FOUND
