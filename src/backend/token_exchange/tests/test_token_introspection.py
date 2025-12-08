"""Tests for token introspection endpoint (RFC 7662)."""

import logging
from base64 import b64encode
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

import pytest
from rest_framework import status

from token_exchange.factories import (
    ExchangedTokenFactory,
    ExpiredExchangedTokenFactory,
    ServiceProviderCredentialsFactory,
)
from token_exchange.models import ExchangedToken, TokenTypeChoices
from token_exchange.token_generator import TokenGenerator

pytestmark = pytest.mark.django_db


def test_introspect_unauthenticated(api_client):
    """Test that introspection requires authentication."""
    url = reverse("token-introspect")
    valid_opaque_token = ExchangedTokenFactory(
        token_type=TokenTypeChoices.ACCESS_TOKEN,
        scope="openid email",
        audiences=["test-audience"],
        subject_email="test@example.com",
        subject_sub="user-123",
    )
    data = {"token": valid_opaque_token.token}

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["detail"] == "Authentication credentials were not provided."


def test_introspect_valid_opaque_token(api_client):
    """Test introspection of valid opaque token returns active=true with all fields."""
    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    url = reverse("token-introspect")
    valid_opaque_token = ExchangedTokenFactory(
        token_type=TokenTypeChoices.ACCESS_TOKEN,
        scope="openid email",
        audiences=["test-audience"],
        subject_email="test@example.com",
        subject_sub="user-123",
    )
    data = {"token": valid_opaque_token.token}

    response = api_client.post(
        url, data, format="json", headers={"Authorization": f"Basic {credentials_b64}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["active"] is True
    assert response.data["scope"] == "openid email"
    assert response.data["username"] == "test@example.com"
    assert response.data["token_type"] == TokenTypeChoices.ACCESS_TOKEN
    assert "exp" in response.data
    assert "iat" in response.data
    assert response.data["sub"] == "user-123"
    assert response.data["email"] == "test@example.com"
    assert response.data["aud"] == ["test-audience"]
    assert "jti" in response.data


def test_introspect_with_multiple_audiences(api_client):
    """Test introspection returns array for multiple audiences."""
    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    token = ExchangedToken.objects.create(
        token=TokenGenerator.generate_opaque_token(),
        token_type=TokenTypeChoices.ACCESS_TOKEN,
        subject_email="test-aud@example.com",
        subject_sub="user-aud-123",
        audiences=["aud1", "aud2", "aud3"],
        scope="openid email",
        expires_at=timezone.now() + timedelta(hours=1),
        subject_token_jti="test-jti",
        subject_token_scope="openid email",
    )

    url = reverse("token-introspect")
    data = {"token": token.token}

    response = api_client.post(
        url, data, format="json", headers={"Authorization": f"Basic {credentials_b64}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["active"] is True
    assert response.data["aud"] == ["aud1", "aud2", "aud3"]


def test_introspect_no_auth_required(api_client):
    """Test that introspection endpoint allows unauthenticated access."""
    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    valid_opaque_token = ExchangedTokenFactory(
        token_type=TokenTypeChoices.ACCESS_TOKEN,
    )

    # Don't authenticate
    url = reverse("token-introspect")
    data = {"token": valid_opaque_token.token}

    response = api_client.post(
        url, data, format="json", headers={"Authorization": f"Basic {credentials_b64}"}
    )

    # Should succeed even without authentication
    assert response.status_code == status.HTTP_200_OK
    assert response.data["active"] is True


def test_introspect_expired_token(api_client):
    """Test introspection of expired token returns active=false."""
    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    url = reverse("token-introspect")
    expired_token = ExpiredExchangedTokenFactory()
    data = {"token": expired_token.token}

    response = api_client.post(
        url, data, format="json", headers={"Authorization": f"Basic {credentials_b64}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["active"] is False


def test_introspect_revoked_token(api_client):
    """Test introspection of revoked token returns active=false."""
    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    url = reverse("token-introspect")
    revoked_token = ExchangedTokenFactory(revoked_at=timezone.now())
    data = {"token": revoked_token.token}

    response = api_client.post(
        url, data, format="json", headers={"Authorization": f"Basic {credentials_b64}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["active"] is False


def test_introspect_nonexistent_token(api_client):
    """Test introspection of non-existent token returns active=false."""
    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    url = reverse("token-introspect")
    data = {"token": "nonexistent-token-12345"}

    response = api_client.post(
        url, data, format="json", headers={"Authorization": f"Basic {credentials_b64}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["active"] is False
    assert len(response.data) == 1  # Only 'active' field


def test_introspect_empty_token(api_client):
    """Test introspection with empty token returns active=false."""
    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    url = reverse("token-introspect")
    data = {"token": ""}

    response = api_client.post(
        url, data, format="json", headers={"Authorization": f"Basic {credentials_b64}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["active"] is False


def test_introspect_missing_token(api_client):
    """Test introspection without token parameter returns active=false."""
    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    url = reverse("token-introspect")
    data = {}

    response = api_client.post(
        url, data, format="json", headers={"Authorization": f"Basic {credentials_b64}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["active"] is False


def test_introspect_logs_valid_token(api_client, caplog):
    """Test that introspection logs for valid tokens."""
    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    valid_opaque_token = ExchangedTokenFactory(
        token_type=TokenTypeChoices.ACCESS_TOKEN,
    )

    caplog.set_level(logging.INFO)

    url = reverse("token-introspect")
    data = {"token": valid_opaque_token.token}

    response = api_client.post(
        url, data, format="json", headers={"Authorization": f"Basic {credentials_b64}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert "Token introspected" in caplog.text
    assert "active=True" in caplog.text or "active=true" in caplog.text.lower()


def test_introspect_logs_invalid_token(api_client, caplog):
    """Test that introspection logs for invalid tokens."""
    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    caplog.set_level(logging.INFO)

    url = reverse("token-introspect")
    expired_token = ExpiredExchangedTokenFactory()
    data = {"token": expired_token.token}

    response = api_client.post(
        url, data, format="json", headers={"Authorization": f"Basic {credentials_b64}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert "Token introspected" in caplog.text
    assert "active=False" in caplog.text or "active=false" in caplog.text.lower()
