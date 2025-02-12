"""Test authentication backend for OIDC provider."""

import pytest

from core import factories as core_factories

from mailbox_manager import factories
from mailbox_oauth2.backends import MailboxModelBackend, get_username_domain_from_email

pytestmark = pytest.mark.django_db


def test_authenticate_valid_credentials():
    """Test authentication with valid credentials."""
    organization = core_factories.OrganizationFactory(with_registration_id=True)
    domain = factories.MailDomainEnabledFactory(organization=organization)
    mailbox = factories.MailboxEnabledFactory(domain=domain)

    assert domain.identity_provider_ready()

    authenticated_user = MailboxModelBackend().authenticate(
        None, email=f"{mailbox.local_part}@{domain.name}", password="password"
    )

    assert authenticated_user == mailbox


def test_authenticate_no_organization():
    """Test authentication when domain don't have organization."""
    domain = factories.MailDomainEnabledFactory()
    mailbox = factories.MailboxEnabledFactory(domain=domain)

    assert not domain.identity_provider_ready()

    authenticated_user = MailboxModelBackend().authenticate(
        None, email=f"{mailbox.local_part}@{domain.name}", password="password"
    )

    assert authenticated_user is None


def test_authenticate_invalid_email_format():
    """Test authentication with invalid email format."""

    authenticated_user = MailboxModelBackend().authenticate(
        None, email="invalid-email", password="any-password"
    )

    assert authenticated_user is None


def test_authenticate_nonexistent_user():
    """Test authentication with non-existent user."""
    authenticated_user = MailboxModelBackend().authenticate(
        None, email="nonexistent@domain.com", password="any-password"
    )

    assert authenticated_user is None


def test_authenticate_wrong_password():
    """Test authentication with wrong password."""
    organization = core_factories.OrganizationFactory(with_registration_id=True)
    domain = factories.MailDomainEnabledFactory(organization=organization)
    mailbox = factories.MailboxEnabledFactory(domain=domain)

    assert domain.identity_provider_ready()

    authenticated_user = MailboxModelBackend().authenticate(
        None, email=f"{mailbox.local_part}@{domain.name}", password="wrong-password"
    )

    assert authenticated_user is None


def test_authenticate_without_middleware():
    """Test authentication without required middleware."""
    authenticated_user = MailboxModelBackend().authenticate(
        None, email="any@domain.com", password="any-password"
    )

    assert authenticated_user is None


def test_authenticate_inactive_domain():
    """Test authentication with inactive identity provider domain."""
    organization = core_factories.OrganizationFactory(with_registration_id=True)
    domain = factories.MailDomainFactory(organization=organization)
    mailbox = factories.MailboxEnabledFactory(domain=domain)

    assert not domain.identity_provider_ready()

    authenticated_user = MailboxModelBackend().authenticate(
        None, email=f"{mailbox.local_part}@{domain.name}", password="password"
    )

    assert authenticated_user is None


def test_get_user_exists():
    """Test get_user with existing user."""
    organization = core_factories.OrganizationFactory(with_registration_id=True)
    domain = factories.MailDomainEnabledFactory(organization=organization)
    mailbox = factories.MailboxEnabledFactory(domain=domain)

    user = MailboxModelBackend().get_user(mailbox.pk)

    assert user == mailbox


def test_get_user_does_not_exist():
    """Test get_user with non-existent user."""
    user = MailboxModelBackend().get_user(999999)

    assert user is None


def test_authenticate_with_username_only():
    """Test authentication fails when only username is provided (no email)."""
    authenticated_user = MailboxModelBackend().authenticate(
        None, username="test", password="password"
    )
    assert authenticated_user is None


def test_authenticate_sql_injection():
    """Test authentication is safe against SQL injection attempts."""
    organization = core_factories.OrganizationFactory(with_registration_id=True)
    domain = factories.MailDomainEnabledFactory(organization=organization)
    mailbox = factories.MailboxEnabledFactory(domain=domain)

    # Test SQL injection in email field
    authenticated_user = MailboxModelBackend().authenticate(
        None, email="' OR '1'='1", password="password"
    )
    assert authenticated_user is None

    # Test SQL injection in password field
    authenticated_user = MailboxModelBackend().authenticate(
        None, email=f"{mailbox.local_part}@{domain.name}", password="' OR '1'='1"
    )
    assert authenticated_user is None


