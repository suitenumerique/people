"""Tests for the authentication process of the resource server."""

import base64
import json

import pytest
import responses
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from joserfc import jwe as jose_jwe
from joserfc import jwt as jose_jwt
from joserfc.rfc7518.rsa_key import RSAKey
from jwt.utils import to_base64url_uint
from lasuite.oidc_resource_server.authentication import (
    ResourceServerAuthentication,
    get_resource_server_backend,
)
from rest_framework.request import Request as DRFRequest
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED

from core.factories import UserFactory
from core.models import ServiceProvider

pytestmark = pytest.mark.django_db


@pytest.fixture(name="jwt_resource_server_backend")
def jwt_resource_server_backend_fixture(settings):
    """Fixture to switch the backend to the JWTResourceServerBackend."""
    _original_backend = str(settings.OIDC_RS_BACKEND_CLASS)

    settings.OIDC_RS_BACKEND_CLASS = (
        "lasuite.oidc_resource_server.backend.JWTResourceServerBackend"
    )
    get_resource_server_backend.cache_clear()

    yield

    settings.OIDC_RS_BACKEND_CLASS = _original_backend
    get_resource_server_backend.cache_clear()


def build_authorization_bearer(token):
    """
    Build an Authorization Bearer header value from a token.

    This can be used like this:
    client.post(
        ...
        HTTP_AUTHORIZATION=f"Bearer {build_authorization_bearer('some_token')}",
    )
    """
    return base64.b64encode(token.encode("utf-8")).decode("utf-8")


