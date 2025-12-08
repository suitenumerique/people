"""Tests for token exchange endpoint (RFC 8693)."""

import base64
import logging

from django.urls import reverse
from django.utils import timezone

import pytest
import responses
from rest_framework import status

from core.factories import ServiceProviderFactory

from token_exchange.factories import (
    ScopeGrantFactory,
    ServiceProviderCredentialsFactory,
    TokenExchangeRuleFactory,
)
from token_exchange.models import (
    ExchangedToken,
    TokenTypeChoices,
)
from token_exchange.tests.helpers import (
    DummyBackend,
    create_token_exchange_rule_with_scopes,
)

pytestmark = pytest.mark.django_db


def _mock_introspection_backend(settings, user_info, origin=None):
    """Configure the resource server backend to use a dummy backend for testing.

    Instead of patching the function, we change OIDC_RS_BACKEND_CLASS setting
    to use a custom DummyBackend that returns fixed introspection data.
    """

    # Create a factory function that returns a configured DummyBackend instance
    def backend_factory():
        return DummyBackend(user_info=user_info, origin=origin)

    # Set the backend class to our factory (it will be called by get_resource_server_introspection_backend)
    # We need to use the full module path for the backend class
    settings.OIDC_RS_BACKEND_CLASS = "token_exchange.tests.helpers.DummyBackend"

    # Store the user_info and origin as class attributes so they're accessible
    # when the backend is instantiated
    DummyBackend._test_user_info = user_info
    DummyBackend._test_origin = origin


