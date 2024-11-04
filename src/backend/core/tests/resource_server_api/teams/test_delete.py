"""
Tests for Teams API endpoint in People's core app: delete
"""

import pytest
from rest_framework.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_405_METHOD_NOT_ALLOWED,
)
from rest_framework.test import APIClient

from core import factories, models

pytestmark = pytest.mark.django_db


def test_api_teams_delete_anonymous():
    """Anonymous users should not be allowed to destroy a team."""
    team = factories.TeamFactory()

    response = APIClient().delete(
        f"/resource-server/v1.0/teams/{team.id!s}/",
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert models.Team.objects.count() == 1


def test_api_teams_delete_not_allowed(client, force_login_via_resource_server):
    """
    Authenticated users should not be allowed to delete a team from a resource
    server, even if they have the right permissions.

    This may be implemented in the future, but for now, it is not allowed.
    """
    user = factories.UserFactory()
    service_provider = factories.ServiceProviderFactory()
    team = factories.TeamFactory(
        users=[(user, "owner")], service_providers=[service_provider]
    )

    with force_login_via_resource_server(client, user, service_provider.audience_id):
        response = client.delete(
            f"/resource-server/v1.0/teams/{team.id!s}/",
        )

    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
    assert response.json() == {"detail": 'Method "DELETE" not allowed.'}
    assert models.Team.objects.count() == 1
