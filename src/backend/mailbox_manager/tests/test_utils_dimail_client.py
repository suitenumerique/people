"""
Unit tests for dimail client
"""

import json
import logging
import re
from email.errors import HeaderParseError, NonASCIILocalPartDefect
from logging import Logger
from unittest import mock

import pytest
import responses
from rest_framework import status

from mailbox_manager import enums, factories, models
from mailbox_manager.utils.dimail import DimailAPIClient

from .fixtures.dimail import (
    CHECK_DOMAIN_BROKEN,
    CHECK_DOMAIN_OK,
    TOKEN_OK,
    response_mailbox_created,
)

pytestmark = pytest.mark.django_db


def test_dimail_synchronization__already_sync():
    """
    No mailbox should be created when everything is already synced.
    """
    domain = factories.MailDomainEnabledFactory()
    factories.MailboxFactory.create_batch(3, domain=domain)

    pre_sync_mailboxes = models.Mailbox.objects.filter(domain=domain)
    assert pre_sync_mailboxes.count() == 3

    dimail_client = DimailAPIClient()
    with responses.RequestsMock() as rsps:
        # Ensure successful response using "responses":
        rsps.add(
            rsps.GET,
            re.compile(r".*/token/"),
            body='{"access_token": "dimail_people_token"}',
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        rsps.add(
            rsps.GET,
            re.compile(rf".*/domains/{domain.name}/mailboxes/"),
            body=str(
                [
                    {
                        "type": "mailbox",
                        "status": "broken",
                        "email": f"{mailbox.local_part}@{domain.name}",
                        "givenName": mailbox.first_name,
                        "surName": mailbox.last_name,
                        "displayName": f"{mailbox.first_name} {mailbox.last_name}",
                    }
                    for mailbox in pre_sync_mailboxes
                ]
            ),
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        imported_mailboxes = dimail_client.import_mailboxes(domain)

    post_sync_mailboxes = models.Mailbox.objects.filter(domain=domain)
    assert post_sync_mailboxes.count() == 3
    assert imported_mailboxes == []
    assert set(models.Mailbox.objects.filter(domain=domain)) == set(pre_sync_mailboxes)


@mock.patch.object(Logger, "warning")
def test_dimail_synchronization__synchronize_mailboxes(mock_warning):
    """A mailbox existing solely on dimail should be synchronized
    upon calling sync function on its domain"""
    domain = factories.MailDomainEnabledFactory()
    assert not models.Mailbox.objects.exists()

    dimail_client = DimailAPIClient()
    with responses.RequestsMock() as rsps:
        # Ensure successful response using "responses":
        rsps.add(
            rsps.GET,
            re.compile(r".*/token/"),
            body='{"access_token": "dimail_people_token"}',
            status=status.HTTP_200_OK,
            content_type="application/json",
        )

        mailbox_valid = {
            "type": "mailbox",
            "status": "broken",
            "email": f"oxadmin@{domain.name}",
            "givenName": "Admin",
            "surName": "Context",
            "displayName": "Context Admin",
        }
        mailbox_with_wrong_domain = {
            "type": "mailbox",
            "status": "broken",
            "email": "johndoe@wrongdomain.com",
            "givenName": "John",
            "surName": "Doe",
            "displayName": "John Doe",
        }
        mailbox_with_invalid_domain = {
            "type": "mailbox",
            "status": "broken",
            "email": f"naw@ake@{domain.name}",
            "givenName": "Joe",
            "surName": "Doe",
            "displayName": "Joe Doe",
        }
        mailbox_with_invalid_local_part = {
            "type": "mailbox",
            "status": "broken",
            "email": f"obalmaské@{domain.name}",
            "givenName": "Jean",
            "surName": "Vang",
            "displayName": "Jean Vang",
        }

        rsps.add(
            rsps.GET,
            re.compile(rf".*/domains/{domain.name}/mailboxes/"),
            body=str(
                [
                    mailbox_valid,
                    mailbox_with_wrong_domain,
                    mailbox_with_invalid_domain,
                    mailbox_with_invalid_local_part,
                ]
            ),
            status=status.HTTP_200_OK,
            content_type="application/json",
        )

        imported_mailboxes = dimail_client.import_mailboxes(domain)

        # 3 imports failed: wrong domain, HeaderParseError, NonASCIILocalPartDefect
        assert mock_warning.call_count == 3

        # first we try to import email with a wrong domain
        assert mock_warning.call_args_list[0][0] == (
            "Import of email %s failed because of a wrong domain",
            mailbox_with_wrong_domain["email"],
        )

        # then we try to import email with invalid domain
        invalid_mailbox_log = mock_warning.call_args_list[1][0]
        assert invalid_mailbox_log[1] == mailbox_with_invalid_domain["email"]
        assert isinstance(invalid_mailbox_log[2], HeaderParseError)

        # finally we try to import email with non ascii local part
        non_ascii_mailbox_log = mock_warning.call_args_list[2][0]
        assert non_ascii_mailbox_log[1] == mailbox_with_invalid_local_part["email"]
        assert isinstance(non_ascii_mailbox_log[2], NonASCIILocalPartDefect)

        mailbox = models.Mailbox.objects.get()
        assert mailbox.local_part == "oxadmin"
        assert mailbox.status == enums.MailboxStatusChoices.ENABLED
        assert imported_mailboxes == [mailbox_valid["email"]]


def test_dimail__fetch_domain_status_from_dimail():
    """Request to dimail health status of a domain"""
    domain = factories.MailDomainEnabledFactory()
    with responses.RequestsMock() as rsps:
        body_content = CHECK_DOMAIN_BROKEN.copy()
        body_content["name"] = domain.name
        rsps.add(
            rsps.GET,
            re.compile(rf".*/domains/{domain.name}/check/"),
            body=json.dumps(body_content),
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        dimail_client = DimailAPIClient()
        response = dimail_client.fetch_domain_status(domain)
        assert response.status_code == status.HTTP_200_OK
        assert domain.status == enums.MailDomainStatusChoices.FAILED

        # Now domain is ok again
        body_content = CHECK_DOMAIN_OK.copy()
        body_content["name"] = domain.name
        rsps.add(
            rsps.GET,
            re.compile(rf".*/domains/{domain.name}/check/"),
            body=json.dumps(body_content),
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        response = dimail_client.fetch_domain_status(domain)
        assert response.status_code == status.HTTP_200_OK
        assert domain.status == enums.MailDomainStatusChoices.ENABLED


def test_dimail___enable_pending_mailboxes(caplog):
    """Status of pending mailboxes should switch to "enabled"
    when calling enable_pending_mailboxes."""
    caplog.set_level(logging.INFO)

    domain = factories.MailDomainFactory()
    mailbox1 = factories.MailboxFactory(
        domain=domain, status=enums.MailboxStatusChoices.PENDING
    )
    mailbox2 = factories.MailboxFactory(
        domain=domain, status=enums.MailboxStatusChoices.PENDING
    )
    factories.MailboxFactory.create_batch(
        2, domain=domain, status=enums.MailboxStatusChoices.ENABLED
    )

    dimail_client = DimailAPIClient()
    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.GET,
            re.compile(r".*/token/"),
            body=TOKEN_OK,
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(rf".*/domains/{domain.name}/mailboxes/"),
            body=response_mailbox_created(f"mock@{domain.name}"),
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )
        dimail_client.enable_pending_mailboxes(domain=domain)

    mailbox1.refresh_from_db()
    mailbox2.refresh_from_db()
    assert mailbox1.status == enums.MailboxStatusChoices.ENABLED
    assert mailbox2.status == enums.MailboxStatusChoices.ENABLED

    assert len(caplog.records) == 6
    assert (
        caplog.records[0].message
        == "Token succesfully granted by mail-provisioning API."
    )
    assert (
        caplog.records[1].message
        == f"Mailbox successfully created on domain {domain.name} by user None"
    )
    assert (
        caplog.records[2].message
        == f"Information for mailbox mock@{domain.name} sent to {mailbox1.secondary_email}."
    )
    assert (
        caplog.records[4].message
        == f"Mailbox successfully created on domain {domain.name} by user None"
    )
    assert (
        caplog.records[5].message
        == f"Information for mailbox mock@{domain.name} sent to {mailbox2.secondary_email}."
    )
