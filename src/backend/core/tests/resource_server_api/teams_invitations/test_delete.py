"""
Tests for Teams Invitations API endpoint in People's core app: delete
"""

import pytest
from rest_framework.status import (
    HTTP_204_NO_CONTENT,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
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
from core.models import Invitation

pytestmark = pytest.mark.django_db


def test_api_teams_invitations_delete_anonymous():
    """Anonymous users should not be allowed to delete team invitations."""
    invitation = InvitationFactory()
    team = invitation.team

    response = APIClient().delete(
        f"/resource-server/v1.0/teams/{team.id}/invitations/{invitation.id}/",
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert Invitation.objects.filter(id=invitation.id).exists()


def test_api_teams_invitations_delete_authenticated_outsider(
    client, force_login_via_resource_server
):
    """Users outside of team should not be permitted to delete team invitations."""
    user = UserFactory()
    invitation = InvitationFactory()
    team = invitation.team
    service_provider = ServiceProviderFactory()
    team.service_providers.add(service_provider)

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.delete(
            f"/resource-server/v1.0/teams/{team.id}/invitations/{invitation.id}/",
        )

    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No Invitation matches the given query."}
    assert Invitation.objects.filter(id=invitation.id).exists()


def test_api_teams_invitations_delete_authenticated_member(
    client, force_login_via_resource_server
):
    """Team members should not be permitted to delete invitations."""
    user = UserFactory()
    invitation = InvitationFactory()
    team = invitation.team
    service_provider = ServiceProviderFactory()
    team.service_providers.add(service_provider)
    TeamAccessFactory(team=team, user=user, role="member")

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.delete(
            f"/resource-server/v1.0/teams/{team.id}/invitations/{invitation.id}/",
        )

    assert response.status_code == HTTP_403_FORBIDDEN
    assert Invitation.objects.filter(id=invitation.id).exists()


@pytest.mark.parametrize("role", ["owner", "administrator"])
def test_api_teams_invitations_delete_authenticated_privileged(
    client, force_login_via_resource_server, role
):
    """Owners and administrators should be able to delete invitations."""
    user = UserFactory()
    invitation = InvitationFactory()
    team = invitation.team
    service_provider = ServiceProviderFactory()
    team.service_providers.add(service_provider)
    TeamAccessFactory(team=team, user=user, role=role)

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.delete(
            f"/resource-server/v1.0/teams/{team.id}/invitations/{invitation.id}/",
        )

    assert response.status_code == HTTP_204_NO_CONTENT
    assert not Invitation.objects.filter(id=invitation.id).exists()


def test_api_teams_invitations_delete_nonexistent(
    client, force_login_via_resource_server
):
    """Should return 404 when trying to delete non-existent invitation."""
    user = UserFactory()
    team = TeamFactory()
    service_provider = ServiceProviderFactory()
    team.service_providers.add(service_provider)
    TeamAccessFactory(team=team, user=user, role="administrator")

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.delete(
            f"/resource-server/v1.0/teams/{team.id}/invitations/nonexistent-uuid/",
        )

    assert response.status_code == HTTP_404_NOT_FOUND


def test_api_teams_invitations_delete_wrong_service_provider(
    client, force_login_via_resource_server
):
    """Should not delete invitation when accessing with wrong service provider."""
    user = UserFactory()
    invitation = InvitationFactory()
    team = invitation.team
    service_provider = ServiceProviderFactory()
    wrong_service_provider = ServiceProviderFactory()
    team.service_providers.add(service_provider)
    TeamAccessFactory(team=team, user=user, role="administrator")

    with force_login_via_resource_server(
        client, user, wrong_service_provider.audience_id
    ):
        response = client.delete(
            f"/resource-server/v1.0/teams/{team.id}/invitations/{invitation.id}/",
        )

    assert response.status_code == HTTP_404_NOT_FOUND
    assert Invitation.objects.filter(id=invitation.id).exists()
