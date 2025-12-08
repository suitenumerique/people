"""Tests for new token exchange models with ActionScopes and throttling."""

import base64
import json

from django.urls import reverse

import pytest
import responses
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from joserfc import jwt
from joserfc.jwk import RSAKey
from lasuite.oidc_resource_server.backend import ResourceServerBackend
from pytest_unordered import unordered
from rest_framework import status

from core.factories import ServiceProviderFactory

from token_exchange.factories import (
    ActionScopeFactory,
    ActionScopeGrantFactory,
    ScopeGrantFactory,
    ServiceProviderCredentialsFactory,
    TokenExchangeActionPermissionFactory,
    TokenExchangeRuleFactory,
)
from token_exchange.models import ExchangedToken, TokenTypeChoices

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def relax_backend(monkeypatch):
    """Disable strict scope verification from the ResourceServerBackend for these tests."""
    monkeypatch.setattr(
        ResourceServerBackend, "_verify_user_info", lambda self, claims: claims
    )


@responses.activate
def test_exchange_with_scope_grant_and_throttling(api_client, settings, monkeypatch):
    """Test token exchange with scope grant that includes throttling."""
    settings.TOKEN_EXCHANGE_ENABLED = True
    settings.OIDC_OP_INTROSPECTION_ENDPOINT = "http://mock-oidc/introspect"
    settings.OIDC_RS_CLIENT_ID = "service-a"
    settings.OIDC_RS_AUDIENCE_CLAIM = "aud"
    settings.OIDC_OP_URL = "http://mock-oidc"
    settings.OIDC_RS_REQUIRED_SCOPES = []

    # Setup: Service A → Service B with throttled scope
    service_a = ServiceProviderFactory(audience_id="service-a")
    service_b = ServiceProviderFactory(audience_id="service-b")
    credentials = ServiceProviderCredentialsFactory(service_provider=service_a)
    credentials_b64 = base64.b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    # Create rule with scope grants
    rule = TokenExchangeRuleFactory(source_service=service_a, target_service=service_b)
    ScopeGrantFactory(
        rule=rule,
        source_scope="orders.read",
        granted_scope="orders.read",
        throttle_rate=None,  # No throttling
    )
    ScopeGrantFactory(
        rule=rule,
        source_scope="payments.write",
        granted_scope="payments.write",
        throttle_rate="5/h",  # Throttled
    )
    ScopeGrantFactory(
        rule=rule,
        source_scope="payments.write",
        granted_scope="payments.refund",
        throttle_rate="5/h",  # Throttled
    )

    # Mock introspection
    responses.add(
        responses.POST,
        "http://mock-oidc/introspect",
        json={
            "active": True,
            "iss": "http://mock-oidc",
            "sub": "user-123",
            "email": "test@example.com",
            "scope": "orders.read payments.write",
            "jti": "token-jti",
            "aud": "service-a",
        },
        status=200,
    )

    # Exchange token
    url = reverse("token-exchange")
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "subject_token": "external-sso-token",
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "audience": "service-b",
    }

    response = api_client.post(
        url, data, headers={"Authorization": f"Basic {credentials_b64}"}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.data

    # Verify the exchanged token contains grants
    token = ExchangedToken.objects.get(subject_sub="user-123")
    assert "orders.read" in token.scope
    assert "payments.write" in token.scope
    assert "payments.refund" not in token.scope  # no escalation without requesting it

    assert token.grants == {
        'service-b': unordered([
            {'scope': 'orders.read', 'throttle': {}},
            {'scope': 'payments.write', 'throttle': {'rate': '5/h'}}
        ]),
    }


@responses.activate
def test_exchange_with_action_scope(api_client, settings):
    """Test token exchange with action scope that grants multiple scopes."""
    settings.TOKEN_EXCHANGE_ENABLED = True
    settings.OIDC_OP_INTROSPECTION_ENDPOINT = "http://mock-oidc/introspect"
    settings.OIDC_RS_CLIENT_ID = "service-a"
    settings.OIDC_RS_AUDIENCE_CLAIM = "aud"
    settings.OIDC_OP_URL = "http://mock-oidc"
    settings.OIDC_RS_REQUIRED_SCOPES = []

    # Setup: Service A → Service B with action scope
    service_a = ServiceProviderFactory(audience_id="service-a")
    service_b = ServiceProviderFactory(audience_id="service-b")
    credentials = ServiceProviderCredentialsFactory(service_provider=service_a)
    credentials_b64 = base64.b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    # Create an action scope
    action = ActionScopeFactory(
        name="action:upload-transcript",
        description="Upload and process student transcript",
    )

    # Action grants multiple scopes on service B
    ActionScopeGrantFactory(
        action=action,
        target_service=service_b,
        granted_scope="files.write",
        throttle_rate="10/h",
    )
    ActionScopeGrantFactory(
        action=action,
        target_service=service_b,
        granted_scope="transcripts.create",
        throttle_rate="5/h",
    )

    # Create rule and permission
    rule = TokenExchangeRuleFactory(source_service=service_a, target_service=service_b)
    TokenExchangeActionPermissionFactory(
        rule=rule,
        action=action,
        required_source_scope="admin",  # Requires admin scope to use this action
    )

    # Mock introspection with admin scope
    responses.add(
        responses.POST,
        "http://mock-oidc/introspect",
        json={
            "active": True,
            "iss": "http://mock-oidc",
            "sub": "user-456",
            "email": "admin@example.com",
            "scope": "admin",
            "jti": "token-jti-2",
            "aud": "service-a",
        },
        status=200,
    )

    # Exchange token requesting the action
    url = reverse("token-exchange")
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "subject_token": "external-sso-token",
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "audience": "service-b",
        "scope": "action:upload-transcript",
    }

    response = api_client.post(
        url, data, headers={"Authorization": f"Basic {credentials_b64}"}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK

    # Verify the exchanged token contains all action scopes
    token = ExchangedToken.objects.get(subject_sub="user-456")
    assert "files.write" in token.scope
    assert "transcripts.create" in token.scope

    # Should have grants with throttling organized by audience_id
    assert "service-b" in token.grants
    grants_for_service_b = token.grants["service-b"]
    assert len(grants_for_service_b) == 2
    throttle_rates = {g["scope"]: g["throttle"]["rate"] for g in grants_for_service_b}
    assert throttle_rates["files.write"] == "10/h"
    assert throttle_rates["transcripts.create"] == "5/h"


@responses.activate
def test_exchange_action_scope_requires_permission(api_client, settings):
    """Test that action scope requires proper source scope."""
    settings.TOKEN_EXCHANGE_ENABLED = True
    settings.OIDC_OP_INTROSPECTION_ENDPOINT = "http://mock-oidc/introspect"
    settings.OIDC_RS_CLIENT_ID = "service-a"
    settings.OIDC_RS_AUDIENCE_CLAIM = "aud"
    settings.OIDC_OP_URL = "http://mock-oidc"
    settings.OIDC_RS_REQUIRED_SCOPES = []

    # Setup
    service_a = ServiceProviderFactory(audience_id="service-a")
    service_b = ServiceProviderFactory(audience_id="service-b")
    credentials = ServiceProviderCredentialsFactory(service_provider=service_a)
    credentials_b64 = base64.b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    # Create an action that requires admin scope
    action = ActionScopeFactory(name="action:delete-account")
    ActionScopeGrantFactory(
        action=action,
        target_service=service_b,
        granted_scope="accounts.delete",
    )

    rule = TokenExchangeRuleFactory(source_service=service_a, target_service=service_b)
    TokenExchangeActionPermissionFactory(
        rule=rule,
        action=action,
        required_source_scope="admin",  # Requires admin
    )

    # Mock introspection WITHOUT admin scope
    responses.add(
        responses.POST,
        "http://mock-oidc/introspect",
        json={
            "active": True,
            "iss": "http://mock-oidc",
            "sub": "user-789",
            "email": "user@example.com",
            "scope": "read",  # Only has read, not admin
            "jti": "token-jti-3",
            "aud": "service-a",
        },
        status=200,
    )

    # Try to exchange with action scope
    url = reverse("token-exchange")
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "subject_token": "external-sso-token",
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "audience": "service-b",
        "scope": "action:delete-account",
    }

    response = api_client.post(
        url, data, headers={"Authorization": f"Basic {credentials_b64}"}, format="json"
    )

    # Should fail because user doesn't have required admin scope
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {
        "error": "invalid_target",
        "error_description": "Invalid target audience",
    }