@responses.activate
def test_exchange_access_token_opaque_success(api_client, settings):
    """Test successful exchange for opaque access_token."""
    # Enable feature
    settings.TOKEN_EXCHANGE_ENABLED = True
    settings.OIDC_OP_INTROSPECTION_ENDPOINT = "http://mock-oidc/introspect"
    settings.OIDC_RS_CLIENT_ID = "aud1"
    settings.OIDC_RS_AUDIENCE_CLAIM = "aud"
    settings.OIDC_OP_URL = "http://mock-oidc"

    # Mock authentication
    sp_audience = "aud1"
    credentials = ServiceProviderCredentialsFactory(
        service_provider__audience_id=sp_audience
    )
    credentials_b64 = base64.b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    # Create token exchange rule and grants
    target_sp = ServiceProviderFactory(audience_id="aud2")
    rule = TokenExchangeRuleFactory(
        source_service=credentials.service_provider,
        target_service=target_sp,
    )
    ScopeGrantFactory(rule=rule, source_scope="openid", granted_scope="openid")
    ScopeGrantFactory(rule=rule, source_scope="email", granted_scope="email")

    # Mock introspection response
    responses.add(
        responses.POST,
        "http://mock-oidc/introspect",
        json={
            "active": True,
            "iss": "http://mock-oidc",
            "sub": "user-123",
            "email": "test@example.com",
            "scope": "openid email",
            "jti": "sso-token-id",
            "aud": sp_audience,
        },
        status=200,
    )

    # Define validation payload
    # auth_payload = {
    #     "sub": "user-123",
    #     "email": "test@example.com",
    #     "scope": "openid email",
    #     "jti": "sso-token-id",
    #     "aud": sp_audience # Matches requesting SP
    # }

    url = reverse("token-exchange")
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "subject_token": "external-sso-token",
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "requested_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "audience": "aud2",
    }

    response = api_client.post(
        url, data, headers={"Authorization": f"Basic {credentials_b64}"}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.data
    assert response.data["token_type"] == "Bearer"
    assert (
        response.data["issued_token_type"]
        == "urn:ietf:params:oauth:token-type:access_token"
    )
    assert "expires_in" in response.data
    assert "scope" in response.data

    # Verify token was created in DB
    assert ExchangedToken.objects.filter(subject_sub="user-123").count() == 1
    token = ExchangedToken.objects.get(subject_sub="user-123")
    assert token.token_type == TokenTypeChoices.ACCESS_TOKEN
    assert token.subject_email == "test@example.com"


@responses.activate
def test_exchange_with_custom_expires_in(api_client, settings):
    """Test exchange with custom expires_in parameter."""
    settings.TOKEN_EXCHANGE_ENABLED = True
    settings.TOKEN_EXCHANGE_MAX_EXPIRES_IN = 7200
    settings.OIDC_OP_INTROSPECTION_ENDPOINT = "http://mock-oidc/introspect"
    settings.OIDC_RS_CLIENT_ID = "aud1"
    settings.OIDC_RS_AUDIENCE_CLAIM = "aud"
    settings.OIDC_OP_URL = "http://mock-oidc"

    # auth_payload = {
    #     "sub": "user-123",
    #     "email": "test@example.com",
    #     "scope": "openid email",
    #     "aud": "aud1"
    # }

    url = reverse("token-exchange")
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "subject_token": "external-sso-token",
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "expires_in": 1800,  # 30 minutes
        "audience": "aud1",
    }

    target_sp = ServiceProviderFactory(audience_id="aud1")
    credentials = ServiceProviderCredentialsFactory(service_provider=target_sp)
    credentials_b64 = base64.b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    # Create token exchange rule
    create_token_exchange_rule_with_scopes(
        credentials.service_provider,
        target_sp,
        ["openid", "email"],
    )

    responses.add(
        responses.POST,
        "http://mock-oidc/introspect",
        json={
            "active": True,
            "iss": "http://mock-oidc",
            "sub": "user-123",
            "email": "test@example.com",
            "scope": "openid email",
            "aud": "aud1",
        },
        status=200,
    )

    response = api_client.post(
        url, data, headers={"Authorization": f"Basic {credentials_b64}"}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["expires_in"] == 1800


@responses.activate
def test_exchange_with_multiple_audiences(api_client, settings):
    """Test exchange with multiple audiences separated by spaces."""
    settings.TOKEN_EXCHANGE_ENABLED = True
    settings.TOKEN_EXCHANGE_MULTI_AUDIENCES_ALLOWED = True
    settings.OIDC_OP_INTROSPECTION_ENDPOINT = "http://mock-oidc/introspect"
    settings.OIDC_RS_CLIENT_ID = "original-aud"
    settings.OIDC_RS_AUDIENCE_CLAIM = "aud"
    settings.OIDC_OP_URL = "http://mock-oidc"

    # auth_payload = {
    #     "sub": "user-123",
    #     "email": "test@example.com",
    #     "aud": "original-aud",
    #     "scope": "openid email"
    # }

    url = reverse("token-exchange")
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "subject_token": "external-sso-token",
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "audience": "aud1 aud2 aud3",
    }

    credentials = ServiceProviderCredentialsFactory(
        service_provider__audience_id="original-aud"
    )
    credentials_b64 = base64.b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    # Create token exchange rules
    sp1 = ServiceProviderFactory(audience_id="aud1")
    sp2 = ServiceProviderFactory(audience_id="aud2")
    sp3 = ServiceProviderFactory(audience_id="aud3")

    create_token_exchange_rule_with_scopes(
        credentials.service_provider, sp1, ["openid", "email"]
    )
    create_token_exchange_rule_with_scopes(
        credentials.service_provider, sp2, ["openid", "email"]
    )
    create_token_exchange_rule_with_scopes(
        credentials.service_provider, sp3, ["openid", "email"]
    )

    responses.add(
        responses.POST,
        "http://mock-oidc/introspect",
        json={
            "active": True,
            "iss": "http://mock-oidc",
            "sub": "user-123",
            "email": "test@example.com",
            "scope": "openid email",
            "aud": "original-aud",
        },
        status=200,
    )

    response = api_client.post(
        url, data, headers={"Authorization": f"Basic {credentials_b64}"}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK

    # Verify audiences were parsed correctly
    token = ExchangedToken.objects.get(subject_sub="user-123")
    assert len(token.audiences) == 3
    assert "aud1" in token.audiences
    assert "aud2" in token.audiences
    assert "aud3" in token.audiences


@responses.activate
def test_exchange_with_scope_subset(api_client, settings):
    """Test exchange with requested scopes that are subset of available."""
    settings.TOKEN_EXCHANGE_ENABLED = True
    settings.OIDC_OP_INTROSPECTION_ENDPOINT = "http://mock-oidc/introspect"
    settings.OIDC_RS_CLIENT_ID = "aud1"
    settings.OIDC_RS_AUDIENCE_CLAIM = "aud"
    settings.OIDC_OP_URL = "http://mock-oidc"

    # auth_payload = {
    #     "sub": "user-123",
    #     "email": "test@example.com",
    #     "scope": "openid email groups profile",
    #     "aud": "aud1"
    # }

    url = reverse("token-exchange")
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "subject_token": "external-sso-token",
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "scope": "openid email",  # Subset of available
        "audience": "aud1",
    }

    target_sp = ServiceProviderFactory(audience_id="aud1")
    credentials = ServiceProviderCredentialsFactory(service_provider=target_sp)
    credentials_b64 = base64.b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    # Create token exchange rule
    create_token_exchange_rule_with_scopes(
        credentials.service_provider,
        target_sp,
        ["openid", "email", "groups", "profile"],
    )

    responses.add(
        responses.POST,
        "http://mock-oidc/introspect",
        json={
            "active": True,
            "iss": "http://mock-oidc",
            "sub": "user-123",
            "email": "test@example.com",
            "scope": "openid email groups profile",
            "aud": "aud1",
        },
        status=200,
    )

    response = api_client.post(
        url, data, headers={"Authorization": f"Basic {credentials_b64}"}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    assert set(response.data["scope"].split()) == {"openid", "email"}


def test_exchange_rejects_refresh_token(api_client, settings):
    """Test that refresh_token type is explicitly rejected."""
    settings.TOKEN_EXCHANGE_ENABLED = True
    settings.OIDC_OP_URL = "http://mock-oidc"
    settings.OIDC_OP_INTROSPECTION_ENDPOINT = "http://mock-oidc/introspect"

    auth_payload = {"sub": "user-123", "email": "test@example.com", "aud": "aud1"}

    url = reverse("token-exchange")
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "subject_token": "external-sso-token",
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "requested_token_type": "urn:ietf:params:oauth:token-type:refresh_token",
        "audience": "aud1",
    }

    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = base64.b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    # Create token exchange rule (though it might fail validation before needing it, safe to have)
    target_sp = ServiceProviderFactory(audience_id="aud1")
    create_token_exchange_rule_with_scopes(
        credentials.service_provider,
        target_sp,
        ["openid", "email"],
    )

    response = api_client.post(
        url, data, headers={"Authorization": f"Basic {credentials_b64}"}, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data
    assert "refresh_token" in str(response.data)


def test_exchange_rejects_invalid_grant_type(api_client, settings):
    """Test that invalid grant_type is rejected."""
    settings.TOKEN_EXCHANGE_ENABLED = True
    settings.OIDC_OP_URL = "http://mock-oidc"
    settings.OIDC_OP_INTROSPECTION_ENDPOINT = "http://mock-oidc/introspect"

    auth_payload = {"sub": "user-123", "email": "test@example.com", "aud": "aud1"}

    url = reverse("token-exchange")
    data = {
        "grant_type": "invalid-grant-type",
        "subject_token": "external-sso-token",
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "audience": "aud1",
    }

    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = base64.b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    target_sp = ServiceProviderFactory(audience_id="aud1")
    create_token_exchange_rule_with_scopes(
        credentials.service_provider,
        target_sp,
        ["openid", "email"],
    )

    response = api_client.post(
        url, data, headers={"Authorization": f"Basic {credentials_b64}"}, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@responses.activate
def test_exchange_rejects_scope_elevation(api_client, settings):
    """Test that scope elevation (requesting additional scopes) is rejected."""
    settings.TOKEN_EXCHANGE_ENABLED = True
    settings.OIDC_OP_INTROSPECTION_ENDPOINT = "http://mock-oidc/introspect"
    settings.OIDC_RS_CLIENT_ID = "aud1"
    settings.OIDC_RS_AUDIENCE_CLAIM = "aud"
    settings.OIDC_OP_URL = "http://mock-oidc"

    # auth_payload = {
    #     "sub": "user-123",
    #     "email": "test@example.com",
    #     "scope": "openid email",
    #     "aud": "aud1"
    # }

    url = reverse("token-exchange")
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "subject_token": "external-sso-token",
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "scope": "openid email profile",  # Requesting extra scope
        "audience": "aud1",
    }

    target_sp = ServiceProviderFactory(audience_id="aud1")
    credentials = ServiceProviderCredentialsFactory(service_provider=target_sp)
    credentials_b64 = base64.b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    create_token_exchange_rule_with_scopes(
        credentials.service_provider,
        target_sp,
        ["openid", "email"],
    )

    responses.add(
        responses.POST,
        "http://mock-oidc/introspect",
        json={
            "active": True,
            "iss": "http://mock-oidc",
            "sub": "user-123",
            "email": "test@example.com",
            "scope": "openid email",
            "aud": "aud1",
        },
        status=200,
    )

    response = api_client.post(
        url, data, headers={"Authorization": f"Basic {credentials_b64}"}, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {
        "error": "invalid_target",
        "error_description": "Invalid target audience",
    }


def test_exchange_rejects_expires_in_exceeding_max(api_client, settings):
    """Test that expires_in exceeding max is rejected."""
    settings.TOKEN_EXCHANGE_ENABLED = True
    settings.TOKEN_EXCHANGE_MAX_EXPIRES_IN = 3600
    settings.OIDC_OP_URL = "http://mock-oidc"
    settings.OIDC_OP_INTROSPECTION_ENDPOINT = "http://mock-oidc/introspect"

    auth_payload = {
        "sub": "user-123",
        "email": "test@example.com",
        "scope": "openid email",
        "aud": "aud1",
    }

    url = reverse("token-exchange")
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "subject_token": "external-sso-token",
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "expires_in": 7200,  # Exceeds max of 3600
        "audience": "aud1",
    }

    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = base64.b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    target_sp = ServiceProviderFactory(audience_id="aud1")
    create_token_exchange_rule_with_scopes(
        credentials.service_provider,
        target_sp,
        ["openid", "email"],
    )

    response = api_client.post(
        url, data, headers={"Authorization": f"Basic {credentials_b64}"}, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_exchange_requires_feature_enabled(api_client, settings):
    """Test that exchange requires TOKEN_EXCHANGE_ENABLED=True."""
    settings.TOKEN_EXCHANGE_ENABLED = False

    url = reverse("token-exchange")
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "subject_token": "external-sso-token",
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "audience": "aud1",
    }

    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = base64.b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    target_sp = ServiceProviderFactory(audience_id="aud1")
    create_token_exchange_rule_with_scopes(
        credentials.service_provider,
        target_sp,
        ["openid", "email"],
    )

    # Even with valid auth, it should fail
    response = api_client.post(
        url, data, headers={"Authorization": f"Basic {credentials_b64}"}, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "token_exchange_disabled" in response.data["error"]


@responses.activate
def test_exchange_enforces_token_limit(api_client, settings):
    """Test that token limit is enforced and oldest tokens are deleted."""
    settings.TOKEN_EXCHANGE_ENABLED = True
    settings.TOKEN_EXCHANGE_MAX_ACTIVE_TOKENS_PER_USER = 3
    settings.OIDC_OP_INTROSPECTION_ENDPOINT = "http://mock-oidc/introspect"
    settings.OIDC_RS_CLIENT_ID = "aud1"
    settings.OIDC_RS_AUDIENCE_CLAIM = "aud"
    settings.OIDC_OP_URL = "http://mock-oidc"

    # auth_payload = {"sub": "user-123", "email": "test@example.com", "scope": "openid email", "aud": "aud1"}

    url = reverse("token-exchange")
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "subject_token": "external-sso-token",
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "audience": "aud1",
    }

    target_sp = ServiceProviderFactory(audience_id="aud1")
    credentials = ServiceProviderCredentialsFactory(service_provider=target_sp)
    credentials_b64 = base64.b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    create_token_exchange_rule_with_scopes(
        credentials.service_provider,
        target_sp,
        ["openid", "email"],
    )

    responses.add(
        responses.POST,
        "http://mock-oidc/introspect",
        json={
            "active": True,
            "iss": "http://mock-oidc",
            "sub": "user-123",
            "email": "test@example.com",
            "scope": "openid email",
            "aud": "aud1",
        },
        status=200,
    )

    # Create 4 tokens (exceeds limit of 3)
    for _i in range(4):
        response = api_client.post(
            url,
            data,
            headers={"Authorization": f"Basic {credentials_b64}"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

    # Should only have 3 tokens (oldest one deleted)
    assert (
        ExchangedToken.objects.filter(
            subject_sub="user-123",
            expires_at__gt=timezone.now(),
            revoked_at__isnull=True,
        ).count()
        == 3
    )


@responses.activate
def test_exchange_logs_token_creation(api_client, caplog, settings):
    """Test that token exchange logs appropriate information."""

    caplog.set_level(logging.INFO)

    settings.TOKEN_EXCHANGE_ENABLED = True
    settings.OIDC_OP_INTROSPECTION_ENDPOINT = "http://mock-oidc/introspect"
    settings.OIDC_RS_CLIENT_ID = "aud1"
    settings.OIDC_RS_AUDIENCE_CLAIM = "aud"
    settings.OIDC_OP_URL = "http://mock-oidc"

    # auth_payload = {
    #     "sub": "user-123",
    #     "email": "logtest@example.com",
    #     "scope": "openid email",
    #     "aud": "aud1"
    # }

    url = reverse("token-exchange")
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "subject_token": "external-sso-token",
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "audience": "aud1",
    }

    target_sp = ServiceProviderFactory(audience_id="aud1")
    credentials = ServiceProviderCredentialsFactory(service_provider=target_sp)
    credentials_b64 = base64.b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    create_token_exchange_rule_with_scopes(
        credentials.service_provider,
        target_sp,
        ["openid", "email"],
    )

    responses.add(
        responses.POST,
        "http://mock-oidc/introspect",
        json={
            "active": True,
            "iss": "http://mock-oidc",
            "sub": "user-123",
            "email": "logtest@example.com",
            "scope": "openid email",
            "aud": "aud1",
        },
        status=200,
    )

    response = api_client.post(
        url, data, headers={"Authorization": f"Basic {credentials_b64}"}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK

    # Check that logging occurred
    assert "Token exchanged" in caplog.text
    assert "logtest@example.com" in caplog.text
    assert "aud1" in caplog.text


@responses.activate
def test_exchange_rejects_unknown_audience(api_client, settings):
    """Test that unknown audience is rejected."""
    settings.TOKEN_EXCHANGE_ENABLED = True
    settings.OIDC_RS_AUDIENCE_CLAIM = "aud"

    credentials = ServiceProviderCredentialsFactory(
        service_provider__audience_id="source-aud",
    )
    credentials_b64 = base64.b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    _mock_introspection_backend(
        settings,
        {
            "active": True,
            "sub": "user-123",
            "email": "user@example.com",
            "scope": "openid",
            "aud": "source-aud",
            "jti": "jti-1",
        },
    )

    response = api_client.post(
        reverse("token-exchange"),
        {
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "subject_token": "external-sso-token",
            "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "audience": "unknown-aud",
        },
        headers={"Authorization": f"Basic {credentials_b64}"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {
        "error": "invalid_target",
        "error_description": "Invalid target audience",
    }


def test_exchange_rejects_inactive_rule(api_client, settings):
    """Test that inactive rule is rejected."""
    settings.TOKEN_EXCHANGE_ENABLED = True

    target_sp = ServiceProviderFactory(audience_id="aud-inactive")
    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = base64.b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    TokenExchangeRuleFactory(
        source_service=credentials.service_provider,
        target_service=target_sp,
        is_active=False,
    )

    response = api_client.post(
        reverse("token-exchange"),
        {
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "subject_token": "external-sso-token",
            "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "audience": target_sp.audience_id,
        },
        headers={"Authorization": f"Basic {credentials_b64}"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "invalid_target"


def test_exchange_invalid_when_identity_missing(api_client, settings):
    """Test that missing identity is rejected."""
    settings.TOKEN_EXCHANGE_ENABLED = True
    settings.OIDC_RS_AUDIENCE_CLAIM = "aud"

    target_sp = ServiceProviderFactory(audience_id="aud-target")
    credentials = ServiceProviderCredentialsFactory(
        service_provider__audience_id="aud-source",
    )
    credentials_b64 = base64.b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    create_token_exchange_rule_with_scopes(
        credentials.service_provider,
        target_sp,
        ["openid"],
    )

    _mock_introspection_backend(
        settings,
        {
            "active": True,
            "scope": "openid",
            "aud": "aud-source",
            "jti": "jti-2",
        },
    )

    response = api_client.post(
        reverse("token-exchange"),
        {
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "subject_token": "external-sso-token",
            "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "audience": target_sp.audience_id,
        },
        headers={"Authorization": f"Basic {credentials_b64}"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "invalid_token"


def test_exchange_rejects_mismatched_token_origin(api_client, settings):
    """Test that mismatched token origin is rejected."""
    settings.TOKEN_EXCHANGE_ENABLED = True
    settings.OIDC_RS_AUDIENCE_CLAIM = "aud"

    target_sp = ServiceProviderFactory(audience_id="aud-target")
    credentials = ServiceProviderCredentialsFactory(
        service_provider__audience_id="aud-source",
    )
    credentials_b64 = base64.b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    create_token_exchange_rule_with_scopes(
        credentials.service_provider,
        target_sp,
        ["openid"],
    )

    _mock_introspection_backend(
        settings,
        {
            "active": True,
            "sub": "user-456",
            "email": "another@example.com",
            "scope": "openid",
            "aud": "aud-source",
            "jti": "jti-3",
        },
        origin="other-aud",
    )

    response = api_client.post(
        reverse("token-exchange"),
        {
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "subject_token": "external-sso-token",
            "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "audience": target_sp.audience_id,
        },
        headers={"Authorization": f"Basic {credentials_b64}"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_exchange_action_scope_requires_permission(api_client, settings):
    """Test that action scope requires permission."""
    settings.TOKEN_EXCHANGE_ENABLED = True
    settings.OIDC_RS_AUDIENCE_CLAIM = "aud"

    target_sp = ServiceProviderFactory(audience_id="aud-action")
    credentials = ServiceProviderCredentialsFactory(
        service_provider__audience_id="aud-source",
    )
    credentials_b64 = base64.b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    TokenExchangeRuleFactory(
        source_service=credentials.service_provider,
        target_service=target_sp,
    )

    _mock_introspection_backend(
        settings,
        {
            "active": True,
            "sub": "user-action",
            "email": "action@example.com",
            "scope": "openid",
            "aud": "aud-source",
            "jti": "jti-4",
        },
    )

    response = api_client.post(
        reverse("token-exchange"),
        {
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "subject_token": "external-sso-token",
            "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "scope": "action:do-something",
            "audience": target_sp.audience_id,
        },
        headers={"Authorization": f"Basic {credentials_b64}"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "invalid_target"


def test_exchange_requires_actor_token_type_when_actor_token_present(
    api_client, settings
):
    """Test that actor_token_type is required when actor_token is present."""
    settings.TOKEN_EXCHANGE_ENABLED = True

    credentials = ServiceProviderCredentialsFactory()
    credentials_b64 = base64.b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    response = api_client.post(
        reverse("token-exchange"),
        {
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "subject_token": "external-sso-token",
            "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "audience": "aud-solo",
            "actor_token": "actor-token-value",
        },
        headers={"Authorization": f"Basic {credentials_b64}"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "actor_token_type" in response.data.get("error_description", "")


def test_exchange_multi_audience_disabled_keeps_first(api_client, settings):
    """Test when multiple audiences are request but not allowed."""
    settings.TOKEN_EXCHANGE_ENABLED = True
    settings.TOKEN_EXCHANGE_MULTI_AUDIENCES_ALLOWED = False
    settings.OIDC_RS_AUDIENCE_CLAIM = "aud"

    credentials = ServiceProviderCredentialsFactory(
        service_provider__audience_id="aud-source",
    )
    credentials_b64 = base64.b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    target_sp_1 = ServiceProviderFactory(audience_id="aud-1")
    target_sp_2 = ServiceProviderFactory(audience_id="aud-2")

    create_token_exchange_rule_with_scopes(
        credentials.service_provider,
        target_sp_1,
        ["openid"],
    )
    create_token_exchange_rule_with_scopes(
        credentials.service_provider,
        target_sp_2,
        ["openid"],
    )

    _mock_introspection_backend(
        settings,
        {
            "active": True,
            "sub": "user-multi",
            "email": "multi@example.com",
            "scope": "openid",
            "aud": "aud-source",
            "jti": "jti-5",
        },
    )

    response = api_client.post(
        reverse("token-exchange"),
        {
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "subject_token": "external-sso-token",
            "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "audience": f"{target_sp_1.audience_id} {target_sp_2.audience_id}",
        },
        headers={"Authorization": f"Basic {credentials_b64}"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    token = ExchangedToken.objects.get(subject_sub="user-multi")
    assert token.audiences == [target_sp_1.audience_id]
