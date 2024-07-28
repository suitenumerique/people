"""
Test for the Resource Server (RS) clients classes.
"""

# pylint: disable=W0212

from unittest.mock import MagicMock, patch

import pytest
from joserfc.jwk import KeySet, RSAKey
from requests.exceptions import HTTPError

from core.resource_server.clients import AuthorizationServerClient


@pytest.fixture(name="client")
def fixture_client():
    """Generate an Authorization Server client."""
    return AuthorizationServerClient(
        url="https://auth.example.com/api/v2",
        url_jwks="https://auth.example.com/api/v2/jwks",
        url_introspection="https://auth.example.com/api/v2/introspect",
        verify_ssl=True,
        timeout=5,
        proxy=None,
    )


def test_authorization_server_client_initialization():
    """Test the AuthorizationServerClient initialization."""

    new_client = AuthorizationServerClient(
        url="https://auth.example.com/api/v2",
        url_jwks="https://auth.example.com/api/v2/jwks",
        url_introspection="https://auth.example.com/api/v2/checktoken/foo",
        verify_ssl=True,
        timeout=5,
        proxy=None,
    )

    assert new_client.url == "https://auth.example.com/api/v2"
    assert (
        new_client._url_introspection
        == "https://auth.example.com/api/v2/checktoken/foo"
    )
    assert new_client._url_jwks == "https://auth.example.com/api/v2/jwks"
    assert new_client._verify_ssl is True
    assert new_client._timeout == 5
    assert new_client._proxy is None


def test_introspection_headers(client):
    """Test the introspection headers to ensure they match the expected values."""
    assert client._introspection_headers == {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/token-introspection+jwt",
    }


@patch("requests.post")
def test_get_introspection_success(mock_post, client):
    """Test 'get_introspection' method with a successful response."""

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.text = "introspection response"
    mock_post.return_value = mock_response

    result = client.get_introspection("client_id", "client_secret", "token")
    assert result == "introspection response"

    mock_post.assert_called_once_with(
        "https://auth.example.com/api/v2/introspect",
        data={
            "client_id": "client_id",
            "client_secret": "client_secret",
            "token": "token",
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/token-introspection+jwt",
        },
        verify=True,
        timeout=5,
        proxies=None,
    )


@patch("requests.post", side_effect=HTTPError())
# pylint: disable=(unused-argument
def test_get_introspection_error(mock_post, client):
    """Test 'get_introspection' method with an HTTPError."""
    with pytest.raises(HTTPError):
        client.get_introspection("client_id", "client_secret", "token")


@patch("requests.get")
def test_get_jwks_success(mock_get, client):
    """Test 'get_jwks' method with a successful response."""

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"jwks": "foo"}
    mock_get.return_value = mock_response

    result = client.get_jwks()
    assert result == {"jwks": "foo"}

    mock_get.assert_called_once_with(
        "https://auth.example.com/api/v2/jwks",
        verify=client._verify_ssl,
        timeout=client._timeout,
        proxies=client._proxy,
    )


@patch("requests.get")
def test_get_jwks_error(mock_get, client):
    """Test 'get_jwks' method with an HTTPError."""

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = HTTPError(
        response=MagicMock(status=500)
    )
    mock_get.return_value = mock_response

    with pytest.raises(HTTPError):
        client.get_jwks()


@patch("requests.get")
def test_import_public_keys_valid(mock_get, client):
    """Test 'import_public_keys' method with a successful response."""

    mocked_key = RSAKey.generate_key(2048)

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"keys": [mocked_key.as_dict()]}
    mock_get.return_value = mock_response

    response = client.import_public_keys()

    assert isinstance(response, KeySet)
    assert response.as_dict() == KeySet([mocked_key]).as_dict()


@patch("requests.get")
def test_import_public_keys_http_error(mock_get, client):
    """Test 'import_public_keys' method with an HTTPError."""

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = HTTPError(
        response=MagicMock(status=500)
    )
    mock_get.return_value = mock_response

    with pytest.raises(HTTPError):
        client.import_public_keys()


@patch("requests.get")
def test_import_public_keys_empty_jwks(mock_get, client):
    """Test 'import_public_keys' method with empty keys response."""

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"keys": []}
    mock_get.return_value = mock_response

    response = client.import_public_keys()

    assert isinstance(response, KeySet)
    assert response.as_dict() == {"keys": []}


@patch("requests.get")
def test_import_public_keys_invalid_jwks(mock_get, client):
    """Test 'import_public_keys' method with invalid keys response."""

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"keys": [{"foo": "foo"}]}
    mock_get.return_value = mock_response

    with pytest.raises(ValueError):
        client.import_public_keys()
