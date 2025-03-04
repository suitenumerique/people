"""
Tests for Teams API endpoint in People's core app: create
"""

import pytest
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
)
from rest_framework.test import APIClient

from core.factories import (
    ServiceProviderFactory,
    TeamAccessFactory,
    TeamFactory,
    UserFactory,
)
from core.models import Invitation

pytestmark = pytest.mark.django_db


def test_api_teams_invitations_create_anonymous():
    """Anonymous users should not be allowed to create team invitation."""
    response = APIClient().post(
        "/resource-server/v1.0/teams/ca143ed4-f83d-11ef-a8c5-af2e53ad69fb/invitations/",
        {
            "email": "toto@example.com",
            "role": "member",
        },
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert not Invitation.objects.exists()


def test_api_teams_invitations_create_authenticated_outsider(
    client, force_login_via_resource_server
):
    """Users outside of team should not be permitted to invite to team."""
    user = UserFactory()
    team = TeamFactory()
    service_provider = ServiceProviderFactory()
    team.service_providers.add(service_provider)

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.post(
            f"/resource-server/v1.0/teams/{team.id}/invitations/",
            {
                "email": "new@example.com",
                "role": "member",
            },
            format="json",
        )

    assert response.status_code == HTTP_403_FORBIDDEN
    assert not Invitation.objects.exists()


def test_api_teams_invitations_create_authenticated_member(
    client, force_login_via_resource_server
):
    """Team members should not be permitted to create invitations."""
    user = UserFactory()
    team = TeamFactory()
    service_provider = ServiceProviderFactory()
    team.service_providers.add(service_provider)
    TeamAccessFactory(team=team, user=user, role="member")

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.post(
            f"/resource-server/v1.0/teams/{team.id}/invitations/",
            {
                "email": "new@example.com",
                "role": "member",
            },
            format="json",
        )

    assert response.status_code == HTTP_403_FORBIDDEN
    assert not Invitation.objects.exists()


@pytest.mark.parametrize("role", ["owner", "administrator"])
def test_api_teams_invitations_create_authenticated_privileged(
    client, force_login_via_resource_server, role
):
    """Owners and administrators should be able to create invitations."""
    user = UserFactory()
    team = TeamFactory()
    service_provider = ServiceProviderFactory()
    team.service_providers.add(service_provider)
    TeamAccessFactory(team=team, user=user, role=role)

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.post(
            f"/resource-server/v1.0/teams/{team.id}/invitations/",
            {
                "email": "new@example.com",
                "role": "member",
            },
            format="json",
        )

    assert response.status_code == HTTP_201_CREATED
    invitation = Invitation.objects.get()
    assert response.json() == {
        "id": str(invitation.id),
        "created_at": invitation.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "email": "new@example.com",
        "team": str(team.id),
        "role": "member",
        "issuer": str(user.id),
        "is_expired": False,
    }


def test_api_teams_invitations_create_duplicate_email(
    client, force_login_via_resource_server
):
    """Should not be able to invite the same email twice."""
    user = UserFactory()
    team = TeamFactory()
    service_provider = ServiceProviderFactory()
    team.service_providers.add(service_provider)
    TeamAccessFactory(team=team, user=user, role="administrator")

    # Create first invitation
    with force_login_via_resource_server(client, user, service_provider.audience_id):
        client.post(
            f"/resource-server/v1.0/teams/{team.id}/invitations/",
            {
                "email": "new@example.com",
                "role": "member",
            },
            format="json",
        )

        # Try to create duplicate invitation
        response = client.post(
            f"/resource-server/v1.0/teams/{team.id}/invitations/",
            {
                "email": "new@example.com",
                "role": "member",
            },
            format="json",
        )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert Invitation.objects.count() == 1


def test_api_teams_invitations_create_wrong_service_provider(
    client, force_login_via_resource_server
):
    """Should not create invitation when accessing with wrong service provider."""
    user = UserFactory()
    team = TeamFactory()
    service_provider = ServiceProviderFactory()
    wrong_service_provider = ServiceProviderFactory()
    team.service_providers.add(service_provider)
    TeamAccessFactory(team=team, user=user, role="administrator")

    with force_login_via_resource_server(
        client, user, wrong_service_provider.audience_id
    ):
        response = client.post(
            f"/resource-server/v1.0/teams/{team.id}/invitations/",
            {
                "email": "new@example.com",
                "role": "member",
            },
            format="json",
        )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == {"team": ["Team not found."]}
    assert not Invitation.objects.exists()
