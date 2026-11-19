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
        with django_assert_num_queries(1):
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
