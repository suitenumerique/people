"""Test the one-time token authentication."""

from django.utils import timezone

import pytest
from rest_framework import exceptions

from core import factories as core_factories

from plugins.la_suite import factories
from plugins.la_suite.authentication import OrganizationOneTimeTokenAuthentication

pytestmark = pytest.mark.django_db


def test_valid_token_authentication():
    """Test successful authentication with a valid token."""
    organization = core_factories.OrganizationFactory(with_registration_id=True)
    token = factories.OrganizationOneTimeTokenFactory(organization=organization)
    auth = OrganizationOneTimeTokenAuthentication()
    authenticated_org, authenticated_token = auth.authenticate_credentials(token.key)

    assert authenticated_org == organization
    assert authenticated_token == token


def test_invalid_token():
    """Test authentication fails with invalid token."""
    auth = OrganizationOneTimeTokenAuthentication()

    with pytest.raises(exceptions.AuthenticationFailed, match="Invalid token"):
        auth.authenticate_credentials("invalid_token")


def test_disabled_token():
    """Test authentication fails with disabled token."""
    token = factories.OrganizationOneTimeTokenFactory(enabled=False)

    auth = OrganizationOneTimeTokenAuthentication()

    with pytest.raises(exceptions.AuthenticationFailed, match="Token is disabled"):
        auth.authenticate_credentials(token.key)


def test_used_token():
    """Test authentication fails with already used token."""

    token = factories.OrganizationOneTimeTokenFactory(used_at=timezone.now())

    auth = OrganizationOneTimeTokenAuthentication()

    with pytest.raises(exceptions.AuthenticationFailed, match="Token is disabled"):
        auth.authenticate_credentials(token.key)
