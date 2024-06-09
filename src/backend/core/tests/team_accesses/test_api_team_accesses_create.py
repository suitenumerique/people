"""
Test for team accesses API endpoints in People's core app : create
"""

import json
import random
import re

import pytest
import responses
from rest_framework.test import APIClient

from core import factories, models

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


def test_api_team_accesses_create_webhook():
    """
    When the team has a webhook, creating a team access should fire a call.
    """
    user, other_user = factories.UserFactory.create_batch(2)

    team = factories.TeamFactory(users=[(user, "owner")])
    webhook = factories.TeamWebhookFactory(team=team)

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
