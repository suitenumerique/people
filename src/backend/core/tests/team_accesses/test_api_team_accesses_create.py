"""
Test for team accesses API endpoints in People's core app : create
"""

import json
import logging
import random
import re

import pytest
import responses
from rest_framework import status
from rest_framework.test import APIClient

from core import enums, factories, models
from core.tests.fixtures import matrix

pytestmark = pytest.mark.django_db


def test_api_team_accesses_create_anonymous():
    """Anonymous users should not be allowed to create team accesses."""
    user = factories.UserFactory()
    team = factories.TeamFactory()

    response = APIClient().post(
        f"/api/v1.0/teams/{team.id!s}/accesses/",
        {
            "user": str(user.id),
            "team": str(team.id),
            "role": random.choice(models.RoleChoices.choices)[0],
        },
        format="json",
    )
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }
    assert models.TeamAccess.objects.exists() is False


def test_api_team_accesses_create_authenticated_unrelated():
    """
    Authenticated users should not be allowed to create team accesses for a team to
    which they are not related.
    """
    user = factories.UserFactory()
    other_user = factories.UserFactory()
    team = factories.TeamFactory()

    client = APIClient()
    client.force_login(user)
    response = client.post(
        f"/api/v1.0/teams/{team.id!s}/accesses/",
        {
            "user": str(other_user.id),
        },
        format="json",
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "You are not allowed to manage accesses for this team."
    }
    assert not models.TeamAccess.objects.filter(user=other_user).exists()


def test_api_team_accesses_create_authenticated_member():
    """Members of a team should not be allowed to create team accesses."""
    user = factories.UserFactory()
    team = factories.TeamFactory(users=[(user, "member")])
    other_user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)
    for role in [role[0] for role in models.RoleChoices.choices]:
        response = client.post(
            f"/api/v1.0/teams/{team.id!s}/accesses/",
            {
                "user": str(other_user.id),
                "role": role,
            },
            format="json",
        )

        assert response.status_code == 403
        assert response.json() == {
            "detail": "You are not allowed to manage accesses for this team."
        }

    assert not models.TeamAccess.objects.filter(user=other_user).exists()


def test_api_team_accesses_create_authenticated_administrator():
    """
    Administrators of a team should be able to create team accesses except for the "owner" role.
    """
    user = factories.UserFactory()
    team = factories.TeamFactory(users=[(user, "administrator")])
    other_user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    # It should not be allowed to create an owner access
    response = client.post(
        f"/api/v1.0/teams/{team.id!s}/accesses/",
        {
            "user": str(other_user.id),
            "role": "owner",
        },
        format="json",
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Only owners of a team can assign other users as owners."
    }

    # It should be allowed to create a lower access
    role = random.choice(
        [role[0] for role in models.RoleChoices.choices if role[0] != "owner"]
    )

    response = client.post(
        f"/api/v1.0/teams/{team.id!s}/accesses/",
        {
            "user": str(other_user.id),
            "role": role,
        },
        format="json",
    )

    assert response.status_code == 201
    assert models.TeamAccess.objects.filter(user=other_user).count() == 1
    new_team_access = models.TeamAccess.objects.filter(user=other_user).get()
    assert response.json() == {
        "abilities": new_team_access.get_abilities(user),
        "id": str(new_team_access.id),
        "role": role,
        "user": str(other_user.id),
    }


def test_api_team_accesses_create_authenticated_owner():
    """
    Owners of a team should be able to create team accesses whatever the role.
    """
    user = factories.UserFactory()
    team = factories.TeamFactory(users=[(user, "owner")])
    other_user = factories.UserFactory()

    role = random.choice([role[0] for role in models.RoleChoices.choices])

    client = APIClient()
    client.force_login(user)
    response = client.post(
        f"/api/v1.0/teams/{team.id!s}/accesses/",
        {
            "user": str(other_user.id),
            "role": role,
        },
        format="json",
    )

    assert response.status_code == 201
    assert models.TeamAccess.objects.filter(user=other_user).count() == 1
    new_team_access = models.TeamAccess.objects.filter(user=other_user).get()
    assert response.json() == {
        "abilities": new_team_access.get_abilities(user),
        "id": str(new_team_access.id),
        "role": role,
        "user": str(other_user.id),
    }


def test_api_team_accesses_create__with_scim_webhook():
    """
    If a team has a SCIM webhook, creating a team access should fire a call
    with the expected payload.
    """
    user, other_user = factories.UserFactory.create_batch(2)

    team = factories.TeamFactory(users=[(user, "owner")])
    webhook = factories.TeamWebhookFactory(
        team=team, protocol=enums.WebhookProtocolChoices.SCIM
    )

    role = random.choice([role[0] for role in models.RoleChoices.choices])

    client = APIClient()
    client.force_login(user)

    with responses.RequestsMock() as rsps:
        # Ensure successful response by scim provider using "responses":
        rsp = rsps.add(
            rsps.PATCH,
            re.compile(r".*/Groups/.*"),
            body="{}",
            status=200,
            content_type="application/json",
        )

        response = client.post(
            f"/api/v1.0/teams/{team.id!s}/accesses/",
            {
                "user": str(other_user.id),
                "role": role,
            },
            format="json",
        )
        assert response.status_code == 201

        assert rsp.call_count == 1
        assert rsps.calls[0].request.url == webhook.url

        # Payload sent to scim provider
        payload = json.loads(rsps.calls[0].request.body)
        assert payload == {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
            "Operations": [
                {
                    "op": "add",
                    "path": "members",
                    "value": [
                        {
                            "value": str(other_user.id),
                            "email": other_user.email,
                            "type": "User",
                        }
                    ],
                }
            ],
        }

    assert models.TeamAccess.objects.filter(user=other_user, team=team).exists()


