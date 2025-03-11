"""
Tests for Teams API endpoint in People's core app: list
"""

import pytest
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED
from rest_framework.test import APIClient

from core import factories

pytestmark = pytest.mark.django_db


def test_api_teams_list_anonymous():
    """Anonymous users should not be allowed to list teams."""
    factories.TeamFactory.create_batch(2)

    response = APIClient().get("/api/v1.0/teams/")

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_teams_list_authenticated():
    """
    Authenticated users should be able to list teams
    they are an owner/administrator/member of.
    """
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    expected_ids = {
        str(access.team.id)
        for access in factories.TeamAccessFactory.create_batch(5, user=user)
    }
    factories.TeamFactory.create_batch(2)  # Other teams

    response = client.get(
        "/api/v1.0/teams/",
    )

    assert response.status_code == HTTP_200_OK
    results = response.json()

    assert len(results) == 5
    results_id = {result["id"] for result in results}
    assert expected_ids == results_id


def test_api_teams_list_authenticated_distinct():
    """A team with several related users should only be listed once."""
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    other_user = factories.UserFactory()

    team = factories.TeamFactory(users=[user, other_user])

    response = client.get(
        "/api/v1.0/teams/",
    )

    assert response.status_code == HTTP_200_OK
    content = response.json()
    assert len(content) == 1
    assert content[0]["id"] == str(team.id)


def test_api_teams_order():
    """
    Test that the endpoint GET teams is sorted in 'created_at' descending order by default.
    """
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    team_ids = [
        str(team.id) for team in factories.TeamFactory.create_batch(5, users=[user])
    ]

    response = client.get(
        "/api/v1.0/teams/",
    )

    assert response.status_code == 200

    response_data = response.json()
    response_team_ids = [team["id"] for team in response_data]

    team_ids.reverse()
    assert response_team_ids == team_ids, (
        "created_at values are not sorted from newest to oldest"
    )


def test_api_teams_order_param():
    """
    Test that the 'created_at' field is sorted in ascending order
    when the 'ordering' query parameter is set.
    """
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    team_ids = [
        str(team.id) for team in factories.TeamFactory.create_batch(5, users=[user])
    ]

    response = client.get(
        "/api/v1.0/teams/?ordering=created_at",
    )
    assert response.status_code == 200

    response_data = response.json()
    response_team_ids = [team["id"] for team in response_data]

    assert response_team_ids == team_ids, (
        "created_at values are not sorted from oldest to newest"
    )


@pytest.mark.parametrize(
    "role,local_team_abilities",
    [
        (
            "owner",
            {
                "delete": True,
                "get": True,
                "manage_accesses": True,
                "patch": True,
                "put": True,
            },
        ),
        (
            "administrator",
            {
                "delete": False,
                "get": True,
                "manage_accesses": True,
                "patch": True,
                "put": True,
            },
        ),
        (
            "member",
            {
                "delete": False,
                "get": True,
                "manage_accesses": False,
                "patch": False,
                "put": False,
            },
        ),
    ],
)
def test_api_teams_list_authenticated_team_tree(client, role, local_team_abilities):
    """
    Authenticated users should be able to list teams
    they are an owner/administrator/member of, or any parent teams.
    """
    user = factories.UserFactory()

    client.force_login(user)

    root_team = factories.TeamFactory(name="Root")
    first_team = factories.TeamFactory(name="First", parent_id=root_team.pk)
    second_team = factories.TeamFactory(name="Second", parent_id=first_team.pk)
    third_team = factories.TeamFactory(name="Third", parent_id=second_team.pk)
    _fourth_team = factories.TeamFactory(name="Fourth", parent_id=third_team.pk)

    # user is a member of the second team
    user_access = factories.TeamAccessFactory(team=second_team, user=user, role=role)

    response = client.get("/api/v1.0/teams/")

    assert response.status_code == HTTP_200_OK
    # By default, the teams are sorted by 'created_at' descending
    assert response.json() == [
        {
            # I have the abilities only on the team I have a specific role
            "abilities": local_team_abilities,
            "accesses": [str(user_access.pk)],
            "created_at": second_team.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "depth": 3,
            "id": str(second_team.pk),
            "is_visible_all_services": False,
            "name": "Second",
            "numchild": 1,
            "path": second_team.path,
            "service_providers": [],
            "updated_at": second_team.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        },
        {
            # For parent teams, I only have the ability to list/retrieve
            "abilities": {
                "delete": False,
                "get": True,
                "manage_accesses": False,
                "patch": False,
                "put": False,
            },
            "accesses": [],
            "created_at": first_team.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "depth": 2,
            "id": str(first_team.pk),
            "is_visible_all_services": False,
            "name": "First",
            "numchild": 1,
            "path": first_team.path,
            "service_providers": [],
            "updated_at": first_team.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        },
        {
            # For parent teams, I only have the ability to list/retrieve
            "abilities": {
                "delete": False,
                "get": True,
                "manage_accesses": False,
                "patch": False,
                "put": False,
            },
            "accesses": [],
            "created_at": root_team.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "depth": 1,
            "id": str(root_team.pk),
            "is_visible_all_services": False,
            "name": "Root",
            "numchild": 1,
            "path": root_team.path,
            "service_providers": [],
            "updated_at": root_team.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        },
    ]


@pytest.mark.parametrize(
    "role,local_team_abilities",
    [
        (
            "owner",
            {
                "delete": True,
                "get": True,
                "manage_accesses": True,
                "patch": True,
                "put": True,
            },
        ),
        (
            "administrator",
            {
                "delete": False,
                "get": True,
                "manage_accesses": True,
                "patch": True,
                "put": True,
            },
        ),
        (
            "member",
            {
                "delete": False,
                "get": True,
                "manage_accesses": False,
                "patch": False,
                "put": False,
            },
        ),
    ],
)
def test_api_teams_list_authenticated_team_different_organization(
    client, role, local_team_abilities
):
    """
    Authenticated users should be able to list teams they
    are an owner/administrator/member of and any parent teams
    only if from the same organization.
    """
    organization = factories.OrganizationFactory(with_registration_id=True)
    user = factories.UserFactory(organization=organization)

    other_organization = factories.OrganizationFactory(with_registration_id=True)
    root_team = factories.TeamFactory(name="Root", organization=other_organization)
    first_team = factories.TeamFactory(
        name="First", parent_id=root_team.pk, organization=other_organization
    )
    second_team = factories.TeamFactory(
        name="Second", parent_id=first_team.pk, organization=other_organization
    )
    third_team = factories.TeamFactory(
        name="Third", parent_id=second_team.pk, organization=other_organization
    )
    _fourth_team = factories.TeamFactory(
        name="Fourth", parent_id=third_team.pk, organization=other_organization
    )

    client.force_login(user)

    # user is a member of the second team
    user_access = factories.TeamAccessFactory(team=second_team, user=user, role=role)

    response = client.get("/api/v1.0/teams/")

    assert response.status_code == HTTP_200_OK
    assert response.json() == [
        {
            # I have the abilities only on the team I have a specific role
            "abilities": local_team_abilities,
            "accesses": [str(user_access.pk)],
            "created_at": second_team.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "depth": 3,
            "id": str(second_team.pk),
            "is_visible_all_services": False,
            "name": "Second",
            "numchild": 1,
            "path": second_team.path,
            "service_providers": [],
            "updated_at": second_team.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        },
    ]
