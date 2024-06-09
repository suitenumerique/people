"""
Test for team accesses API endpoints in People's core app : list
"""

import pytest
from rest_framework.status import HTTP_200_OK
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
    user = factories.UserFactory()
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
    to which they are related, with a given role.
    """
    user, administrator, owner = factories.UserFactory.create_batch(3)
    team = factories.TeamFactory()

    access1 = factories.TeamAccessFactory.create(team=team, user=owner, role="owner")
    access2 = factories.TeamAccessFactory.create(
        team=team, user=administrator, role="administrator"
    )

    # Ensure this user's role is different from other team members to test abilities' computation
    user_access = models.TeamAccess.objects.create(team=team, user=user, role="member")

    # Grant other team accesses to the user, they should not be listed either
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
                "user": {
                    "id": str(user_access.user.id),
                    "email": str(user.email),
                    "name": str(user.name),
                },
                "role": str(user_access.role),
                "abilities": user_access.get_abilities(user),
            },
            {
                "id": str(access1.id),
                "user": {
                    "id": str(access1.user.id),
                    "email": str(owner.email),
                    "name": str(owner.name),
                },
                "role": str(access1.role),
                "abilities": access1.get_abilities(user),
            },
            {
                "id": str(access2.id),
                "user": {
                    "id": str(access2.user.id),
                    "email": str(administrator.email),
                    "name": str(administrator.name),
                },
                "role": str(access2.role),
                "abilities": access2.get_abilities(user),
            },
        ],
        key=lambda x: x["id"],
    )


def test_api_team_accesses_list_authenticated_constant_numqueries(
    django_assert_num_queries,
):
    """
    The number of queries should not depend on the amount of fetched accesses.
    """
    user = factories.UserFactory()
    team = factories.TeamFactory()
    models.TeamAccess.objects.create(team=team, user=user)  # random role

    client = APIClient()
    client.force_login(user)
    # Only 3 queries are needed to efficiently fetch team accesses,
    # related users and identities :
    # - query retrieving logged-in user for user_role annotation
    # - count from pagination
    # - distinct from viewset
    with django_assert_num_queries(3):
        response = client.get(
            f"/api/v1.0/teams/{team.id!s}/accesses/",
        )

    # create 20 new team members
    for _ in range(20):
        extra_user = factories.UserFactory()
        factories.TeamAccessFactory(team=team, user=extra_user)

    # num queries should still be the same
    with django_assert_num_queries(3):
        response = client.get(
            f"/api/v1.0/teams/{team.id!s}/accesses/",
        )

    assert response.status_code == 200
    assert response.json()["count"] == 21


def test_api_team_accesses_list_authenticated_ordering():
    """Team accesses can be ordered by "role"."""

    user = factories.UserFactory()
    team = factories.TeamFactory()
    models.TeamAccess.objects.create(team=team, user=user)

    # create 20 new team members
    for _ in range(20):
        extra_user = factories.UserFactory()
        factories.TeamAccessFactory(team=team, user=extra_user)

    client = APIClient()
    client.force_login(user)

    response = client.get(
        f"/api/v1.0/teams/{team.id!s}/accesses/?ordering=role",
    )
    assert response.status_code == HTTP_200_OK
    assert response.json()["count"] == 21

    results = [team_access["role"] for team_access in response.json()["results"]]
    assert sorted(results) == results

    response = client.get(
        f"/api/v1.0/teams/{team.id!s}/accesses/?ordering=-role",
    )
    assert response.status_code == HTTP_200_OK
    assert response.json()["count"] == 21

    results = [team_access["role"] for team_access in response.json()["results"]]
    assert sorted(results, reverse=True) == results


@pytest.mark.parametrize("ordering_field", ["email", "name"])
def test_api_team_accesses_list_authenticated_ordering_user(ordering_field):
    """Team accesses can be ordered by user's fields."""

    user = factories.UserFactory()
    team = factories.TeamFactory()
    models.TeamAccess.objects.create(team=team, user=user)

    # create 20 new team members
    for _ in range(20):
        extra_user = factories.UserFactory()
        factories.TeamAccessFactory(team=team, user=extra_user)

    client = APIClient()
    client.force_login(user)

    response = client.get(
        f"/api/v1.0/teams/{team.id!s}/accesses/?ordering=user__{ordering_field}",
    )
    assert response.status_code == HTTP_200_OK
    assert response.json()["count"] == 21

    def normalize(x):
        """Mimic Django order_by, which is case-insensitive and space-insensitive"""
        return x.casefold().replace(" ", "")

    results = [
        team_access["user"][ordering_field]
        for team_access in response.json()["results"]
    ]
    assert sorted(results, key=normalize) == results
