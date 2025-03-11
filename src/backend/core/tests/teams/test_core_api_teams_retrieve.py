"""
Tests for Teams API endpoint in People's core app: retrieve
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories

pytestmark = pytest.mark.django_db


def test_api_teams_retrieve_anonymous():
    """Anonymous users should not be allowed to retrieve a team."""
    team = factories.TeamFactory()
    response = APIClient().get(f"/api/v1.0/teams/{team.id}/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_teams_retrieve_authenticated_unrelated():
    """
    Authenticated users should not be allowed to retrieve a team to which they are
    not related.
    """
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    team = factories.TeamFactory()

    response = client.get(
        f"/api/v1.0/teams/{team.id!s}/",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No Team matches the given query."}


def test_api_teams_retrieve_authenticated_related():
    """
    Authenticated users should be allowed to retrieve a team to which they
    are related whatever the role.
    """
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    team = factories.TeamFactory()
    access1 = factories.TeamAccessFactory(team=team, user=user)
    access2 = factories.TeamAccessFactory(team=team)

    response = client.get(
        f"/api/v1.0/teams/{team.id!s}/",
    )

    assert response.status_code == status.HTTP_200_OK
    assert sorted(response.json().pop("accesses")) == sorted(
        [
            str(access1.id),
            str(access2.id),
        ]
    )
    assert response.json() == {
        "abilities": team.get_abilities(user),
        "created_at": team.created_at.isoformat().replace("+00:00", "Z"),
        "depth": 1,
        "id": str(team.id),
        "is_visible_all_services": False,
        "name": team.name,
        "numchild": 0,
        "path": team.path,
        "service_providers": [],
        "updated_at": team.updated_at.isoformat().replace("+00:00", "Z"),
    }


@pytest.mark.parametrize(
    "role",
    ["owner", "administrator", "member"],
)
def test_api_teams_retrieve_authenticated_related_parent(client, role):
    """
    Authenticated users should be allowed to retrieve a parent team
    to which they are related through the child team whatever the role.
    """
    user = factories.UserFactory()

    client.force_login(user)

    root_team = factories.TeamFactory(name="Root")
    first_team = factories.TeamFactory(name="First", parent_id=root_team.pk)
    second_team = factories.TeamFactory(name="Second", parent_id=first_team.pk)

    # user is a member of the second team
    factories.TeamAccessFactory(team=second_team, user=user, role=role)

    response = client.get(f"/api/v1.0/teams/{first_team.pk!s}/")

    # the abilities enforces the "get" via the queryset
    abilities = first_team.get_abilities(user)
    abilities["get"] = True

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "abilities": abilities,
        "accesses": [],
        "created_at": first_team.created_at.isoformat().replace("+00:00", "Z"),
        "depth": 2,
        "id": str(first_team.pk),
        "is_visible_all_services": False,
        "name": first_team.name,
        "numchild": 1,
        "path": first_team.path,
        "service_providers": [],
        "updated_at": first_team.updated_at.isoformat().replace("+00:00", "Z"),
    }


@pytest.mark.parametrize(
    "role",
    ["owner", "administrator", "member"],
)
def test_api_teams_retrieve_authenticated_related_children(client, role):
    """
    Authenticated users should NOT be allowed to retrieve a child team
    to which they are related through the parent team whatever the role.
    """
    user = factories.UserFactory()

    client.force_login(user)

    root_team = factories.TeamFactory(name="Root")
    first_team = factories.TeamFactory(name="First", parent_id=root_team.pk)
    second_team = factories.TeamFactory(name="Second", parent_id=first_team.pk)

    # user is a member of the first team
    factories.TeamAccessFactory(team=first_team, user=user, role=role)

    response = client.get(f"/api/v1.0/teams/{second_team.pk!s}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No Team matches the given query."}
