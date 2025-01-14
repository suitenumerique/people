"""Test authentication backend for OIDC provider."""

from django.contrib.auth.hashers import make_password

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

    assert domain.is_identity_provider_ready()

    authenticated_user = MailboxModelBackend().authenticate(
        None, email=f"{mailbox.local_part}@{domain.name}", password="password"
    )

    assert authenticated_user == mailbox

    # Is case insensitive
    authenticated_user = MailboxModelBackend().authenticate(
        None, email=f"{mailbox.local_part.upper()}@{domain.name}", password="password"
    )

    assert authenticated_user == mailbox


def test_authenticate_no_organization():
    """Test authentication when domain don't have organization."""
    domain = factories.MailDomainEnabledFactory()
    mailbox = factories.MailboxEnabledFactory(domain=domain)

    assert not domain.is_identity_provider_ready()

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

    assert domain.is_identity_provider_ready()

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

    assert not domain.is_identity_provider_ready()

    authenticated_user = MailboxModelBackend().authenticate(
        None, email=f"{mailbox.local_part}@{domain.name}", password="password"
    )

    assert authenticated_user is None


def test_authenticate_unusable_password():
    """
    Test authentication with valid mailbox. but with unusable password.
    This test is important because we use "make_password(None)" to generate
    an unusable password for the mailbox (instead of set_unusable_password()
    which would require an extra query).
    """
    organization = core_factories.OrganizationFactory(with_registration_id=True)
    domain = factories.MailDomainEnabledFactory(organization=organization)
    mailbox = factories.MailboxEnabledFactory(domain=domain)
    mailbox.password = make_password(None)
    mailbox.save()

    assert domain.is_identity_provider_ready()

    authenticated_user = MailboxModelBackend().authenticate(
        None, email=f"{mailbox.local_part}@{domain.name}", password=mailbox.password
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


@pytest.mark.parametrize(
    "email, expected_username, expected_domain",
    [
        ("test@example.com", "test", "example.com"),
        ("test+label@example.com", "test+label", "example.com"),
        ("invalid-email", None, None),
        ("", None, None),
        ("üser@exämple.com", None, None),
        ("user@admin@example.com", None, None),
        ("unicodeonly@üser.com", "unicodeonly", "üser.com"),
        ("spaces in@domain.com", None, None),
        ("verylong" + "a" * 1000 + "@example.com", None, None),
        ("verylong@ex" + "a" * 1000 + "mple.com", None, None),
        ("weird\0char@domain.com", None, None),
        ("@domain.com", None, None),
        ("username@", None, None),
        ("quotes'and,commas@example.com", None, None),
    ],
)
def test_get_username_domain_from_email(email, expected_username, expected_domain):
    """Test extracting username and domain from email."""
    username, domain = get_username_domain_from_email(email)
    assert username == expected_username
    assert domain == expected_domain


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
