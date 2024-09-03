"""
Unit tests for the mailbox model
"""

import json
import re
from logging import Logger
from unittest import mock

from django.core import exceptions

import pytest
import responses
from rest_framework import status

from mailbox_manager import enums, factories, models
from mailbox_manager.api import serializers

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


### SYNC TO DIMAIL-API


def test_models_mailboxes__no_secret():
    """If no secret is declared on the domain, the function should raise an error."""
    domain = factories.MailDomainEnabledFactory(secret=None)

    with pytest.raises(
        exceptions.ValidationError,
        match="Please configure your domain's secret before creating any mailbox.",
    ):
        factories.MailboxFactory(domain=domain)


def test_models_mailboxes__wrong_secret():
    """If domain secret is inaccurate, the function should raise an error."""

    domain = factories.MailDomainEnabledFactory()

    with responses.RequestsMock() as rsps:
        # Ensure successful response by scim provider using "responses":
        rsps.add(
            rsps.GET,
            re.compile(r".*/token/"),
            body='{"detail": "Permission denied"}',
            status=status.HTTP_403_FORBIDDEN,
            content_type="application/json",
        )

        with pytest.raises(
            exceptions.PermissionDenied,
            match=f"Token denied - Wrong secret on mail domain {domain.name}",
        ):
            mailbox = factories.MailboxFactory(use_mock=False, domain=domain)
            # Payload sent to mailbox provider
            payload = json.loads(rsps.calls[1].request.body)
            assert payload == {
                "displayName": f"{mailbox.first_name} {mailbox.last_name}",
                "givenName": mailbox.first_name,
                "surName": mailbox.last_name,
            }


@mock.patch.object(Logger, "error")
@mock.patch.object(Logger, "info")
def test_models_mailboxes__create_mailbox_success(mock_info, mock_error):
    """Creating a mailbox sends the expected information and get expected response before saving."""
    domain = factories.MailDomainEnabledFactory()

    # generate mailbox data before mailbox, to mock responses
    mailbox_data = serializers.MailboxSerializer(
        factories.MailboxFactory.build(domain=domain)
    ).data

    with responses.RequestsMock() as rsps:
        # Ensure successful response using "responses":
        rsps.add(
            rsps.GET,
            re.compile(r".*/token/"),
            body='{"access_token": "domain_owner_token"}',
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(rf".*/domains/{domain.name}/mailboxes/"),
            body=str(
                {
                    "email": f"{mailbox_data['local_part']}@{domain.name}",
                    "password": "newpass",
                    "uuid": "uuid",
                }
            ),
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )

        mailbox = factories.MailboxFactory(
            use_mock=False, local_part=mailbox_data["local_part"], domain=domain
        )

        # Check headers
        headers = rsps.calls[1].request.headers
        # assert "Authorization" not in headers
        assert headers["Content-Type"] == "application/json"

        # Payload sent to mailbox provider
        payload = json.loads(rsps.calls[1].request.body)
        assert payload == {
            "displayName": f"{mailbox.first_name} {mailbox.last_name}",
            "givenName": mailbox.first_name,
            "surName": mailbox.last_name,
        }

    # Logger
    assert not mock_error.called
    assert mock_info.call_count == 2
    assert mock_info.call_args_list[0][0] == (
        "Token succesfully granted by mail-provisioning API.",
    )
    assert mock_info.call_args_list[1][0] == (
        "Mailbox successfully created on domain %s",
        domain.name,
    )
    assert mock_info.call_args_list[1][1] == (
        {
            "extra": {
                "response": str(
                    {
                        "email": f"{mailbox.local_part}@{domain.name}",
                        "password": "newpass",
                        "uuid": "uuid",
                    }
                )
            }
        }
    )
