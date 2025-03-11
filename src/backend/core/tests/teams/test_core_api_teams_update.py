"""
Tests for Teams API endpoint in People's core app: update
"""

import random

import pytest
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)
from rest_framework.test import APIClient

from core import factories
from core.api.client import serializers

pytestmark = pytest.mark.django_db


def test_api_teams_update_anonymous():
    """Anonymous users should not be allowed to update a team."""
    team = factories.TeamFactory()
    old_team_values = serializers.TeamSerializer(instance=team).data

    new_team_values = serializers.TeamSerializer(instance=factories.TeamFactory()).data
    response = APIClient().put(
        f"/api/v1.0/teams/{team.id!s}/",
        new_team_values,
        format="json",
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }

    team.refresh_from_db()
    team_values = serializers.TeamSerializer(instance=team).data
    assert team_values == old_team_values


def test_api_teams_update_authenticated_unrelated():
    """
    Authenticated users should not be allowed to update a team to which they are not related.
    """
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    team = factories.TeamFactory()
    old_team_values = serializers.TeamSerializer(instance=team).data

    new_team_values = serializers.TeamSerializer(instance=factories.TeamFactory()).data
    response = client.put(
        f"/api/v1.0/teams/{team.id!s}/",
        new_team_values,
        format="json",
    )

    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No Team matches the given query."}

    team.refresh_from_db()
    team_values = serializers.TeamSerializer(instance=team).data
    assert team_values == old_team_values


def test_api_teams_update_authenticated_members():
    """
    Users who are members of a team but not administrators should
    not be allowed to update it.
    """
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    team = factories.TeamFactory(users=[(user, "member")])
    old_team_values = serializers.TeamSerializer(instance=team).data

    new_team_values = serializers.TeamSerializer(instance=factories.TeamFactory()).data
    response = client.put(
        f"/api/v1.0/teams/{team.id!s}/",
        new_team_values,
        format="json",
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "You do not have permission to perform this action."
    }

    team.refresh_from_db()
    team_values = serializers.TeamSerializer(instance=team).data
    assert team_values == old_team_values


def test_api_teams_update_authenticated_administrators():
    """Administrators of a team should be allowed to update it."""
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    team = factories.TeamFactory(users=[(user, "administrator")])
    initial_values = serializers.TeamSerializer(instance=team).data

    # generate new random values
    new_values = serializers.TeamSerializer(instance=factories.TeamFactory.build()).data
    response = client.put(
        f"/api/v1.0/teams/{team.id!s}/",
        new_values,
        format="json",
    )
    assert response.status_code == HTTP_200_OK

    team.refresh_from_db()
    final_values = serializers.TeamSerializer(instance=team).data
    for key, value in final_values.items():
        if key in ["id", "accesses", "created_at", "depth", "path", "numchild"]:
            assert value == initial_values[key]
        elif key == "updated_at":
            assert value > initial_values[key]
        else:
            # name and abilities successfully modified
            assert value == new_values[key]


def test_api_teams_update_is_visible_all_services():
    """Administrators of a team should be allowed to update the visibility to all services."""
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    team = factories.TeamFactory(
        users=[(user, "administrator")], is_visible_all_services=False
    )

    response = client.patch(
        f"/api/v1.0/teams/{team.id!s}/",
        {"is_visible_all_services": True},
        format="json",
    )
    assert response.status_code == HTTP_200_OK
    team.refresh_from_db()
    assert team.is_visible_all_services is True


def test_api_teams_update_authenticated_owners():
    """Administrators of a team should be allowed to update it,
    apart from read-only fields."""
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    team = factories.TeamFactory(users=[(user, "owner")])
    old_team_values = serializers.TeamSerializer(instance=team).data

    new_team_values = serializers.TeamSerializer(
        instance=factories.TeamFactory.build()
    ).data
    response = client.put(
        f"/api/v1.0/teams/{team.id!s}/",
        new_team_values,
        format="json",
    )
    assert response.status_code == HTTP_200_OK

    team.refresh_from_db()
    team_values = serializers.TeamSerializer(instance=team).data
    for key, value in team_values.items():
        if key in ["id", "accesses", "created_at", "depth", "path", "numchild"]:
            assert value == old_team_values[key]
        elif key == "updated_at":
            assert value > old_team_values[key]
        else:
            # name and abilities successfully modified
            assert value == new_team_values[key]


def test_api_teams_update_administrator_or_owner_of_another():
    """
    Being administrator or owner of a team should not grant authorization to update
    another team.
    """
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    factories.TeamFactory(users=[(user, random.choice(["administrator", "owner"]))])
    team = factories.TeamFactory(name="Old name")
    old_team_values = serializers.TeamSerializer(instance=team).data

    new_team_values = serializers.TeamSerializer(instance=factories.TeamFactory()).data
    response = client.put(
        f"/api/v1.0/teams/{team.id!s}/",
        new_team_values,
        format="json",
    )

    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No Team matches the given query."}

    team.refresh_from_db()
    team_values = serializers.TeamSerializer(instance=team).data
    assert team_values == old_team_values


def test_api_teams_update_authenticated_owners_add_service_providers():
    """
    Owners of a team should be allowed to update its service providers.
    """
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    team = factories.TeamFactory(users=[(user, "owner")])
    new_team_values = serializers.TeamSerializer(instance=team).data

    service_provider_1 = factories.ServiceProviderFactory()
    service_provider_2 = factories.ServiceProviderFactory()
    new_team_values["service_providers"] = [
        service_provider_1.pk,
        service_provider_2.pk,
    ]

    response = client.put(
        f"/api/v1.0/teams/{team.id!s}/",
        new_team_values,
        format="json",
    )
    assert response.status_code == HTTP_200_OK

    team.refresh_from_db()
    assert team.service_providers.count() == 2
    assert set(team.service_providers.all()) == {service_provider_1, service_provider_2}


@pytest.mark.parametrize(
    "role",
    ["owner", "administrator", "member"],
)
def test_api_teams_update_whatever_access_of_child_team(client, role):
    """
    Being member, administrator or owner of a team should not grant
    authorization to update a parent team.
    """
    user = factories.UserFactory()

    client.force_login(user)

    root_team = factories.TeamFactory(name="Root")
    first_team = factories.TeamFactory(name="First", parent_id=root_team.pk)
    second_team = factories.TeamFactory(name="Second", parent_id=first_team.pk)

    # user is a member of the second team
    factories.TeamAccessFactory(team=second_team, user=user, role=role)

    response = client.patch(
        f"/api/v1.0/teams/{first_team.pk}/",
        {
            "name": "New name",
        },
        format="json",
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "You do not have permission to perform this action."
    }

    first_team.refresh_from_db()
    assert first_team.name == "First"


@pytest.mark.parametrize(
    "role",
    ["owner", "administrator", "member"],
)
def test_api_teams_update_whatever_access_of_parent_team(client, role):
    """
    Being member, administrator or owner of a team should not grant
    authorization to update a child team.
    """
    user = factories.UserFactory()

    client.force_login(user)

    root_team = factories.TeamFactory(name="Root")
    first_team = factories.TeamFactory(name="First", parent_id=root_team.pk)
    second_team = factories.TeamFactory(name="Second", parent_id=first_team.pk)

    # user is a member of the first team
    factories.TeamAccessFactory(team=first_team, user=user, role=role)

    response = client.patch(
        f"/api/v1.0/teams/{second_team.pk}/",
        {
            "name": "New name",
        },
        format="json",
    )

    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No Team matches the given query."}

    second_team.refresh_from_db()
    assert second_team.name == "Second"
