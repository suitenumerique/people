"""Tests for OAuth2 validators."""

from django.contrib.auth.models import AnonymousUser

import pytest
from oauth2_provider.models import Application

from core import factories as core_factories

from mailbox_manager import factories
from mailbox_oauth2.validators import BaseValidator, ProConnectValidator

pytestmark = pytest.mark.django_db


@pytest.fixture(name="mailbox")
def mailbox_fixture():
    """Create a mailbox for testing."""
    organization = core_factories.OrganizationFactory(with_registration_id=True)
    domain = factories.MailDomainEnabledFactory(
        organization=organization, name="example.com"
    )
    return factories.MailboxEnabledFactory(
        domain=domain, local_part="user", first_name="John", last_name="Doe"
    )


@pytest.fixture(name="oauth_request_authenticated")
def oauth_request_authenticated_fixture(mailbox):
    """Create a mock OAuth request object with authenticated user."""

    class MockRequest:  # pylint: disable=missing-class-docstring
        def __init__(self):
            self.user = mailbox
            self.scopes = set()
            self.claims = None
            self.acr_values = None

    return MockRequest()


@pytest.fixture(name="oauth_request_anonymous")
def oauth_request_anonymous_fixture():
    """Create a mock OAuth request object with anonymous user."""

    class MockRequest:  # pylint: disable=missing-class-docstring
        def __init__(self):
            self.user = AnonymousUser()
            self.scopes = set()
            self.claims = None
            self.acr_values = None

    return MockRequest()


@pytest.fixture(name="oauth_request_for_auth_code")
def oauth_request_for_auth_code_fixture(oauth_request_authenticated):
    """Create a mock OAuth request object with full authorization code attributes."""

    class MockRequestWithClient:  # pylint: disable=missing-class-docstring,too-many-instance-attributes
        def __init__(self, base_request):
            self.user = base_request.user
            self.scopes = {"openid"}
            self.claims = None
            self.acr_values = None
            # Required OAuth2 attributes for authorization code
            self.client = Application.objects.create(
                name="test_app",
                client_type=Application.CLIENT_CONFIDENTIAL,
                authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
                skip_authorization=True,
            )
            self.redirect_uri = "https://example.com/callback"
            self.code_challenge = "test_challenge"
            self.code_challenge_method = "S256"
            self.nonce = "test_nonce"

    return MockRequestWithClient(oauth_request_authenticated)


# Base Validator Tests
def test_get_additional_claims_basic(oauth_request_authenticated):
    """Test basic additional claims without scopes."""
    validator = BaseValidator()
    claims = validator.get_additional_claims(oauth_request_authenticated)

    assert claims["sub"] == str(oauth_request_authenticated.user.pk)
    assert claims["amr"] == "pwd"
    assert "email" not in claims


def test_get_additional_claims_with_email_scope(oauth_request_authenticated):
    """Test additional claims with email scope."""
    validator = BaseValidator()
    oauth_request_authenticated.scopes = {"email"}
    claims = validator.get_additional_claims(oauth_request_authenticated)

    assert claims["email"] == oauth_request_authenticated.user.get_email()


def test_validate_silent_authorization_authenticated(oauth_request_authenticated):
    """Test silent authorization with authenticated user."""
    validator = BaseValidator()
    assert validator.validate_silent_authorization(oauth_request_authenticated) is True


def test_validate_silent_authorization_unauthenticated(oauth_request_anonymous):
    """Test silent authorization with unauthenticated user."""
    validator = BaseValidator()
    assert validator.validate_silent_authorization(oauth_request_anonymous) is False


def test_validate_silent_login_authenticated(oauth_request_authenticated):
    """Test silent login with authenticated user."""
    validator = BaseValidator()
    assert validator.validate_silent_login(oauth_request_authenticated) is True


def test_validate_silent_login_unauthenticated(oauth_request_anonymous):
    """Test silent login with unauthenticated user."""
    validator = BaseValidator()
    assert validator.validate_silent_login(oauth_request_anonymous) is False


def test_introspect_token_not_implemented():
    """Test that introspect_token raises RuntimeError."""
    validator = BaseValidator()
    with pytest.raises(RuntimeError, match="Introspection not implemented"):
        validator.introspect_token(None, None, None)


# ProConnect Validator Tests
def test_proconnect_get_additional_claims_given_name(oauth_request_authenticated):
    """Test getting given_name claim."""
    validator = ProConnectValidator()
    oauth_request_authenticated.scopes = {"given_name"}
    claims = validator.get_additional_claims(oauth_request_authenticated)
    assert claims["given_name"] == "John"


def test_proconnect_get_additional_claims_usual_name(oauth_request_authenticated):
    """Test getting usual_name claim."""
    validator = ProConnectValidator()
    oauth_request_authenticated.scopes = {"usual_name"}
    claims = validator.get_additional_claims(oauth_request_authenticated)
    assert claims["usual_name"] == "Doe"


def test_proconnect_get_additional_claims_siret(oauth_request_authenticated):
    """Test getting siret claim."""
    validator = ProConnectValidator()
    oauth_request_authenticated.scopes = {"siret"}
    claims = validator.get_additional_claims(oauth_request_authenticated)
    assert (
        claims["siret"]
        == oauth_request_authenticated.user.domain.organization.registration_id_list[0]
    )


def test_proconnect_get_additional_claims_with_acr_claim(oauth_request_authenticated):
    """Test getting acr claim when eidas1 is requested."""
    validator = ProConnectValidator()
    oauth_request_authenticated.claims = {"acr": "eidas1"}
    claims = validator.get_additional_claims(oauth_request_authenticated)
    assert claims["acr"] == "eidas1"


def test_proconnect_get_additional_claims_without_acr_claim(
    oauth_request_authenticated,
):
    """Test no acr claim when not requested."""
    validator = ProConnectValidator()
    claims = validator.get_additional_claims(oauth_request_authenticated)
    assert "acr" not in claims


def test_proconnect_create_authorization_code_with_eidas1(oauth_request_for_auth_code):
    """Test creating authorization code with eidas1 acr value."""
    validator = ProConnectValidator()
    oauth_request_for_auth_code.acr_values = "eidas1"
    code = {"code": "test_code"}  # OAuth2 provider expects a dict with 'code' key
    validator._create_authorization_code(oauth_request_for_auth_code, code)  # pylint: disable=protected-access
    assert oauth_request_for_auth_code.claims == {"acr": "eidas1"}


def test_proconnect_create_authorization_code_without_eidas1(
    oauth_request_for_auth_code,
):
    """Test creating authorization code without eidas1 acr value."""
    validator = ProConnectValidator()
    oauth_request_for_auth_code.acr_values = "other_value"
    code = {"code": "test_code"}  # OAuth2 provider expects a dict with 'code' key
    validator._create_authorization_code(oauth_request_for_auth_code, code)  # pylint: disable=protected-access
    assert not oauth_request_for_auth_code.claims
