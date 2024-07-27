"""
Tests for the Resource Server (RS) Views.
"""

from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse

import pytest
from joserfc.jwk import RSAKey
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@mock.patch("core.resource_server.utils.import_private_key_from_settings")
def test_view_jwks_valid_public_key(mock_import_private_key_from_settings):
    """JWKs endpoint should return a set of valid Json Web Key"""

    mocked_key = RSAKey.generate_key(2048)
    mock_import_private_key_from_settings.return_value = mocked_key

    url = reverse("resource_server_jwks")
    response = APIClient().get(url)

    mock_import_private_key_from_settings.assert_called_once()

    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"

    jwks = response.json()
    assert jwks == {"keys": [mocked_key.as_dict(private=False)]}

    # Security checks to make sure no details from the private key are exposed
    private_details = ["d", "p", "q", "dp", "dq", "qi", "oth", "r", "t"]
    assert all(
        private_detail not in jwks["keys"][0].keys()
        for private_detail in private_details
    )


@mock.patch("core.resource_server.utils.import_private_key_from_settings")
def test_view_jwks_invalid_private_key(mock_import_private_key_from_settings):
    """JWKS endpoint should return a proper exception when loading keys fails."""

    mock_import_private_key_from_settings.return_value = "wrong_key"

    url = reverse("resource_server_jwks")
    response = APIClient().get(url)

    mock_import_private_key_from_settings.assert_called_once()

    assert response.status_code == 500
    assert response.json() == {"error": "Could not load key"}


@mock.patch("core.resource_server.utils.import_private_key_from_settings")
def test_view_jwks_missing_private_key(mock_import_private_key_from_settings):
    """JWKS endpoint should return a proper exception when private key is missing."""

    mock_import_private_key_from_settings.side_effect = ImproperlyConfigured("foo.")

    url = reverse("resource_server_jwks")
    response = APIClient().get(url)

    mock_import_private_key_from_settings.assert_called_once()

    assert response.status_code == 500
    assert response.json() == {"error": "foo."}
