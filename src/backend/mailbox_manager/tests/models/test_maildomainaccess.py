"""
Unit tests for the MailDomainAccess model
"""

from django.core.exceptions import ValidationError

import pytest

from mailbox_manager import factories

pytestmark = pytest.mark.django_db

# USER FIELD


def test_models_maildomainaccess__user_be_a_user_instance():
    """The "user" field should be a user instance."""
    expected_error = '"MailDomainAccess.user" must be a "User" instance.'
    with pytest.raises(ValueError, match=expected_error):
        factories.MailDomainAccessFactory(user="")


def test_models_maildomainaccess__user_should_not_be_null():
    """The user field should not be null."""
    with pytest.raises(ValidationError, match="This field cannot be null."):
        factories.MailDomainAccessFactory(user=None)


# DOMAIN FIELD


def test_models_maildomainaccesses__domain_must_be_a_maildomain_instance():
    """The "domain" field should be an instance of MailDomain."""
    expected_error = '"MailDomainAccess.domain" must be a "MailDomain" instance.'
    with pytest.raises(ValueError, match=expected_error):
        factories.MailDomainAccessFactory(domain="")

    with pytest.raises(ValueError, match=expected_error):
        factories.MailDomainAccessFactory(domain="domain-as-string.com")


def test_models_maildomainaccesses__domain_cannot_be_null():
    """The "domain" field should not be null."""
    with pytest.raises(ValidationError, match="This field cannot be null"):
        factories.MailDomainAccessFactory(domain=None)


# ROLE FIELD


def test_models_maildomainaccesses__role_cannot_be_empty():
    """The "role" field cannot be empty."""
    with pytest.raises(ValidationError, match="This field cannot be blank"):
        factories.MailDomainAccessFactory(role="")


def test_models_maildomainaccesses__role_cannot_be_null():
    """The "role" field cannot be null."""
    with pytest.raises(ValidationError, match="This field cannot be null"):
        factories.MailDomainAccessFactory(role=None)