@responses.activate
def test_api_team_accesses_create__with_matrix_webhook():
    """
    If a team has a Matrix webhook, creating a team access should fire a call
    with the expected payload.
    """
    user, other_user = factories.UserFactory.create_batch(2)

    team = factories.TeamFactory(users=[(user, "owner")])
    webhook = factories.TeamWebhookFactory(
        team=team,
        url="https://server.fr/#/room/room_id:home_server.fr",
        secret="some-secret-you-should-not-store-on-a-postit",
        protocol=enums.WebhookProtocolChoices.MATRIX,
    )

    role = random.choice([role[0] for role in models.RoleChoices.choices])

    client = APIClient()
    client.force_login(user)

    # Mock successful responses by matrix server
    responses.post(
        re.compile(r".*/join"),
        body=str(matrix.mock_join_room_successful("room_id")["message"]),
        status=matrix.mock_join_room_successful("room_id")["status_code"],
        content_type="application/json",
    )
    responses.post(
        re.compile(r".*/invite"),
        body=str(matrix.mock_invite_successful()["message"]),
        status=matrix.mock_invite_successful()["status_code"],
        content_type="application/json",
    )

    response = client.post(
        f"/api/v1.0/teams/{team.id!s}/accesses/",
        {
            "user": str(other_user.id),
            "role": role,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED

    assert len(responses.calls) == 2
    assert (
        responses.calls[0].request.url
        == "https://home_server.fr/_matrix/client/v3/rooms/room_id:home_server.fr/join"
    )

    # Payload sent to matrix server
    assert webhook.secret in responses.calls[0].request.headers["Authorization"]
    assert json.loads(responses.calls[1].request.body) == {
        "user_id": f"@{other_user.email.replace('@', ':')}",
        "reason": f"User added to team {webhook.team} on People",
    }

    assert models.TeamAccess.objects.filter(user=other_user, team=team).exists()


def test_api_team_accesses_create__multiple_webhooks_success(caplog):
    """
    When the team has multiple webhooks, creating a team access should fire all the expected calls.
    If all responses are positive, proceeds to add the user to the team.
    """
    caplog.set_level(logging.INFO)

    user, other_user = factories.UserFactory.create_batch(2)

    team = factories.TeamFactory(users=[(user, "owner")])
    webhook_scim = factories.TeamWebhookFactory(
        team=team, protocol=enums.WebhookProtocolChoices.SCIM, secret="wesh"
    )
    webhook_matrix = factories.TeamWebhookFactory(
        team=team,
        url="https://www.webhookserver.fr/#/room/room_id:home_server/",
        protocol=enums.WebhookProtocolChoices.MATRIX,
        secret="yo",
    )

    role = random.choice([role[0] for role in models.RoleChoices.choices])

    client = APIClient()
    client.force_login(user)

    with responses.RequestsMock() as rsps:
        # Ensure successful response by scim provider using "responses":
        rsps.add(
            rsps.PATCH,
            re.compile(r".*/Groups/.*"),
            body="{}",
            status=200,
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(r".*/join"),
            body=str(matrix.mock_join_room_successful),
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(r".*/invite"),
            body=str(matrix.mock_invite_successful()["message"]),
            status=matrix.mock_invite_successful()["status_code"],
            content_type="application/json",
        )

        response = client.post(
            f"/api/v1.0/teams/{team.id!s}/accesses/",
            {
                "user": str(other_user.id),
                "role": role,
            },
            format="json",
        )
        assert response.status_code == 201

    # Logger
    log_messages = [msg.message for msg in caplog.records]
    for webhook in [webhook_scim, webhook_matrix]:
        assert (
            f"add_user_to_group synchronization succeeded with {webhook.url}"
            in log_messages
        )

    # Status
    for webhook in [webhook_scim, webhook_matrix]:
        webhook.refresh_from_db()
        assert webhook.status == "success"
    assert models.TeamAccess.objects.filter(user=other_user, team=team).exists()


@responses.activate
def test_api_team_accesses_create__multiple_webhooks_failure(caplog):
    """When a webhook fails, user should still be added to the team."""
    caplog.set_level(logging.INFO)

    user, other_user = factories.UserFactory.create_batch(2)

    team = factories.TeamFactory(users=[(user, "owner")])
    webhook_scim = factories.TeamWebhookFactory(
        team=team, protocol=enums.WebhookProtocolChoices.SCIM, secret="wesh"
    )
    webhook_matrix = factories.TeamWebhookFactory(
        team=team,
        url="https://www.webhookserver.fr/#/room/room_id:home_server/",
        protocol=enums.WebhookProtocolChoices.MATRIX,
        secret="secret",
    )

    role = random.choice([role[0] for role in models.RoleChoices.choices])
    client = APIClient()
    client.force_login(user)

    responses.patch(
        re.compile(r".*/Groups/.*"),
        body="{}",
        status=200,
    )
    responses.post(
        re.compile(r".*/join"),
        body=str(matrix.mock_join_room_forbidden()["message"]),
        status=str(matrix.mock_join_room_forbidden()["status_code"]),
    )

    response = client.post(
        f"/api/v1.0/teams/{team.id!s}/accesses/",
        {
            "user": str(other_user.id),
            "role": role,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED

    # Logger
    log_messages = [msg.message for msg in caplog.records]
    assert (
        f"add_user_to_group synchronization succeeded with {webhook_scim.url}"
        in log_messages
    )
    assert (
        f"add_user_to_group synchronization failed with {webhook_matrix.url}"
        in log_messages
    )

    # Status
    webhook_scim.status = "success"
    webhook_matrix.status = "failure"
    assert models.TeamAccess.objects.filter(user=other_user, team=team).exists()
