"""
Unit tests for the mailbox model
"""

from django.core.exceptions import ValidationError

import pytest

from mailbox_manager import enums, factories

pytestmark = pytest.mark.django_db


# LOCAL PART FIELD


def test_models_mailboxes__local_part_cannot_be_empty():
    """The "local_part" field should not be empty."""
    with pytest.raises(ValidationError, match="This field cannot be blank"):
        factories.MailboxFactory(local_part="")


def test_models_mailboxes__local_part_cannot_be_null():
    """The "local_part" field should not be null."""
    with pytest.raises(ValidationError, match="This field cannot be null"):
        factories.MailboxFactory(local_part=None)


def test_models_mailboxes__local_part_matches_expected_format():
    """
    The local part should contain alpha-numeric caracters
    and a limited set of special caracters ("+", "-", ".", "_").
    """
    factories.MailboxFactory(local_part="Marie-Jose.Perec+JO_2024")

    with pytest.raises(ValidationError, match="Enter a valid value"):
        factories.MailboxFactory(local_part="mariejo@unnecessarydomain.com")

    with pytest.raises(ValidationError, match="Enter a valid value"):
        factories.MailboxFactory(local_part="!")


def test_models_mailboxes__local_part_unique_per_domain():
    """Local parts should be unique per domain."""

    existing_mailbox = factories.MailboxFactory()

    # same local part on another domain should not be a problem
    factories.MailboxFactory(local_part=existing_mailbox.local_part)

    # same local part on the same domain should not be possible
    with pytest.raises(
        ValidationError, match="Mailbox with this Local_part and Domain already exists."
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
    with pytest.raises(ValidationError, match="This field cannot be null"):
        factories.MailboxFactory(domain=None)


# SECONDARY_EMAIL FIELD


def test_models_mailboxes__secondary_email_cannot_be_empty():
    """The "secondary_email" field should not be empty."""
    with pytest.raises(ValidationError, match="This field cannot be blank"):
        factories.MailboxFactory(secondary_email="")


def test_models_mailboxes__secondary_email_cannot_be_null():
    """The "secondary_email" field should not be null."""
    with pytest.raises(ValidationError, match="This field cannot be null"):
        factories.MailboxFactory(secondary_email=None)


def test_models_mailboxes__cannot_be_created_for_disabled_maildomain():
    """Mailbox creation is allowed only for a domain enabled.
    A disabled status for the mail domain raises an error."""
    with pytest.raises(
        ValidationError, match="You can create mailbox only for a domain enabled"
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
        ValidationError, match="You can create mailbox only for a domain enabled"
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
        ValidationError, match="You can create mailbox only for a domain enabled"
    ):
        # MailDomainFactory initializes a mail domain with default values,
        # so mail domain status is pending!
        factories.MailboxFactory(domain=factories.MailDomainFactory())