@responses.activate
def test_resource_server_authentication_class(client, settings):
    """
    Defines the settings for the resource server
    for a full authentication with introspection process.

    This is an integration test that checks the authentication process
    when using the ResourceServerAuthentication class.

    This test asserts the DRF request object contains the
    `resource_server_token_audience` attribute which is used in
    the resource server views.

    This test uses the `/resource-server/v1.0/teams/` URL as an example
    because we don't want to create a new URL just for this test.
    """
    assert (
        settings.OIDC_RS_BACKEND_CLASS
        == "lasuite.oidc_resource_server.backend.ResourceServerBackend"
    )

    settings.OIDC_RS_CLIENT_ID = "some_client_id"
    settings.OIDC_RS_CLIENT_SECRET = "some_client_secret"

    settings.OIDC_OP_URL = "https://oidc.example.com"
    settings.OIDC_VERIFY_SSL = False
    settings.OIDC_TIMEOUT = 5
    settings.OIDC_PROXY = None
    settings.OIDC_OP_JWKS_ENDPOINT = "https://oidc.example.com/jwks"
    settings.OIDC_OP_INTROSPECTION_ENDPOINT = "https://oidc.example.com/introspect"

    responses.add(
        responses.POST,
        "https://oidc.example.com/introspect",
        json={
            "iss": "https://oidc.example.com",
            "aud": "some_client_id",  # settings.OIDC_RS_CLIENT_ID
            "sub": "very-specific-sub",
            "client_id": "some_service_provider",
            "scope": "openid groups",
            "active": True,
        },
    )

    # Try to authenticate while the user does not exist => 401
    response = client.get(
        "/resource-server/v1.0/teams/",  # use an exising URL here
        format="json",
        HTTP_AUTHORIZATION=f"Bearer {build_authorization_bearer('some_token')}",
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert ServiceProvider.objects.count() == 0

    # Create a user with the specific sub, the access is authorized
    UserFactory(sub="very-specific-sub")

    response = client.get(
        "/resource-server/v1.0/teams/",  # use an exising URL here
        format="json",
        HTTP_AUTHORIZATION=f"Bearer {build_authorization_bearer('some_token')}",
    )

    assert response.status_code == HTTP_200_OK

    response_request = response.renderer_context.get("request")
    assert isinstance(response_request, DRFRequest)
    assert isinstance(
        response_request.successful_authenticator, ResourceServerAuthentication
    )

    # Check that the user is authenticated
    assert response_request.user.is_authenticated

    # Check the request contains the resource server token audience
    assert response_request.resource_server_token_audience == "some_service_provider"

    # Check that no service provider is created here
    assert ServiceProvider.objects.count() == 0


@responses.activate
def test_jwt_resource_server_authentication_class(  # pylint: disable=unused-argument
    client, jwt_resource_server_backend, settings
):
    """
    Defines the settings for the resource server
    for a full authentication with introspection process.

    This is an integration test that checks the authentication process
    when using the ResourceServerAuthentication class.

    This test asserts the DRF request object contains the
    `resource_server_token_audience` attribute which is used in
    the resource server views.

    This test uses the `/resource-server/v1.0/teams/` URL as an example
    because we don't want to create a new URL just for this test.
    """
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    unencrypted_pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    pem_public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    settings.OIDC_RS_PRIVATE_KEY_STR = unencrypted_pem_private_key.decode("utf-8")
    settings.OIDC_RS_ENCRYPTION_KEY_TYPE = "RSA"
    settings.OIDC_RS_ENCRYPTION_ENCODING = "A256GCM"
    settings.OIDC_RS_ENCRYPTION_ALGO = "RSA-OAEP"
    settings.OIDC_RS_SIGNING_ALGO = "RS256"
    settings.OIDC_RS_CLIENT_ID = "some_client_id"
    settings.OIDC_RS_CLIENT_SECRET = "some_client_secret"

    settings.OIDC_OP_URL = "https://oidc.example.com"
    settings.OIDC_VERIFY_SSL = False
    settings.OIDC_TIMEOUT = 5
    settings.OIDC_PROXY = None
    settings.OIDC_OP_JWKS_ENDPOINT = "https://oidc.example.com/jwks"
    settings.OIDC_OP_INTROSPECTION_ENDPOINT = "https://oidc.example.com/introspect"

    # Mock the JWKS endpoint
    public_numbers = private_key.public_key().public_numbers()
    responses.add(
        responses.GET,
        settings.OIDC_OP_JWKS_ENDPOINT,
        body=json.dumps(
            {
                "keys": [
                    {
                        "kty": settings.OIDC_RS_ENCRYPTION_KEY_TYPE,
                        "alg": settings.OIDC_RS_SIGNING_ALGO,
                        "use": "sig",
                        "kid": "1234567890",
                        "n": to_base64url_uint(public_numbers.n).decode("ascii"),
                        "e": to_base64url_uint(public_numbers.e).decode("ascii"),
                    }
                ]
            }
        ),
    )

    def encrypt_jwt(json_data):
        """Encrypt the JWT token for the backend to decrypt."""
        token = jose_jwt.encode(
            {
                "kid": "1234567890",
                "alg": settings.OIDC_RS_SIGNING_ALGO,
            },
            json_data,
            RSAKey.import_key(unencrypted_pem_private_key),
            algorithms=[settings.OIDC_RS_SIGNING_ALGO],
        )

        return jose_jwe.encrypt_compact(
            protected={
                "alg": settings.OIDC_RS_ENCRYPTION_ALGO,
                "enc": settings.OIDC_RS_ENCRYPTION_ENCODING,
            },
            plaintext=token,
            public_key=RSAKey.import_key(pem_public_key),
            algorithms=[
                settings.OIDC_RS_ENCRYPTION_ALGO,
                settings.OIDC_RS_ENCRYPTION_ENCODING,
            ],
        )

    responses.add(
        responses.POST,
        "https://oidc.example.com/introspect",
        body=encrypt_jwt(
            {
                "iss": "https://oidc.example.com",
                "aud": "some_client_id",  # settings.OIDC_RS_CLIENT_ID
                "token_introspection": {
                    "sub": "very-specific-sub",
                    "iss": "https://oidc.example.com",
                    "aud": "some_client_id",
                    "client_id": "some_service_provider",
                    "scope": "openid groups",
                    "active": True,
                },
            }
        ),
    )

    # Try to authenticate while the user does not exist => 401
    response = client.get(
        "/resource-server/v1.0/teams/",  # use an exising URL here
        format="json",
        HTTP_AUTHORIZATION=f"Bearer {build_authorization_bearer('some_token')}",
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert ServiceProvider.objects.count() == 0

    # Create a user with the specific sub, the access is authorized
    UserFactory(sub="very-specific-sub")

    response = client.get(
        "/resource-server/v1.0/teams/",  # use an exising URL here
        format="json",
        HTTP_AUTHORIZATION=f"Bearer {build_authorization_bearer('some_token')}",
    )

    assert response.status_code == HTTP_200_OK

    response_request = response.renderer_context.get("request")
    assert isinstance(response_request, DRFRequest)
    assert isinstance(
        response_request.successful_authenticator, ResourceServerAuthentication
    )

    # Check that the user is authenticated
    assert response_request.user.is_authenticated

    # Check the request contains the resource server token audience
    assert response_request.resource_server_token_audience == "some_service_provider"

    # Check that no service provider is created here
    assert ServiceProvider.objects.count() == 0
