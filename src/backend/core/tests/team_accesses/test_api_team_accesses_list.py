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


def test_api_team_accesses_list_find_members(django_assert_num_queries):
    """
    Authenticated users should be able to search users access with a case-insensitive and
    partial query on the name.
    """
    dave = factories.UserFactory(name="dave bowman", email=None)
    frank = factories.UserFactory(name="frank poole", email=None)
    mary = factories.UserFactory(name="mary poole", email=None)
    nicole = factories.UserFactory(name="nicole foole", email=None)
    factories.UserFactory(email="tester@ministry.fr", name="john doe")
    factories.UserFactory(name="heywood floyd", email=None)
    factories.UserFactory(name="Andrei Smyslov", email=None)
    factories.TeamFactory.create_batch(10)

    # Add Mary, Nicole and Dave in the same team
    team = factories.TeamFactory(
        name="Odyssey",
        users=[
            (mary, models.RoleChoices.OWNER),
            (nicole, models.RoleChoices.ADMIN),
            (dave, models.RoleChoices.MEMBER),
        ],
    )
    factories.TeamFactory(users=[(frank, models.RoleChoices.MEMBER)])

    # Search users in the team Odyssey
    client = APIClient()
    client.force_login(mary)

    # 5 queries are needed here:
    # - 1 query: select on user authenticated
    # - 4 queries: get all users, owner included (2 more queries)
    with django_assert_num_queries(5):
        response = client.get(
            f"/api/v1.0/teams/{team.id!s}/accesses/",
        )
    assert response.status_code == HTTP_200_OK
    assert response.json()["count"] == 3

    # We can find David Bowman
    # 3 queries are needed here:
    # - 1 query: user authenticated
    # - 2 queries: search user query with match
    with django_assert_num_queries(3):
        response = client.get(
            f"/api/v1.0/teams/{team.id!s}/accesses/?q=bowman",
        )
    assert response.status_code == HTTP_200_OK
    assert response.json()["count"] == 1
    dave_access = dave.accesses.get(team=team)
    assert response.json()["results"][0]["id"] == str(dave_access.id)

    # We can find Nicole
    # 3 queries are needed here:
    # - 1 query: user authenticated
    # - 2 queries: search user query with match
    with django_assert_num_queries(3):
        response = client.get(
            f"/api/v1.0/teams/{team.id!s}/accesses/?q=nicol",
        )
    assert response.status_code == HTTP_200_OK
    assert response.json()["count"] == 1
    nicole_access = nicole.accesses.get(team=team)
    assert response.json()["results"][0]["id"] == str(nicole_access.id)

    # We can find Nicole and Mary
    # 5 queries are needed here:
    # - 1 query: select on user authenticated
    # - 4 queries: search user query with match and the owner found (2 more queries)
    with django_assert_num_queries(5):
        response = client.get(
            f"/api/v1.0/teams/{team.id!s}/accesses/?q=ool",
        )
    assert response.status_code == HTTP_200_OK
    assert response.json()["count"] == 2
    user_access_ids = sorted([user["id"] for user in response.json()["results"]])
    mary_access = mary.accesses.get(team=team)
    assert sorted([str(mary_access.id), str(nicole_access.id)]) == user_access_ids

    # We cannot find Andrei, because he isn't a member of the current team
    # 2 queries are needed here:
    # - 1 query: select on user authenticated
    # - 1 query: search user query with no match
    with django_assert_num_queries(2):
        response = client.get(
            f"/api/v1.0/teams/{team.id!s}/accesses/?q=andrei",
        )
    assert response.status_code == HTTP_200_OK
    assert response.json()["count"] == 0

    # We can find Mary
    # 5 queries are needed here:
    # - 1 query: select on user authenticated
    # - 4 queries: search user query with match and an owner found (2 more queries)
    with django_assert_num_queries(5):
        response = client.get(
            f"/api/v1.0/teams/{team.id!s}/accesses/?q=mary",
        )
    assert response.status_code == HTTP_200_OK
    assert response.json()["count"] == 1
    assert response.json()["results"][0]["id"] == str(mary_access.id)


def test_api_team_accesses__list_find_members_by_email():
    """
    Authenticated users should be able to search users access with a case-insensitive and
    partial query on the email.
    """
    user = factories.UserFactory(name=None)

    # set all names to None to match only on emails
    colleague1 = factories.UserFactory(name=None, email="prudence_crandall@edu.us")
    colleague2 = factories.UserFactory(name=None, email="reinebrunehaut@gouv.fr")
    colleague3 = factories.UserFactory(name=None, email="artemisia.gentileschi@arte.it")

    # Add all colleague in the same team
    team = factories.TeamFactory(
        users=[
            (user, models.RoleChoices.ADMIN),
            (colleague1, models.RoleChoices.OWNER),
            (colleague2, models.RoleChoices.ADMIN),
            (colleague3, models.RoleChoices.MEMBER),
        ],
    )
    factories.TeamAccessFactory.create_batch(4)

    # Create another team with similar email
    factories.TeamFactory(
        users=[
            (
                factories.UserFactory(name=None, email="bruneau@gouv.fr"),
                models.RoleChoices.ADMIN,
            ),
        ],
    )

    # Search users in the team Odyssey
    client = APIClient()
    client.force_login(user)

    response = client.get(
        f"/api/v1.0/teams/{team.id!s}/accesses/?q=BRUNE",
    )
    assert response.status_code == HTTP_200_OK
    assert response.json()["count"] == 1
    assert response.json()["results"][0]["user"]["email"] == "reinebrunehaut@gouv.fr"


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
