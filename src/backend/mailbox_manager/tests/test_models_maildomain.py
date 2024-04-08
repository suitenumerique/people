"""
Unit tests for the MailDomain model
"""

from django.core.exceptions import ValidationError

import pytest

from mailbox_manager import factories

pytestmark = pytest.mark.django_db


# NAME FIELD


def test_models_mail_domain__domain_name_should_not_be_empty():
    """The domain name field should not be empty."""
    with pytest.raises(ValidationError, match="This field cannot be blank"):
        factories.MailDomainFactory(name="")


def test_models_mail_domain__domain_name_should_not_be_null():
    """The domain name field should not be null."""
    with pytest.raises(ValidationError, match="This field cannot be null."):
        factories.MailDomainFactory(name=None)
