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

    response = APIClient().get("/resource-server/v1.0/teams/")

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_teams_list_authenticated(  # pylint: disable=too-many-locals
    client, django_assert_num_queries, force_login_via_resource_server
):
    """
    Authenticated users should be able to list teams
    they are an owner/administrator/member of, and only list from the
    requesting service provider should appear.
    """
    user = factories.UserFactory()
    service_provider = factories.ServiceProviderFactory()
    hidden_service_provider = factories.ServiceProviderFactory()

    team_access_1 = factories.TeamAccessFactory(
        user=user, team__service_providers=[service_provider], role="member"
    )
    team_1 = team_access_1.team

    team_access_2 = factories.TeamAccessFactory(
        user=user,
        team__service_providers=[hidden_service_provider, service_provider],
        role="member",
    )
    team_2 = team_access_2.team

    team_access_3 = factories.TeamAccessFactory(
        user=user, team__service_providers=[service_provider], role="administrator"
    )
    team_3 = team_access_3.team

    team_access_4 = factories.TeamAccessFactory(
        user=user, team__service_providers=[service_provider], role="owner"
    )
    team_4 = team_access_4.team

    # Team filtered out because of the service provider
    _not_included_team_access = factories.TeamAccessFactory(
        user=user, team__service_providers=[hidden_service_provider]
    )

    # Authenticate using the resource server, ie via the Authorization header
    with force_login_via_resource_server(client, user, service_provider.audience_id):
        with django_assert_num_queries(5):
            # queries: Team path, Count, Team, ServiceProvider, TeamAccess
            response = client.get(
                "/resource-server/v1.0/teams/?ordering=created_at",
                format="json",
                HTTP_AUTHORIZATION="Bearer b64untestedbearertoken",
            )

    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "count": 4,
        "next": None,
        "previous": None,
        "results": [
            {
                "created_at": team_1.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "depth": team_1.depth,
                "id": str(team_1.pk),
                "is_visible_all_services": False,
                "name": team_1.name,
                "numchild": team_1.numchild,
                "path": team_1.path,
                "updated_at": team_1.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            },
            {
                "created_at": team_2.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "depth": team_2.depth,
                "id": str(team_2.pk),
                "is_visible_all_services": False,
                "name": team_2.name,
                "numchild": team_2.numchild,
                "path": team_2.path,
                "updated_at": team_2.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            },
            {
                "created_at": team_3.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "depth": team_3.depth,
                "id": str(team_3.pk),
                "is_visible_all_services": False,
                "name": team_3.name,
                "numchild": team_3.numchild,
                "path": team_3.path,
                "updated_at": team_3.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            },
            {
                "created_at": team_4.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "depth": team_4.depth,
                "id": str(team_4.pk),
                "is_visible_all_services": False,
                "name": team_4.name,
                "numchild": team_4.numchild,
                "path": team_4.path,
                "updated_at": team_4.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            },
        ],
    }


def test_api_teams_list_authenticated_new_service_provider(
    client, force_login_via_resource_server
):
    """
    Team list from not yet known service provider should be empty (not fail).

    Teams without service providers should not be listed.
    """
    user = factories.UserFactory()
    _team = factories.TeamFactory(users=[user])

    with force_login_via_resource_server(client, user, "some_service_provider"):
        response = client.get(
            "/resource-server/v1.0/teams/",
        )

    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "count": 0,
        "next": None,
        "previous": None,
        "results": [],
    }


