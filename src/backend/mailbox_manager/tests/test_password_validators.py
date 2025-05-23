"""Test the production settings for password validation is correct."""

from django.contrib.auth.password_validation import (
    get_default_password_validators,
    validate_password,
)

import pytest

from mailbox_manager.factories import MailboxFactory
from people.settings import Production

pytestmark = pytest.mark.django_db


@pytest.fixture(name="use_production_password_validators")
def use_production_password_validators_fixture(settings):
    """Set the production password validators."""
    settings.AUTH_PASSWORD_VALIDATORS = Production.AUTH_PASSWORD_VALIDATORS

    get_default_password_validators.cache_clear()
    assert len(get_default_password_validators()) == 5

    yield

    get_default_password_validators.cache_clear()


@pytest.mark.parametrize(
    "password, error",
    [
        ("password", "This password is too common."),
        ("password123", "This password is too common."),
        ("123", "This password is too common."),
        ("coucou", "This password is too common."),
        ("john doe 123", "The password is too similar to the"),
    ],
)
def test_validate_password_validator(
    use_production_password_validators,  # pylint: disable=unused-argument
    password,
    error,
):
    """Test the Mailbox password validation."""
    mailbox_1 = MailboxFactory(
        first_name="John",
        last_name="Doe",
    )
    mailbox_2 = MailboxFactory(
        local_part="john.doe",
    )

    with pytest.raises(Exception) as excinfo:
        validate_password(password, mailbox_1)
    assert error in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        validate_password(password, mailbox_2)
    assert error in str(excinfo.value)
