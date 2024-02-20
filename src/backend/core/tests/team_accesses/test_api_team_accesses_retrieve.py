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
    identity = factories.IdentityFactory()
    user = identity.user

    team = factories.TeamFactory()
    access = factories.TeamAccessFactory(team=team)

    client = APIClient()
    client.force_login(user)
    response = client.get(
        f"/api/v1.0/teams/{team.id!s}/accesses/{access.id!s}/",
    )
    assert response.status_code == 403
    assert response.json() == {
        "detail": "You do not have permission to perform this action."
    }

    # Accesses related to another team should be excluded even if the user is related to it
    for access in [
        factories.TeamAccessFactory(),
        factories.TeamAccessFactory(user=user),
    ]:
        response = client.get(
            f"/api/v1.0/teams/{team.id!s}/accesses/{access.id!s}/",
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "Not found."}


def test_api_team_accesses_retrieve_authenticated_related():
    """
    A user who is related to a team should be allowed to retrieve the
    associated team user accesses.
    """
    identity = factories.IdentityFactory()
    user = identity.user

    team = factories.TeamFactory(users=[user])
    access = factories.TeamAccessFactory(team=team)

    client = APIClient()
    client.force_login(user)
    response = client.get(
        f"/api/v1.0/teams/{team.id!s}/accesses/{access.id!s}/",
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": str(access.id),
        "user": str(access.user.id),
        "role": access.role,
        "abilities": access.get_abilities(user),
    }
