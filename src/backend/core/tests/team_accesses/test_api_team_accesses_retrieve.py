"""
Test for team accesses API endpoints in People's core app : retrieve
"""

import pytest
from rest_framework.test import APIClient

from core import factories

pytestmark = pytest.mark.django_db


def test_api_team_accesses_retrieve_anonymous():
    """
    Anonymous users should not be allowed to retrieve a team access.
    """
    access = factories.TeamAccessFactory()

    response = APIClient().get(
        f"/api/v1.0/teams/{access.team.id!s}/accesses/{access.id!s}/",
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_team_accesses_retrieve_authenticated_unrelated():
    """
    Authenticated users should not be allowed to retrieve a team access for
    a team to which they are not related.
    """
    user = factories.UserFactory()
    access = factories.TeamAccessFactory(team=factories.TeamFactory())

    client = APIClient()
    client.force_login(user)
    response = client.get(
        f"/api/v1.0/teams/{access.team.id!s}/accesses/{access.id!s}/",
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "No TeamAccess matches the given query."}

    # Accesses related to another team should be excluded even if the user is related to it
    for other_access in [
        factories.TeamAccessFactory(),
        factories.TeamAccessFactory(user=user),
    ]:
        response = client.get(
            f"/api/v1.0/teams/{access.team.id!s}/accesses/{other_access.id!s}/",
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "No TeamAccess matches the given query."}


def test_api_team_accesses_retrieve_authenticated_related():
    """
    A user who is related to a team should be allowed to retrieve the
    associated team user accesses.
    """
    user = factories.UserFactory()
    team = factories.TeamFactory()
    access = factories.TeamAccessFactory(team=team, user=user)

    client = APIClient()
    client.force_login(user)
    response = client.get(
        f"/api/v1.0/teams/{team.id!s}/accesses/{access.id!s}/",
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": str(access.id),
        "user": {
            "id": str(access.user.id),
            "email": str(user.email),
            "name": str(user.name),
        },
        "role": str(access.role),
        "abilities": access.get_abilities(user),
    }