@responses.activate
def test_exchange_jwt_contains_grants_in_payload(api_client, settings):
    """Test that JWT tokens contain grants in the payload."""
    settings.TOKEN_EXCHANGE_ENABLED = True
    settings.OIDC_OP_INTROSPECTION_ENDPOINT = "http://mock-oidc/introspect"
    settings.OIDC_RS_CLIENT_ID = "service-a"
    settings.OIDC_RS_AUDIENCE_CLAIM = "aud"
    settings.OIDC_OP_URL = "http://mock-oidc"
    settings.OIDC_RS_REQUIRED_SCOPES = []

    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    settings.TOKEN_EXCHANGE_JWT_SIGNING_KEYS = {"test-key-1": private_pem}
    settings.TOKEN_EXCHANGE_JWT_CURRENT_KID = "test-key-1"
    settings.TOKEN_EXCHANGE_JWT_ALGORITHM = "RS256"

    # Setup
    service_a = ServiceProviderFactory(audience_id="service-a")
    service_b = ServiceProviderFactory(audience_id="service-b")
    credentials = ServiceProviderCredentialsFactory(service_provider=service_a)
    credentials_b64 = base64.b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode()
    ).decode()

    # Create rule with throttled grant
    rule = TokenExchangeRuleFactory(source_service=service_a, target_service=service_b)
    ScopeGrantFactory(
        rule=rule,
        source_scope="api.access",
        granted_scope="api.access",
        throttle_rate="100/day",
    )

    # Mock introspection
    responses.add(
        responses.POST,
        "http://mock-oidc/introspect",
        json={
            "active": True,
            "iss": "http://mock-oidc",
            "sub": "user-jwt",
            "email": "jwt@example.com",
            "scope": "api.access",
            "jti": "token-jti-jwt",
            "aud": "service-a",
        },
        status=200,
    )

    # Request JWT token
    url = reverse("token-exchange")
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "subject_token": "external-sso-token",
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "requested_token_type": "urn:ietf:params:oauth:token-type:jwt",
        "audience": "service-b",
    }

    response = api_client.post(
        url, data, headers={"Authorization": f"Basic {credentials_b64}"}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["issued_token_type"] == "urn:ietf:params:oauth:token-type:jwt"

    # Decode JWT to verify grants are in the payload
    token_value = response.data["access_token"]
    key = RSAKey.import_key(private_pem)
    claims = jwt.decode(token_value, key).claims

    # Verify grants in JWT payload
    assert "grants" in claims
    assert isinstance(claims["grants"], dict)
    assert "service-b" in claims["grants"]
    service_b_grants = claims["grants"]["service-b"]
    assert len(service_b_grants) == 1
    assert service_b_grants[0]["scope"] == "api.access"
    assert service_b_grants[0]["throttle"]["rate"] == "100/day"
    assert claims["aud"] == ["service-b"]
    assert "api.access" in claims["scope"]
