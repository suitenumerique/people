"""
Unit tests for the mailbox model
"""

from django.core import exceptions
from django.test.utils import override_settings

import pytest

from mailbox_manager import enums, factories, models

pytestmark = pytest.mark.django_db

# LOCAL PART FIELD


def test_models_mailboxes__local_part_cannot_be_empty():
    """The "local_part" field should not be empty."""
    with pytest.raises(exceptions.ValidationError, match="This field cannot be blank"):
        factories.MailboxFactory(local_part="")


def test_models_mailboxes__local_part_cannot_be_null():
    """The "local_part" field should not be null."""
    with pytest.raises(exceptions.ValidationError, match="This field cannot be null"):
        factories.MailboxFactory(local_part=None)


def test_models_mailboxes__local_part_matches_expected_format():
    """
    The local part should contain alpha-numeric caracters
    and a limited set of special caracters ("+", "-", ".", "_").
    """
    # "-", ".", "_" are allowed
    factories.MailboxFactory(local_part="Marie-Jose.Perec_2024")

    # other special characters should raise a validation error
    # "+" included, as this test is about mail creation
    for character in ["+", "@", "!", "$", "%", " "]:
        with pytest.raises(exceptions.ValidationError, match="Enter a valid value"):
            factories.MailboxFactory(local_part=f"marie{character}jo")


def test_models_mailboxes__local_part_unique_per_domain():
    """Local parts should be unique per domain."""

    existing_mailbox = factories.MailboxFactory()

    # same local part on another domain should not be a problem
    factories.MailboxFactory(local_part=existing_mailbox.local_part)

    # same local part on the same domain should not be possible
    with pytest.raises(
        exceptions.ValidationError,
        match="Mailbox with this Local_part and Domain already exists.",
    ):
        factories.MailboxFactory(
            local_part=existing_mailbox.local_part, domain=existing_mailbox.domain
        )


# DOMAIN FIELD


def test_models_mailboxes__domain_must_be_a_maildomain_instance():
    """The "domain" field should be an instance of MailDomain."""
    expected_error = '"Mailbox.domain" must be a "MailDomain" instance.'
    with pytest.raises(ValueError, match=expected_error):
        factories.MailboxFactory(domain="")

    with pytest.raises(ValueError, match=expected_error):
        factories.MailboxFactory(domain="domain-as-string.com")


def test_models_mailboxes__domain_cannot_be_null():
    """The "domain" field should not be null."""
    with pytest.raises(models.MailDomain.DoesNotExist, match="Mailbox has no domain."):
        factories.MailboxFactory(domain=None)


# SECONDARY_EMAIL FIELD


def test_models_mailboxes__secondary_email_cannot_be_empty():
    """The "secondary_email" field should not be empty."""
    with pytest.raises(exceptions.ValidationError, match="This field cannot be blank"):
        factories.MailboxFactory(secondary_email="")


def test_models_mailboxes__secondary_email_cannot_be_null():
    """The "secondary_email" field should not be null."""
    with pytest.raises(exceptions.ValidationError, match="This field cannot be null"):
        factories.MailboxFactory(secondary_email=None)


def test_models_mailboxes__cannot_be_created_for_disabled_maildomain():
    """Mailbox creation is allowed only for a domain enabled.
    A disabled status for the mail domain raises an error."""
    with pytest.raises(
        exceptions.ValidationError,
        match="You can create mailbox only for a domain enabled",
    ):
        factories.MailboxFactory(
            domain=factories.MailDomainFactory(
                status=enums.MailDomainStatusChoices.DISABLED
            )
        )


def test_models_mailboxes__cannot_be_created_for_failed_maildomain():
    """Mailbox creation is allowed only for a domain enabled.
    A failed status for the mail domain raises an error."""
    with pytest.raises(
        exceptions.ValidationError,
        match="You can create mailbox only for a domain enabled",
    ):
        factories.MailboxFactory(
            domain=factories.MailDomainFactory(
                status=enums.MailDomainStatusChoices.FAILED
            )
        )


def test_models_mailboxes__cannot_be_created_for_pending_maildomain():
    """Mailbox creation is allowed only for a domain enabled.
    A pending status for the mail domain raises an error."""
    with pytest.raises(
        exceptions.ValidationError,
        match="You can create mailbox only for a domain enabled",
    ):
        # MailDomainFactory initializes a mail domain with default values,
        # so mail domain status is pending!
        factories.MailboxFactory(domain=factories.MailDomainFactory())


### REACTING TO DIMAIL-API
### We mock dimail's responses to avoid testing dimail's container too


@override_settings(MAIL_PROVISIONING_API_CREDENTIALS=None)
def test_models_mailboxes__dimail_no_credentials():
    """
    If MAIL_PROVISIONING_API_CREDENTIALS setting is not configured,
    trying to create a mailbox should raise an error.
    """
    domain = factories.MailDomainEnabledFactory()

    with pytest.raises(
        exceptions.ValidationError,
        match="Please configure MAIL_PROVISIONING_API_CREDENTIALS before creating any mailbox.",
    ):
        factories.MailboxFactory(domain=domain)
