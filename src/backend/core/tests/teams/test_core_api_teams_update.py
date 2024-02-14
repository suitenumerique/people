"""
Tests for Teams API endpoint in People's core app: update
"""
import random

import pytest
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)
from rest_framework.test import APIClient

from core import factories
from core.api import serializers

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
    identity = factories.IdentityFactory()

    client = APIClient()
    client.force_login(identity.user)

    team = factories.TeamFactory()
    old_team_values = serializers.TeamSerializer(instance=team).data

    new_team_values = serializers.TeamSerializer(instance=factories.TeamFactory()).data
    response = client.put(
        f"/api/v1.0/teams/{team.id!s}/",
        new_team_values,
        format="json",
    )

    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Not found."}

    team.refresh_from_db()
    team_values = serializers.TeamSerializer(instance=team).data
    assert team_values == old_team_values


def test_api_teams_update_authenticated_members():
    """
    Users who are members of a team but not administrators should
    not be allowed to update it.
    """
    identity = factories.IdentityFactory()
    user = identity.user

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
    identity = factories.IdentityFactory()
    user = identity.user

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
        if key in ["id", "accesses"]:  # pylint: disable=R1733
            assert value == initial_values[key]
        else:
            # name, slug and abilities successfully modified
            assert value == new_values[key]


def test_api_teams_update_authenticated_owners():
    """Administrators of a team should be allowed to update it,
    apart from read-only fields."""
    identity = factories.IdentityFactory()
    user = identity.user

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
        if key in ["id", "accesses"]:
            assert value == old_team_values[key]
        else:
            # name, slug and abilities successfully modified
            assert value == new_team_values[key]


def test_api_teams_update_administrator_or_owner_of_another():
    """
    Being administrator or owner of a team should not grant authorization to update
    another team.
    """
    identity = factories.IdentityFactory()
    user = identity.user

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
    assert response.json() == {"detail": "Not found."}

    team.refresh_from_db()
    team_values = serializers.TeamSerializer(instance=team).data
    assert team_values == old_team_values


def test_api_teams_update_existing_slug_should_return_error():
    """
    Updating a team's name to an existing slug should return a bad request,
    instead of creating a duplicate.
    """
    identity = factories.IdentityFactory()
    user = identity.user

    client = APIClient()
    client.force_login(user)

    factories.TeamFactory(name="Existing team", users=[(user, "administrator")])
    my_team = factories.TeamFactory(name="New team", users=[(user, "administrator")])

    updated_values = serializers.TeamSerializer(instance=my_team).data
    # Update my team's name for existing team. Creates a duplicate slug
    updated_values["name"] = "existing team"
    response = client.put(
        f"/api/v1.0/teams/{my_team.id!s}/",
        updated_values,
        format="json",
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["slug"] == ["Team with this Slug already exists."]
    # Both teams names and slugs should be unchanged
    assert my_team.name == "New team"
    assert my_team.slug == "new-team"
