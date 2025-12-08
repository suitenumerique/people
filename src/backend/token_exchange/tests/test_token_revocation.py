"""Tests for token revocation endpoint (RFC 7009)."""

import logging
from base64 import b64encode

from django.urls import reverse
from django.utils import timezone

import pytest
from rest_framework import status

from token_exchange.factories import (
    ExchangedTokenFactory,
    ServiceProviderCredentialsFactory,
)

pytestmark = pytest.mark.django_db


def test_revoke_token_success(api_client):
    """Test that authenticated user can successfully revoke a token."""
    # Authenticate as a service provider
    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    valid_token = ExchangedTokenFactory()

    url = reverse("token-revoke")
    data = {"token": valid_token.token}

    response = api_client.post(
        url, data, format="json", headers={"Authorization": f"Basic {credentials_b64}"}
    )

    # RFC 7009: Always return 200 OK
    assert response.status_code == status.HTTP_200_OK

    # Verify token was revoked
    valid_token.refresh_from_db()
    assert valid_token.is_revoked() is True
    assert valid_token.revoked_at is not None
    assert valid_token.is_valid() is False


def test_revoke_sets_revoked_at_timestamp(api_client):
    """Test that revocation sets revoked_at timestamp."""
    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()
    valid_token = ExchangedTokenFactory()

    before_revoke = timezone.now()

    url = reverse("token-revoke")
    data = {"token": valid_token.token}

    response = api_client.post(
        url, data, format="json", headers={"Authorization": f"Basic {credentials_b64}"}
    )

    after_revoke = timezone.now()

    assert response.status_code == status.HTTP_200_OK

    valid_token.refresh_from_db()
    assert valid_token.revoked_at is not None
    assert before_revoke <= valid_token.revoked_at <= after_revoke


def test_revoke_with_token_type_hint(api_client):
    """Test revocation with optional token_type_hint parameter."""
    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()
    valid_token = ExchangedTokenFactory()

    url = reverse("token-revoke")
    data = {
        "token": valid_token.token,
        "token_type_hint": "access_token",
    }

    response = api_client.post(
        url, data, format="json", headers={"Authorization": f"Basic {credentials_b64}"}
    )

    assert response.status_code == status.HTTP_200_OK

    valid_token.refresh_from_db()
    assert valid_token.is_revoked() is True


def test_revoked_token_becomes_invalid(api_client):
    """Test that token becomes invalid after revocation."""
    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()
    valid_token = ExchangedTokenFactory()

    # Token is valid before revocation
    assert valid_token.is_valid() is True

    url = reverse("token-revoke")
    data = {"token": valid_token.token}

    response = api_client.post(
        url, data, format="json", headers={"Authorization": f"Basic {credentials_b64}"}
    )
    assert response.status_code == status.HTTP_200_OK

    # Token is invalid after revocation
    valid_token.refresh_from_db()
    assert valid_token.is_valid() is False
    assert valid_token.is_revoked() is True


def test_introspection_returns_inactive_after_revocation(api_client):
    """Test that introspection returns active=false after revocation."""
    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    # First, revoke the token
    valid_token = ExchangedTokenFactory()
    revoke_url = reverse("token-revoke")
    revoke_data = {"token": valid_token.token}
    revoke_response = api_client.post(
        revoke_url,
        revoke_data,
        format="json",
        headers={"Authorization": f"Basic {credentials_b64}"},
    )
    assert revoke_response.status_code == status.HTTP_200_OK

    # Now introspect the revoked token
    introspect_url = reverse("token-introspect")
    introspect_data = {"token": valid_token.token}

    response = api_client.post(
        introspect_url,
        introspect_data,
        format="json",
        headers={"Authorization": f"Basic {credentials_b64}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["active"] is False


def test_revoke_nonexistent_token_returns_200(api_client):
    """Test that revoking non-existent token returns 200 (RFC 7009)."""
    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    url = reverse("token-revoke")
    data = {"token": "nonexistent-token-12345"}

    response = api_client.post(
        url, data, format="json", headers={"Authorization": f"Basic {credentials_b64}"}
    )

    # RFC 7009: Silent success
    assert response.status_code == status.HTTP_200_OK


def test_revoke_requires_authentication(api_client):
    """Test that revocation requires authentication."""
    valid_token = ExchangedTokenFactory()

    # Don't authenticate
    url = reverse("token-revoke")
    data = {"token": valid_token.token}

    response = api_client.post(url, data, format="json")

    # Should fail without authentication (ResourceServerMixin requirement)
    assert response.status_code in [
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    ]


def test_revoke_logs_successful_revocation(api_client, caplog):
    """Test that successful revocation is logged."""
    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    caplog.set_level(logging.INFO)

    valid_token = ExchangedTokenFactory()

    url = reverse("token-revoke")
    data = {"token": valid_token.token}

    response = api_client.post(
        url, data, format="json", headers={"Authorization": f"Basic {credentials_b64}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert "Token revoked" in caplog.text
    # We removed user from log, used sub/email instead which are random/none in factory unless set
    # check valid_token.subject_sub is randomized?
    # Factory uses LazyFunction uuid4 for sub.
    # It might NOT be logged if factory didn't set it (Factory has user field removed, and defaults set).
    # We should verify "sub=" or "email=" is present.
    assert "sub=" in caplog.text


def test_revoke_logs_attempted_revocation(api_client, caplog):
    """Test that attempted revocation of non-existent token is logged."""
    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    caplog.set_level(logging.INFO)

    url = reverse("token-revoke")
    data = {"token": "nonexistent-token"}

    response = api_client.post(
        url, data, format="json", headers={"Authorization": f"Basic {credentials_b64}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert "Token revocation attempted" in caplog.text
