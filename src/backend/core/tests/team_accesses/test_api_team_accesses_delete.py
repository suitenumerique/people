"""
Test for team accesses API endpoints in People's core app : delete
"""

import random

import pytest
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
    identity = factories.IdentityFactory()
    user = identity.user

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
    identity = factories.IdentityFactory()
    user = identity.user

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
    identity = factories.IdentityFactory()
    user = identity.user

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
    identity = factories.IdentityFactory()
    user = identity.user

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
    identity = factories.IdentityFactory()
    user = identity.user

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
    identity = factories.IdentityFactory()
    user = identity.user

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
