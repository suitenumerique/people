"""
Unit tests for the TeamAccess model
"""

import json
import re

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError

import pytest
import responses

from core import factories, models

pytestmark = pytest.mark.django_db


def test_models_team_accesses_str():
    """
    The str representation should include user name, team full name and role.
    """
    user = factories.UserFactory()
    access = factories.TeamAccessFactory(
        role="member",
        user=user,
        team__name="admins",
    )
    assert str(access) == f"{user} is {access.role} in team {access.team}"


def test_models_team_accesses_unique():
    """Team accesses should be unique for a given couple of user and team."""
    access = factories.TeamAccessFactory()

    with pytest.raises(
        ValidationError,
        match="Team/user relation with this User and Team already exists.",
    ):
        factories.TeamAccessFactory(user=access.user, team=access.team)


def test_models_team_accesses_create_webhook():
    """
    When the team has a webhook, creating a team access should fire a call.
    """
    user = factories.UserFactory()
    team = factories.TeamFactory()
    webhook = factories.TeamWebhookFactory(team=team)

    with responses.RequestsMock() as rsps:
        # Ensure successful response by scim provider using "responses":
        rsp = rsps.add(
            rsps.PATCH,
            re.compile(r".*/Groups/.*"),
            body="{}",
            status=200,
            content_type="application/json",
        )

        models.TeamAccess.objects.create(user=user, team=team)

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
                            "value": str(user.id),
                            "email": user.email,
                            "type": "User",
                        }
                    ],
                }
            ],
        }


