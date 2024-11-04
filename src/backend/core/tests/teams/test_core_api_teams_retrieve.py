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
        "id": str(team.id),
        "name": team.name,
        "abilities": team.get_abilities(user),
        "created_at": team.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": team.updated_at.isoformat().replace("+00:00", "Z"),
        "service_providers": [],
    }
