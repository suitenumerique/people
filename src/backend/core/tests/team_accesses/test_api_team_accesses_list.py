"""
Test for team accesses API endpoints in People's core app : list
"""
import pytest
from rest_framework.test import APIClient

from core import factories, models

pytestmark = pytest.mark.django_db


def test_api_team_accesses_list_anonymous():
    """Anonymous users should not be allowed to list team accesses."""
    team = factories.TeamFactory()
    factories.TeamAccessFactory.create_batch(2, team=team)

    response = APIClient().get(f"/api/v1.0/teams/{team.id!s}/accesses/")
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_team_accesses_list_authenticated_unrelated():
    """
    Authenticated users should not be allowed to list team accesses for a team
    to which they are not related.
    """
    identity = factories.IdentityFactory()
    user = identity.user

    team = factories.TeamFactory()
    factories.TeamAccessFactory.create_batch(3, team=team)

    # Accesses for other teams to which the user is related should not be listed either
    other_access = factories.TeamAccessFactory(user=user)
    factories.TeamAccessFactory(team=other_access.team)

    client = APIClient()
    client.force_login(user)
    response = client.get(
        f"/api/v1.0/teams/{team.id!s}/accesses/",
    )
    assert response.status_code == 200
    assert response.json() == {
        "count": 0,
        "next": None,
        "previous": None,
        "results": [],
    }


def test_api_team_accesses_list_authenticated_related():
    """
    Authenticated users should be able to list team accesses for a team
    to which they are related, whatever their role in the team.
    """
    identity = factories.IdentityFactory()
    user = identity.user

    team = factories.TeamFactory()
    user_access = models.TeamAccess.objects.create(team=team, user=user)  # random role
    access1, access2 = factories.TeamAccessFactory.create_batch(2, team=team)

    # Accesses for other teams to which the user is related should not be listed either
    other_access = factories.TeamAccessFactory(user=user)
    factories.TeamAccessFactory(team=other_access.team)

    client = APIClient()
    client.force_login(user)
    response = client.get(
        f"/api/v1.0/teams/{team.id!s}/accesses/",
    )

    assert response.status_code == 200
    assert response.json()["count"] == 3
    assert sorted(response.json()["results"], key=lambda x: x["id"]) == sorted(
        [
            {
                "id": str(user_access.id),
                "user": str(user.id),
                "role": user_access.role,
                "abilities": user_access.get_abilities(user),
            },
            {
                "id": str(access1.id),
                "user": str(access1.user.id),
                "role": access1.role,
                "abilities": access1.get_abilities(user),
            },
            {
                "id": str(access2.id),
                "user": str(access2.user.id),
                "role": access2.role,
                "abilities": access2.get_abilities(user),
            },
        ],
        key=lambda x: x["id"],
    )
