"""
Tests for Teams API endpoint in People's core app: delete
"""

import pytest
from rest_framework.status import (
    HTTP_204_NO_CONTENT,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)
from rest_framework.test import APIClient

from core import factories, models

pytestmark = pytest.mark.django_db


def test_api_teams_delete_anonymous():
    """Anonymous users should not be allowed to destroy a team."""
    team = factories.TeamFactory()

    response = APIClient().delete(
        f"/api/v1.0/teams/{team.id!s}/",
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert models.Team.objects.count() == 1


def test_api_teams_delete_authenticated_unrelated():
    """
    Authenticated users should not be allowed to delete a team to which they are not
    related.
    """
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    team = factories.TeamFactory()

    response = client.delete(
        f"/api/v1.0/teams/{team.id!s}/",
    )

    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No Team matches the given query."}
    assert models.Team.objects.count() == 1


def test_api_teams_delete_authenticated_member():
    """
    Authenticated users should not be allowed to delete a team for which they are
    only a member.
    """
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    team = factories.TeamFactory(users=[(user, "member")])

    response = client.delete(
        f"/api/v1.0/teams/{team.id}/",
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "You do not have permission to perform this action."
    }
    assert models.Team.objects.count() == 1


def test_api_teams_delete_authenticated_administrator():
    """
    Authenticated users should not be allowed to delete a team for which they are
    administrator.
    """
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    team = factories.TeamFactory(users=[(user, "administrator")])

    response = client.delete(
        f"/api/v1.0/teams/{team.id}/",
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "You do not have permission to perform this action."
    }
    assert models.Team.objects.count() == 1


def test_api_teams_delete_authenticated_owner():
    """
    Authenticated users should be able to delete a team for which they are directly
    owner.
    """
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    team = factories.TeamFactory(users=[(user, "owner")])

    response = client.delete(
        f"/api/v1.0/teams/{team.id}/",
    )

    assert response.status_code == HTTP_204_NO_CONTENT
    assert models.Team.objects.exists() is False


@pytest.mark.parametrize(
    "role",
    ["owner", "administrator", "member"],
)
def test_api_teams_delete_authenticated_owner_parent_team(client, role):
    """
    Authenticated users should not be able to delete a parent team they
    don't own.
    """
    user = factories.UserFactory()

    client.force_login(user)

    root_team = factories.TeamFactory(name="Root")
    first_team = factories.TeamFactory(name="First", parent_id=root_team.pk)
    second_team = factories.TeamFactory(name="Second", parent_id=first_team.pk)

    # user is a member of the second team
    factories.TeamAccessFactory(team=second_team, user=user, role=role)

    response = client.delete(f"/api/v1.0/teams/{first_team.pk}/")

    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "You do not have permission to perform this action."
    }
    assert models.Team.objects.count() == 3


@pytest.mark.parametrize(
    "role",
    ["owner", "administrator", "member"],
)
def test_api_teams_delete_authenticated_owner_child_team(client, role):
    """
    Authenticated users should not be able to delete a children team they
    don't own.
    """
    user = factories.UserFactory()

    client.force_login(user)

    root_team = factories.TeamFactory(name="Root")
    first_team = factories.TeamFactory(name="First", parent_id=root_team.pk)
    second_team = factories.TeamFactory(name="Second", parent_id=first_team.pk)

    # user is a member of the first team
    factories.TeamAccessFactory(team=first_team, user=user, role=role)

    response = client.delete(f"/api/v1.0/teams/{second_team.pk}/")

    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No Team matches the given query."}
    assert models.Team.objects.count() == 3