@responses.activate
def test_models_team_accesses_delete_webhook():
    """
    When the team has a webhook, deleting a team access should fire a call.
    """
    team = factories.TeamFactory()
    access = factories.TeamAccessFactory(team=team)
    # add webhook after access to prevent webhook from being triggered
    webhook = factories.TeamWebhookFactory(team=team)

    # Ensure successful response by scim provider using "responses":
    rsp = responses.patch(webhook.url, status=200, json={})

    access.delete()

    assert rsp.call_count == 1

    # Payload sent to scim provider
    payload = json.loads(rsp.calls[0].request.body)
    assert payload == {
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

    assert models.TeamAccess.objects.exists() is False


# get_abilities


def test_models_team_access_get_abilities_anonymous():
    """Check abilities returned for an anonymous user."""
    access = factories.TeamAccessFactory()
    abilities = access.get_abilities(AnonymousUser())
    assert abilities == {
        "delete": False,
        "get": False,
        "patch": False,
        "put": False,
        "set_role_to": [],
    }


def test_models_team_access_get_abilities_authenticated():
    """Check abilities returned for an authenticated user."""
    access = factories.TeamAccessFactory()
    user = factories.UserFactory()
    abilities = access.get_abilities(user)
    assert abilities == {
        "delete": False,
        "get": False,
        "patch": False,
        "put": False,
        "set_role_to": [],
    }


# - for owner


def test_models_team_access_get_abilities_for_owner_of_self_allowed():
    """
    Check abilities of self access for the owner of a team when there is more than one user left.
    """
    access = factories.TeamAccessFactory(role="owner")
    factories.TeamAccessFactory(team=access.team, role="owner")
    abilities = access.get_abilities(access.user)
    assert abilities == {
        "delete": True,
        "get": True,
        "patch": True,
        "put": True,
        "set_role_to": ["administrator", "member"],
    }


def test_models_team_access_get_abilities_for_owner_of_self_last():
    """Check abilities of self access for the owner of a team when there is only one owner left."""
    access = factories.TeamAccessFactory(role="owner")
    abilities = access.get_abilities(access.user)
    assert abilities == {
        "delete": False,
        "get": True,
        "patch": False,
        "put": False,
        "set_role_to": [],
    }


def test_models_team_access_get_abilities_for_owner_of_owner():
    """Check abilities of owner access for the owner of a team."""
    access = factories.TeamAccessFactory(role="owner")
    factories.TeamAccessFactory(team=access.team)  # another one
    user = factories.TeamAccessFactory(team=access.team, role="owner").user
    abilities = access.get_abilities(user)
    assert abilities == {
        "delete": False,
        "get": True,
        "patch": False,
        "put": False,
        "set_role_to": [],
    }


def test_models_team_access_get_abilities_for_owner_of_administrator():
    """Check abilities of administrator access for the owner of a team."""
    access = factories.TeamAccessFactory(role="administrator")
    factories.TeamAccessFactory(team=access.team)  # another one
    user = factories.TeamAccessFactory(team=access.team, role="owner").user
    abilities = access.get_abilities(user)
    assert abilities == {
        "delete": True,
        "get": True,
        "patch": True,
        "put": True,
        "set_role_to": ["owner", "member"],
    }


def test_models_team_access_get_abilities_for_owner_of_member():
    """Check abilities of member access for the owner of a team."""
    access = factories.TeamAccessFactory(role="member")
    factories.TeamAccessFactory(team=access.team)  # another one
    user = factories.TeamAccessFactory(team=access.team, role="owner").user
    abilities = access.get_abilities(user)
    assert abilities == {
        "delete": True,
        "get": True,
        "patch": True,
        "put": True,
        "set_role_to": ["owner", "administrator"],
    }


# - for administrator


def test_models_team_access_get_abilities_for_administrator_of_owner():
    """Check abilities of owner access for the administrator of a team."""
    access = factories.TeamAccessFactory(role="owner")
    factories.TeamAccessFactory(team=access.team)  # another one
    user = factories.TeamAccessFactory(team=access.team, role="administrator").user
    abilities = access.get_abilities(user)
    assert abilities == {
        "delete": False,
        "get": True,
        "patch": False,
        "put": False,
        "set_role_to": [],
    }


def test_models_team_access_get_abilities_for_administrator_of_administrator():
    """Check abilities of administrator access for the administrator of a team."""
    access = factories.TeamAccessFactory(role="administrator")
    factories.TeamAccessFactory(team=access.team)  # another one
    user = factories.TeamAccessFactory(team=access.team, role="administrator").user
    abilities = access.get_abilities(user)
    assert abilities == {
        "delete": True,
        "get": True,
        "patch": True,
        "put": True,
        "set_role_to": ["member"],
    }


def test_models_team_access_get_abilities_for_administrator_of_member():
    """Check abilities of member access for the administrator of a team."""
    access = factories.TeamAccessFactory(role="member")
    factories.TeamAccessFactory(team=access.team)  # another one
    user = factories.TeamAccessFactory(team=access.team, role="administrator").user
    abilities = access.get_abilities(user)
    assert abilities == {
        "delete": True,
        "get": True,
        "patch": True,
        "put": True,
        "set_role_to": ["administrator"],
    }


# - for member


def test_models_team_access_get_abilities_for_member_of_owner():
    """Check abilities of owner access for the member of a team."""
    access = factories.TeamAccessFactory(role="owner")
    factories.TeamAccessFactory(team=access.team)  # another one
    user = factories.TeamAccessFactory(team=access.team, role="member").user
    abilities = access.get_abilities(user)
    assert abilities == {
        "delete": False,
        "get": True,
        "patch": False,
        "put": False,
        "set_role_to": [],
    }


def test_models_team_access_get_abilities_for_member_of_administrator():
    """Check abilities of administrator access for the member of a team."""
    access = factories.TeamAccessFactory(role="administrator")
    factories.TeamAccessFactory(team=access.team)  # another one
    user = factories.TeamAccessFactory(team=access.team, role="member").user
    abilities = access.get_abilities(user)
    assert abilities == {
        "delete": False,
        "get": True,
        "patch": False,
        "put": False,
        "set_role_to": [],
    }


def test_models_team_access_get_abilities_for_member_of_member_user(
    django_assert_num_queries,
):
    """Check abilities of member access for the member of a team."""
    access = factories.TeamAccessFactory(role="member")
    factories.TeamAccessFactory(team=access.team)  # another one
    user = factories.TeamAccessFactory(team=access.team, role="member").user

    with django_assert_num_queries(1):
        abilities = access.get_abilities(user)

    assert abilities == {
        "delete": False,
        "get": True,
        "patch": False,
        "put": False,
        "set_role_to": [],
    }


def test_models_team_access_get_abilities_preset_role(django_assert_num_queries):
    """No query is done if the role is preset, e.g., with a query annotation."""
    access = factories.TeamAccessFactory(role="member")
    user = factories.TeamAccessFactory(team=access.team, role="member").user
    access.user_role = "member"

    with django_assert_num_queries(0):
        abilities = access.get_abilities(user)

    assert abilities == {
        "delete": False,
        "get": True,
        "patch": False,
        "put": False,
        "set_role_to": [],
    }