def test_api_teams_list_authenticated_distinct(client, force_login_via_resource_server):
    """A team with several related users should only be listed once."""
    user = factories.UserFactory()
    service_provider = factories.ServiceProviderFactory()

    other_user = factories.UserFactory()

    team = factories.TeamFactory(
        users=[user, other_user], service_providers=[service_provider]
    )

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.get(
            "/resource-server/v1.0/teams/",
        )

    assert response.status_code == HTTP_200_OK
    content = response.json()
    assert content["count"] == 1

    results = content["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(team.id)


def test_api_teams_order_param(client, force_login_via_resource_server):
    """
    Test that the 'created_at' field is sorted in ascending order
    when the 'ordering' query parameter is set.
    """
    user = factories.UserFactory()
    service_provider = factories.ServiceProviderFactory()

    team_ids = [
        str(team.id)
        for team in factories.TeamFactory.create_batch(
            5, users=[user], service_providers=[service_provider]
        )
    ]

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.get(
            "/resource-server/v1.0/teams/?ordering=created_at",
        )
    assert response.status_code == 200

    response_data = response.json()
    response_team_ids = [team["id"] for team in response_data["results"]]

    assert response_team_ids == team_ids, (
        "created_at values are not sorted from oldest to newest"
    )


def test_api_teams_list_with_parent_teams(client, force_login_via_resource_server):
    """
    Authenticated users should be able to list teams including parent teams.
    Parent teams should not be listed if they don't have the service provider.
    """
    user = factories.UserFactory()
    service_provider = factories.ServiceProviderFactory()

    root_team = factories.TeamFactory(name="Root", service_providers=[service_provider])
    first_team = factories.TeamFactory(name="First", parent_id=root_team.pk)
    second_team = factories.TeamFactory(
        name="Second", parent_id=first_team.pk, service_providers=[service_provider]
    )

    factories.TeamAccessFactory(user=user, team=second_team, role="member")

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.get(
            "/resource-server/v1.0/teams/",
            format="json",
            HTTP_AUTHORIZATION="Bearer b64untestedbearertoken",
        )

    assert response.status_code == HTTP_200_OK
    response_data = response.json()
    assert response_data["count"] == 2

    team_ids = [team["id"] for team in response_data["results"]]
    assert len(team_ids) == 2
    assert set(team_ids) == {str(root_team.id), str(second_team.id)}


def test_api_teams_list_with_parent_teams_other_organization(
    client, force_login_via_resource_server
):
    """
    Authenticated users should be able to list teams including parent teams.
    Parent teams should not be listed if they don't have the service provider
    or if the user does not belong to the organization.
    """
    organization = factories.OrganizationFactory(with_registration_id=True)
    user = factories.UserFactory(organization=organization)
    service_provider = factories.ServiceProviderFactory()

    other_organization = factories.OrganizationFactory(with_registration_id=True)
    root_team = factories.TeamFactory(
        name="Root",
        service_providers=[service_provider],
        organization=other_organization,
    )
    first_team = factories.TeamFactory(
        name="First", parent_id=root_team.pk, organization=other_organization
    )
    second_team = factories.TeamFactory(
        name="Second",
        parent_id=first_team.pk,
        service_providers=[service_provider],
        organization=other_organization,
    )

    factories.TeamAccessFactory(user=user, team=second_team, role="member")

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.get(
            "/resource-server/v1.0/teams/",
            format="json",
            HTTP_AUTHORIZATION="Bearer b64untestedbearertoken",
        )

    assert response.status_code == HTTP_200_OK
    response_data = response.json()
    assert response_data["count"] == 1

    team_ids = [team["id"] for team in response_data["results"]]
    assert len(team_ids) == 1
    assert set(team_ids) == {str(second_team.id)}


def test_api_teams_list_is_visible_all_services_teams(
    client, force_login_via_resource_server
):
    """
    Authenticated users should be able to see teams
    if they are associated with another requesting service provider.
    """
    user = factories.UserFactory()
    service_provider = factories.ServiceProviderFactory()
    other_service_provider = factories.ServiceProviderFactory()

    # Create a public team visible to the requesting service provider
    service_team = factories.TeamFactory(
        is_visible_all_services=False,
        service_providers=[service_provider],
    )
    factories.TeamAccessFactory(user=user, team=service_team, role="member")

    # Create a public team visible to another service provider (should be listed)
    other_public_team = factories.TeamFactory(
        is_visible_all_services=True,
        service_providers=[other_service_provider],
    )
    factories.TeamAccessFactory(user=user, team=other_public_team, role="member")

    # Create a public team visible to the requesting service provider (should not be listed)
    private_team = factories.TeamFactory(
        is_visible_all_services=False,
        service_providers=[other_service_provider],
    )
    factories.TeamAccessFactory(user=user, team=private_team, role="member")

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.get("/resource-server/v1.0/teams/")

    assert response.status_code == HTTP_200_OK
    response_data = response.json()
    assert response_data["count"] == 2

    team_ids = [team["id"] for team in response_data["results"]]
    assert len(team_ids) == 2
    assert str(service_team.id) in team_ids
    assert str(other_public_team.id) in team_ids
