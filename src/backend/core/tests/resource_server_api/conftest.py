"""Defines fixtures for the resource server API tests."""

from contextlib import contextmanager
from typing import Optional
from unittest import mock

from django.contrib.auth import get_user_model

import pytest
import responses
from faker import Faker
from lasuite.oidc_resource_server.authentication import ResourceServerAuthentication

User = get_user_model()
fake = Faker()


@contextmanager
def _force_login_via_resource_server(
    client_fixture,
    user: User,
    service_provider_audience: Optional[str],
):
    """
    Context manager to authenticate a user with a service provider via
    a resource server call.

    This allows to authenticate a user with a service provider without doing
    all the introspection process.

    This is a private function, use the `force_login_via_resource_server`
    fixture instead.

    The `service_provider_audience` parameter might not match any existing
    service provider audience, doing so allow to check the behavior when
    the service provider is not yet known.
    """

    def mock_authenticate(self, request):  # pylint: disable=unused-argument
        request.resource_server_token_audience = (
            service_provider_audience or fake.pystr(min_chars=10, max_chars=10)
        )
        return user, "unused-token"

    with mock.patch.object(
        ResourceServerAuthentication, "authenticate", mock_authenticate
    ):
        client_fixture.force_login(
            user,
            backend="lasuite.oidc_resource_server.authentication.ResourceServerAuthentication",
        )
        yield


@pytest.fixture(name="force_login_via_resource_server")
@responses.activate
def force_login_via_resource_server_fixture():
    """
    Fixture to authenticate a user with a service provider via a resource server call.

    Usage:
    ```
    def test_login_with_resource_server(
        client, force_login_via_resource_server,
    ):
        user = UserFactory()
        service_provider = ServiceProviderFactory()
        with force_login_via_resource_server(client, user, service_provider.audience_id):
            response = client.get(
                "/resource-server/v1.0/<whatever>/",
                format="json",
                HTTP_AUTHORIZATION="Bearer b64untestedbearertoken",
            )

            # response is authenticated
    ```
    """
    return _force_login_via_resource_server
