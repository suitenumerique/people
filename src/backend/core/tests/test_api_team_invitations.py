"""
Unit tests for the Invitation model
"""

import time

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories
from core.api.client import serializers

pytestmark = pytest.mark.django_db


def test_api_team_invitations__create__anonymous():
    """Anonymous users should not be able to create invitations."""
    team = factories.TeamFactory()
    invitation_values = serializers.InvitationSerializer(
        factories.InvitationFactory.build()
    ).data

    response = APIClient().post(
        f"/api/v1.0/teams/{team.id}/invitations/",
        invitation_values,
        format="json",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_team_invitations__create__authenticated_outsider():
    """Users outside of team should not be permitted to invite to team."""
    user = factories.UserFactory()
    team = factories.TeamFactory()
    invitation_values = serializers.InvitationSerializer(
        factories.InvitationFactory.build()
    ).data

    client = APIClient()
    client.force_login(user)

    response = client.post(
        f"/api/v1.0/teams/{team.id}/invitations/",
        invitation_values,
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "role",
    ["owner", "administrator"],
)
def test_api_team_invitations__create__privileged_members(role):
    """Owners and administrators should be able to invite new members."""
    user = factories.UserFactory()
    team = factories.TeamFactory(users=[(user, role)])

    invitation_values = serializers.InvitationSerializer(
        factories.InvitationFactory.build()
    ).data

    client = APIClient()
    client.force_login(user)

    response = client.post(
        f"/api/v1.0/teams/{team.id}/invitations/",
        invitation_values,
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED


def test_api_team_invitations__create__members():
    """
    Members should not be able to invite new members.
    """
    user = factories.UserFactory()
    team = factories.TeamFactory(users=[(user, "member")])

    invitation_values = serializers.InvitationSerializer(
        factories.InvitationFactory.build()
    ).data

    client = APIClient()
    client.force_login(user)

    response = client.post(
        f"/api/v1.0/teams/{team.id}/invitations/",
        invitation_values,
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "You are not allowed to manage invitation for this team."
    }


def test_api_team_invitations__create__issuer_and_team_automatically_added():
    """Team and issuer fields should auto-complete."""
    user = factories.UserFactory()
    team = factories.TeamFactory(users=[(user, "owner")])

    # Generate a random invitation
    invitation = factories.InvitationFactory.build()
    invitation_data = {"email": invitation.email, "role": invitation.role}

    client = APIClient()
    client.force_login(user)

    response = client.post(
        f"/api/v1.0/teams/{team.id}/invitations/",
        invitation_data,
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    # team and issuer automatically set
    assert response.json()["team"] == str(team.id)
    assert response.json()["issuer"] == str(user.id)


def test_api_team_invitations__create__cannot_duplicate_invitation():
    """An email should not be invited multiple times to the same team."""
    existing_invitation = factories.InvitationFactory()
    team = existing_invitation.team

    # Grant privileged role on the Team to the user
    user = factories.UserFactory()
    factories.TeamAccessFactory(team=team, user=user, role="administrator")

    # Create a new invitation to the same team with the exact same email address
    duplicated_invitation = serializers.InvitationSerializer(
        factories.InvitationFactory.build(email=existing_invitation.email)
    ).data

    client = APIClient()
    client.force_login(user)
    response = client.post(
        f"/api/v1.0/teams/{team.id}/invitations/",
        duplicated_invitation,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["__all__"] == [
        "Team invitation with this Email address and Team already exists."
    ]


def test_api_team_invitations__create__cannot_invite_existing_users():
    """
    Should not be able to invite already existing users.
    """
    user, existing_user = factories.UserFactory.create_batch(2)
    team = factories.TeamFactory(users=[(user, "administrator")])

    # Build an invitation to the email of an exising identity in the db
    invitation_values = serializers.InvitationSerializer(
        factories.InvitationFactory.build(email=existing_user.email, team=team)
    ).data

    client = APIClient()
    client.force_login(user)

    response = client.post(
        f"/api/v1.0/teams/{team.id}/invitations/",
        invitation_values,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert (
        response.json()["detail"]
        == "Email already known. Invitation not sent but access created instead."
    )


def test_api_team_invitations__list__anonymous_user():
    """Anonymous users should not be able to list invitations."""
    team = factories.TeamFactory()
    response = APIClient().get(f"/api/v1.0/teams/{team.id}/invitations/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_api_team_invitations__list__authenticated():
    """
    Authenticated user should be able to list invitations
    in teams they belong to, including from other issuers.
    """
    user, other_user = factories.UserFactory.create_batch(2)
    team = factories.TeamFactory(users=[(user, "administrator"), (other_user, "owner")])
    invitation = factories.InvitationFactory(
        team=team, role="administrator", issuer=user
    )
    other_invitations = factories.InvitationFactory.create_batch(
        2, team=team, role="member", issuer=other_user
    )

    # invitations from other teams should not be listed
    other_team = factories.TeamFactory()
    factories.InvitationFactory.create_batch(2, team=other_team, role="member")

    client = APIClient()
    client.force_login(user)
    response = client.get(
        f"/api/v1.0/teams/{team.id}/invitations/",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 3
    assert sorted(response.json()["results"], key=lambda x: x["created_at"]) == sorted(
        [
            {
                "id": str(i.id),
                "created_at": i.created_at.isoformat().replace("+00:00", "Z"),
                "email": str(i.email),
                "team": str(team.id),
                "role": i.role,
                "issuer": str(i.issuer.id),
                "is_expired": False,
            }
            for i in [invitation, *other_invitations]
        ],
        key=lambda x: x["created_at"],
    )


def test_api_team_invitations__list__expired_invitations_still_listed(settings):
    """
    Expired invitations are still listed.
    """
    user = factories.UserFactory()
    other_user = factories.UserFactory()

    team = factories.TeamFactory(users=[(user, "administrator"), (other_user, "owner")])

    # override settings to accelerate validation expiration
    settings.INVITATION_VALIDITY_DURATION = 1  # second
    expired_invitation = factories.InvitationFactory(
        team=team,
        role="member",
        issuer=user,
    )
    time.sleep(1)

    client = APIClient()
    client.force_login(user)
    response = client.get(
        f"/api/v1.0/teams/{team.id}/invitations/",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 1
    assert sorted(response.json()["results"], key=lambda x: x["created_at"]) == sorted(
        [
            {
                "id": str(expired_invitation.id),
                "created_at": expired_invitation.created_at.isoformat().replace(
                    "+00:00", "Z"
                ),
                "email": str(expired_invitation.email),
                "team": str(team.id),
                "role": expired_invitation.role,
                "issuer": str(expired_invitation.issuer.id),
                "is_expired": True,
            },
        ],
        key=lambda x: x["created_at"],
    )


def test_api_team_invitations__retrieve__anonymous_user():
    """
    Anonymous user should not be able to retrieve invitations.
    """

    invitation = factories.InvitationFactory()
    response = APIClient().get(
        f"/api/v1.0/teams/{invitation.team.id}/invitations/{invitation.id}/",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_api_team_invitations__retrieve__unrelated_user():
    """
    Authenticated unrelated users should not be able to retrieve invitations.
    """
    user = factories.UserFactory()
    invitation = factories.InvitationFactory()

    client = APIClient()
    client.force_login(user)

    response = client.get(
        f"/api/v1.0/teams/{invitation.team.id}/invitations/{invitation.id}/",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_api_team_invitations__retrieve__team_member():
    """
    Authenticated team members should be able to retrieve invitations
    whatever their role in the team.
    """
    user = factories.UserFactory()
    invitation = factories.InvitationFactory()
    factories.TeamAccessFactory(team=invitation.team, user=user, role="member")

    client = APIClient()
    client.force_login(user)
    response = client.get(
        f"/api/v1.0/teams/{invitation.team.id}/invitations/{invitation.id}/",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(invitation.id),
        "created_at": invitation.created_at.isoformat().replace("+00:00", "Z"),
        "email": invitation.email,
        "team": str(invitation.team.id),
        "role": str(invitation.role),
        "issuer": str(invitation.issuer.id),
        "is_expired": False,
    }


@pytest.mark.parametrize(
    "method",
    ["put", "patch"],
)
def test_api_team_invitations__update__forbidden(method):
    """
    Update of invitations is currently forbidden.
    """
    user = factories.UserFactory()
    invitation = factories.InvitationFactory()
    factories.TeamAccessFactory(team=invitation.team, user=user, role="owner")

    client = APIClient()
    client.force_login(user)

    response = None
    if method == "put":
        response = client.put(
            f"/api/v1.0/teams/{invitation.team.id}/invitations/{invitation.id}/",
        )
    if method == "patch":
        response = client.patch(
            f"/api/v1.0/teams/{invitation.team.id}/invitations/{invitation.id}/",
        )
    assert response is not None
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert response.json()["detail"] == f'Method "{method.upper()}" not allowed.'


def test_api_team_invitations__delete__anonymous():
    """Anonymous user should not be able to delete invitations."""
    invitation = factories.InvitationFactory()

    response = APIClient().delete(
        f"/api/v1.0/teams/{invitation.team.id}/invitations/{invitation.id}/",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_api_team_invitations__delete__authenticated_outsider():
    """Members outside of team should not cancel invitations."""
    user = factories.UserFactory()
    team = factories.TeamFactory()
    invitation = factories.InvitationFactory(team=team)

    client = APIClient()
    client.force_login(user)
    response = client.delete(
        f"/api/v1.0/teams/{team.id}/invitations/{invitation.id}/",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize("role", ["owner", "administrator"])
def test_api_team_invitations__delete__privileged_members(role):
    """Privileged member should be able to cancel invitation."""
    user = factories.UserFactory()
    team = factories.TeamFactory(users=[(user, role)])
    invitation = factories.InvitationFactory(team=team)

    client = APIClient()
    client.force_login(user)
    response = client.delete(
        f"/api/v1.0/teams/{team.id}/invitations/{invitation.id}/",
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_api_team_invitations__delete__members():
    """Member should not be able to cancel invitation."""
    user = factories.UserFactory()
    team = factories.TeamFactory(users=[(user, "member")])
    invitation = factories.InvitationFactory(team=team)

    client = APIClient()
    client.force_login(user)
    response = client.delete(
        f"/api/v1.0/teams/{team.id}/invitations/{invitation.id}/",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert (
        response.json()["detail"]
        == "You do not have permission to perform this action."
    )