def test_get_inactive_mailbox():
    """Test get_user with inactive user."""
    organization = core_factories.OrganizationFactory(with_registration_id=True)
    domain = factories.MailDomainEnabledFactory(organization=organization)
    mailbox = factories.MailboxFactory(domain=domain)

    user = MailboxModelBackend().get_user(mailbox.pk)
    assert user is None


def test_get_username_domain_from_email_valid():
    """Test extracting username and domain from valid email."""

    username, domain = get_username_domain_from_email("test@example.com")
    assert username == "test"
    assert domain == "example.com"


def test_get_username_domain_from_email_invalid():
    """Test extracting username and domain from invalid email."""

    username, domain = get_username_domain_from_email("invalid-email")
    assert username is None
    assert domain is None


def test_get_username_domain_from_email_empty():
    """Test extracting username and domain from empty email."""

    username, domain = get_username_domain_from_email("")
    assert username is None
    assert domain is None


def test_get_username_domain_from_email_special_chars():
    """Test extracting username and domain with special characters."""
    username, domain = get_username_domain_from_email("test+label@example.com")
    assert username == "test+label"
    assert domain == "example.com"


def test_get_username_domain_from_email_unicode():
    """Test extracting username and domain with unicode characters."""
    username, domain = get_username_domain_from_email("üser@exämple.com")
    assert username is None
    assert domain is None


def test_get_username_domain_from_double_domain():
    """Test extracting username and domain with double domain."""
    username, domain = get_username_domain_from_email("user@admin@example.com")
    assert username is None
    assert domain is None


def test_login_attempts_tracking(settings):
    """Test tracking of failed login attempts."""
    organization = core_factories.OrganizationFactory(with_registration_id=True)
    domain = factories.MailDomainEnabledFactory(organization=organization)
    mailbox = factories.MailboxEnabledFactory(domain=domain)
    email = f"{mailbox.local_part}@{domain.name}"
    backend = MailboxModelBackend()

    # First attempts should allow authentication (but fail due to wrong password)
    for _ in range(settings.MAX_LOGIN_ATTEMPTS - 1):
        authenticated_user = backend.authenticate(
            None, email=email, password="wrong-password"
        )
        assert authenticated_user is None

    # Last attempt before lockout
    authenticated_user = backend.authenticate(
        None, email=email, password="wrong-password"
    )
    assert authenticated_user is None

    # Account should now be locked
    authenticated_user = backend.authenticate(None, email=email, password="password")
    assert authenticated_user is None


def test_login_attempts_reset_on_success(settings):
    """Test that successful login resets the failed attempts counter."""
    organization = core_factories.OrganizationFactory(with_registration_id=True)
    domain = factories.MailDomainEnabledFactory(organization=organization)
    mailbox = factories.MailboxEnabledFactory(domain=domain)
    email = f"{mailbox.local_part}@{domain.name}"
    backend = MailboxModelBackend()

    # Make some failed attempts
    for _ in range(settings.MAX_LOGIN_ATTEMPTS - 1):
        authenticated_user = backend.authenticate(
            None, email=email, password="wrong-password"
        )
        assert authenticated_user is None

    # Successful login should reset counter
    authenticated_user = backend.authenticate(None, email=email, password="password")
    assert authenticated_user == mailbox

    # Should be able to attempt again after reset
    authenticated_user = backend.authenticate(
        None, email=email, password="wrong-password"
    )
    assert authenticated_user is None


def test_login_attempts_cache_key():
    """Test the cache key generation for login attempts."""
    backend = MailboxModelBackend()
    email = "test@example.com"

    cache_key = backend._get_cache_key(email)  # pylint: disable=protected-access
    assert cache_key == "login_attempts_test_at_example_dot_com"
