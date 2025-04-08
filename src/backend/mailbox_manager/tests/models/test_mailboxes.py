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
    with pytest.raises(exceptions.ValidationError, match="This field cannot be null"):
        factories.MailboxFactory(domain=None)


# SECONDARY_EMAIL FIELD


@pytest.mark.parametrize(
    "domain_status",
    [
        enums.MailDomainStatusChoices.PENDING,
        enums.MailDomainStatusChoices.FAILED,
    ],
)
def test_models_mailboxes__can_create_pending_mailboxes_on_non_enabled_domain(
    domain_status,
):
    """Mailbox creation is allowed for a domain pending and failed.
    A pending mailbox is created."""
    mailbox = factories.MailboxFactory(
        domain=factories.MailDomainFactory(status=domain_status)
    )
    assert mailbox.status == enums.MailboxStatusChoices.PENDING


def test_models_mailboxes__cannot_create_mailboxes_on_disabled_domain():
    """Mailbox creation is not allowed for a domain disabled.
    A disabled status for the mail domain raises an error."""
    with pytest.raises(
        exceptions.ValidationError,
        match="You can't create or update a mailbox for a disabled domain.",
    ):
        factories.MailboxFactory(
            domain=factories.MailDomainFactory(
                status=enums.MailDomainStatusChoices.DISABLED
            )
        )
        assert not models.Mailbox.objects.exist()


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
