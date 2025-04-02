"""
Test for team accesses API endpoints in People's core app : delete
"""

import json
import random

import pytest
import responses
from rest_framework.test import APIClient

from core import factories, models

pytestmark = pytest.mark.django_db


def test_api_team_accesses_delete_anonymous():
    """Anonymous users should not be allowed to destroy a team access."""
    access = factories.TeamAccessFactory()

    response = APIClient().delete(
        f"/api/v1.0/teams/{access.team.id!s}/accesses/{access.id!s}/",
    )

    assert response.status_code == 401
    assert models.TeamAccess.objects.count() == 1


def test_api_team_accesses_delete_authenticated():
    """
    Authenticated users should not be allowed to delete a team access for a
    team to which they are not related.
    """
    user = factories.UserFactory()
    access = factories.TeamAccessFactory()

    client = APIClient()
    client.force_login(user)
    response = client.delete(
        f"/api/v1.0/teams/{access.team.id!s}/accesses/{access.id!s}/",
    )

    assert response.status_code == 403
    assert models.TeamAccess.objects.count() == 1


def test_api_team_accesses_delete_member():
    """
    Authenticated users should not be allowed to delete a team access for a
    team in which they are a simple member.
    """
    user = factories.UserFactory()
    team = factories.TeamFactory(users=[(user, "member")])
    access = factories.TeamAccessFactory(team=team)

    assert models.TeamAccess.objects.count() == 2
    assert models.TeamAccess.objects.filter(user=access.user).exists()

    client = APIClient()
    client.force_login(user)
    response = client.delete(
        f"/api/v1.0/teams/{team.id!s}/accesses/{access.id!s}/",
    )

    assert response.status_code == 403
    assert models.TeamAccess.objects.count() == 2


def test_api_team_accesses_delete_administrators():
    """
    Users who are administrators in a team should be allowed to delete an access
    from the team provided it is not ownership.
    """
    user = factories.UserFactory()
    team = factories.TeamFactory(users=[(user, "administrator")])
    access = factories.TeamAccessFactory(
        team=team, role=random.choice(["member", "administrator"])
    )

    assert models.TeamAccess.objects.count() == 2
    assert models.TeamAccess.objects.filter(user=access.user).exists()

    client = APIClient()
    client.force_login(user)
    response = client.delete(
        f"/api/v1.0/teams/{team.id!s}/accesses/{access.id!s}/",
    )

    assert response.status_code == 204
    assert models.TeamAccess.objects.count() == 1


def test_api_team_accesses_delete_owners_except_owners():
    """
    Users should be able to delete the team access of another user
    for a team of which they are owner provided it is not an owner access.
    """
    user = factories.UserFactory()
    team = factories.TeamFactory(users=[(user, "owner")])
    access = factories.TeamAccessFactory(
        team=team, role=random.choice(["member", "administrator"])
    )

    assert models.TeamAccess.objects.count() == 2
    assert models.TeamAccess.objects.filter(user=access.user).exists()

    client = APIClient()
    client.force_login(user)
    response = client.delete(
        f"/api/v1.0/teams/{team.id!s}/accesses/{access.id!s}/",
    )

    assert response.status_code == 204
    assert models.TeamAccess.objects.count() == 1


def test_api_team_accesses_delete_owners_for_owners():
    """
    Users should not be allowed to delete the team access of another owner
    even for a team in which they are direct owner.
    """
    user = factories.UserFactory()
    team = factories.TeamFactory(users=[(user, "owner")])
    access = factories.TeamAccessFactory(team=team, role="owner")

    assert models.TeamAccess.objects.count() == 2
    assert models.TeamAccess.objects.filter(user=access.user).exists()

    client = APIClient()
    client.force_login(user)
    response = client.delete(
        f"/api/v1.0/teams/{team.id!s}/accesses/{access.id!s}/",
    )

    assert response.status_code == 403
    assert models.TeamAccess.objects.count() == 2


def test_api_team_accesses_delete_owners_last_owner():
    """
    It should not be possible to delete the last owner access from a team
    """
    user = factories.UserFactory()
    team = factories.TeamFactory()
    access = factories.TeamAccessFactory(team=team, user=user, role="owner")
    assert models.TeamAccess.objects.count() == 1

    client = APIClient()
    client.force_login(user)

    response = client.delete(
        f"/api/v1.0/teams/{team.id!s}/accesses/{access.id!s}/",
    )

    assert response.status_code == 403
    assert models.TeamAccess.objects.count() == 1


@responses.activate
def test_api_team_accesses_delete_webhook():
    """
    When the team has a webhook, deleting a team access should fire a call.
    """
    user = factories.UserFactory()
    team = factories.TeamFactory(users=[(user, "administrator")])
    access = factories.TeamAccessFactory(
        team=team, role=random.choice(["member", "administrator"])
    )
    # add webhook after access to prevent webhook from being triggered
    webhook = factories.TeamWebhookFactory(team=team)

    assert models.TeamAccess.objects.count() == 2
    assert models.TeamAccess.objects.filter(user=access.user).exists()

    client = APIClient()
    client.force_login(user)

    patch_response = responses.patch(webhook.url, status=200, json={})

    response = client.delete(
        f"/api/v1.0/teams/{team.id!s}/accesses/{access.id!s}/",
    )
    assert response.status_code == 204

    # Check the request was made
    assert patch_response.call_count == 1

    # Payload sent to scim provider
    scim_payload = json.loads(patch_response.calls[0].request.body)
    assert scim_payload == {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
        "Operations": [
            {
                "op": "remove",
                "path": "members",
                "value": [
                    {
                        "value": str(access.user.id),
                        "email": access.user.email,
                        "type": "User",
                    }
                ],
            }
        ],
    }

    assert models.TeamAccess.objects.count() == 1
    assert models.TeamAccess.objects.filter(user=access.user).exists() is False
