"""
Tests for the SCIM Me API endpoint in People's core app
"""

import pytest
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_405_METHOD_NOT_ALLOWED,
)

from core import factories
from core.models import RoleChoices

pytestmark = pytest.mark.django_db


def test_api_me_anonymous(client):
    """Anonymous users should not be allowed to access the Me endpoint."""
    response = client.get("/resource-server/v1.0/scim/Me/")

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.headers["Content-Type"] == "application/json+scim"

    # Check the full response with the expected structure
    assert response.json() == {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
        "status": "401",
        "detail": "",
    }


def test_api_me_authenticated(
    client, force_login_via_resource_server, django_assert_num_queries
):
    """
    Authenticated users should be able to access their own information
    in SCIM format.
    """
    user = factories.UserFactory(name="Test User", email="test@example.com")
    service_provider = factories.ServiceProviderFactory()

    # Authenticate using the resource server, ie via the Authorization header
    with force_login_via_resource_server(client, user, service_provider.audience_id):
        with django_assert_num_queries(2):
            response = client.get(
                "/resource-server/v1.0/scim/Me/",
                format="json",
                HTTP_AUTHORIZATION="Bearer b64untestedbearertoken",
            )

    assert response.status_code == HTTP_200_OK
    assert response.headers["Content-Type"] == "application/json+scim"

    # Check the full response with the expected structure
    assert response.json() == {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "id": str(user.pk),
        "active": True,
        "userName": user.sub,
        "displayName": user.name,
        "emails": [
            {
                "value": user.email,
                "primary": True,
                "type": "work",
            }
        ],
        "groups": [],
        "meta": {
            "resourceType": "User",
            "created": user.created_at.isoformat(),
            "lastModified": user.updated_at.isoformat(),
            "location": "http://testserver/resource-server/v1.0/scim/Me/",
        },
    }


def test_api_me_authenticated_with_team_access(
    client, force_login_via_resource_server, django_assert_num_queries
):
    """
    Authenticated users with TeamAccess should see their team information
    in SCIM format, but only for teams visible to the service provider.
    """
    user = factories.UserFactory(name="Test User", email="test@example.com")
    service_provider = factories.ServiceProviderFactory()

    # Create teams with different visibility settings
    team_visible = factories.TeamFactory(name="Visible Team")
    team_visible.service_providers.add(service_provider)

    team_all_services = factories.TeamFactory(
        name="All Services Team", is_visible_all_services=True
    )

    team_not_visible = factories.TeamFactory(name="Not Visible Team")
    # This team is not associated with the service provider

    # Add user to all teams
    factories.TeamAccessFactory(user=user, team=team_visible, role=RoleChoices.MEMBER)
    factories.TeamAccessFactory(
        user=user, team=team_all_services, role=RoleChoices.ADMIN
    )
    factories.TeamAccessFactory(
        user=user, team=team_not_visible, role=RoleChoices.OWNER
    )

    # Authenticate using the resource server, ie via the Authorization header
    with force_login_via_resource_server(client, user, service_provider.audience_id):
        with django_assert_num_queries(
            2
        ):  # User + TeamAccess (with select_related teams)
            response = client.get(
                "/resource-server/v1.0/scim/Me/",
                format="json",
                HTTP_AUTHORIZATION="Bearer b64untestedbearertoken",
            )

    assert response.status_code == HTTP_200_OK
    assert response.headers["Content-Type"] == "application/json+scim"
    # Check the full response with the expected structure
    assert response.json() == {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "id": str(user.pk),
        "active": True,
        "userName": user.sub,
        "displayName": user.name,
        "emails": [
            {
                "value": user.email,
                "primary": True,
                "type": "work",
            }
        ],
        "groups": [
            {
                "value": str(team_visible.external_id),
                "display": team_visible.name,
                "type": "direct",
            },
            {
                "value": str(team_all_services.external_id),
                "display": team_all_services.name,
                "type": "direct",
            },
        ],
        "meta": {
            "resourceType": "User",
            "created": user.created_at.isoformat(),
            "lastModified": user.updated_at.isoformat(),
            "location": "http://testserver/resource-server/v1.0/scim/Me/",
        },
    }


@pytest.mark.parametrize(
    "http_method",
    ["post", "put", "patch", "delete"],
    ids=["POST", "PUT", "PATCH", "DELETE"],
)
def test_api_me_method_not_allowed(
    client, force_login_via_resource_server, http_method
):
    """Test that methods other than GET are not allowed for the Me endpoint."""
    user = factories.UserFactory()
    service_provider = factories.ServiceProviderFactory()

    # Authenticate using the resource server, ie via the Authorization header
    with force_login_via_resource_server(client, user, service_provider.audience_id):
        client_method = getattr(client, http_method)
        response = client_method(
            "/resource-server/v1.0/scim/Me/",
            format="json",
            HTTP_AUTHORIZATION="Bearer b64untestedbearertoken",
        )

    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
    assert response.headers["Content-Type"] == "application/json+scim"

    # Check the full response with the expected structure
    assert response.json() == {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
        "status": str(HTTP_405_METHOD_NOT_ALLOWED),
        "detail": "",
    }
