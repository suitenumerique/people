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
    identity = factories.IdentityFactory(is_main=True)
    user = identity.user

    team = factories.TeamFactory()
    user_access = models.TeamAccess.objects.create(team=team, user=user)  # random role

    # other team members should appear
    other_member = factories.UserFactory()
    other_member_identity = factories.IdentityFactory(is_main=True, user=other_member)
    access1 = factories.TeamAccessFactory.create(team=team, user=other_member)

    # Accesses for other teams to which the user is related should not be listed either
    other_access = factories.TeamAccessFactory(user=user)
    factories.TeamAccessFactory(team=other_access.team)

    client = APIClient()
    client.force_login(user)
    response = client.get(
        f"/api/v1.0/teams/{team.id!s}/accesses/",
    )

    assert response.status_code == 200
    assert response.json()["count"] == 2
    assert sorted(response.json()["results"], key=lambda x: x["id"]) == sorted(
        [
            {
                "id": str(user_access.id),
                "user": {
                    "id": str(user_access.user.id),
                    "email": str(identity.email),
                    "name": str(identity.name),
                },
                "role": str(user_access.role),
                "abilities": user_access.get_abilities(user),
            },
            {
                "id": str(access1.id),
                "user": {
                    "id": str(access1.user.id),
                    "email": str(other_member_identity.email),
                    "name": str(other_member_identity.name),
                },
                "role": str(access1.role),
                "abilities": access1.get_abilities(user),
            },
        ],
        key=lambda x: x["id"],
    )


def test_api_team_accesses_list_authenticated_main_identity():
    """
    Name and email should be returned from main identity only
    """
    user = factories.UserFactory()
    identity = factories.IdentityFactory(user=user, is_main=True)
    factories.IdentityFactory(user=user)  # additional non-main identity

    team = factories.TeamFactory()
    models.TeamAccess.objects.create(team=team, user=user)  # random role

    # other team members should appear, with correct identity
    other_user = factories.UserFactory()
    other_main_identity = factories.IdentityFactory(is_main=True, user=other_user)
    factories.IdentityFactory(user=other_user)
    factories.TeamAccessFactory.create(team=team, user=other_user)

    # Accesses for other teams to which the user is related should not be listed either
    other_access = factories.TeamAccessFactory(user=user)
    factories.TeamAccessFactory(team=other_access.team)

    client = APIClient()
    client.force_login(user)
    response = client.get(
        f"/api/v1.0/teams/{team.id!s}/accesses/",
    )

    assert response.status_code == 200
    assert response.json()["count"] == 2
    users_info = [
        (access["user"]["email"], access["user"]["name"])
        for access in response.json()["results"]
    ]
    # user information should be returned from main identity
    assert sorted(users_info) == sorted(
        [
            (str(identity.email), str(identity.name)),
            (str(other_main_identity.email), str(other_main_identity.name)),
        ]
    )


def test_api_team_accesses_list_authenticated_constant_numqueries(
    django_assert_num_queries,
):
    """
    The number of queries should not depend on the amount of fetched accesses.
    """
    user = factories.UserFactory()
    factories.IdentityFactory(user=user, is_main=True)

    team = factories.TeamFactory()
    models.TeamAccess.objects.create(team=team, user=user)  # random role

    client = APIClient()
    client.force_login(user)
    # Only 4 queries are needed to efficiently fetch team accesses,
    # related users and identities :
    # - query retrieving logged-in user for user_role annotation
    # - count from pagination
    # - query prefetching users' main identity
    # - distinct from viewset
    with django_assert_num_queries(4):
        response = client.get(
            f"/api/v1.0/teams/{team.id!s}/accesses/",
        )

    # create 20 new team members
    for _ in range(20):
        extra_user = factories.IdentityFactory(is_main=True).user
        factories.TeamAccessFactory(team=team, user=extra_user)

    # num queries should still be 4
    with django_assert_num_queries(4):
        response = client.get(
            f"/api/v1.0/teams/{team.id!s}/accesses/",
        )

    assert response.status_code == 200
    assert response.json()["count"] == 21
