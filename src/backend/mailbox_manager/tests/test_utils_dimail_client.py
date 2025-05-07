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
    CHECK_DOMAIN_BROKEN_EXTERNAL,
    CHECK_DOMAIN_BROKEN_INTERNAL,
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


@pytest.mark.parametrize(
    "domain_status",
    [
        enums.MailDomainStatusChoices.PENDING,
        enums.MailDomainStatusChoices.ACTION_REQUIRED,
        enums.MailDomainStatusChoices.FAILED,
        enums.MailDomainStatusChoices.ENABLED,
    ],
)
@responses.activate
def test_dimail__fetch_domain_status__switch_to_enabled(domain_status):
    """Domains should be enabled when dimail check returns ok status"""
    domain = factories.MailDomainFactory(status=domain_status)
    body_content = CHECK_DOMAIN_OK.copy()
    body_content["name"] = domain.name
    responses.add(
        responses.GET,
        re.compile(rf".*/domains/{domain.name}/check/"),
        body=json.dumps(body_content),
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
    dimail_client = DimailAPIClient()
    dimail_client.fetch_domain_status(domain)
    domain.refresh_from_db()
    assert domain.status == enums.MailDomainStatusChoices.ENABLED
    assert domain.last_check_details == body_content

    # call again, should be ok
    dimail_client.fetch_domain_status(domain)
    domain.refresh_from_db()
    assert domain.status == enums.MailDomainStatusChoices.ENABLED
    assert domain.last_check_details == body_content


@pytest.mark.parametrize(
    "domain_status",
    [
        enums.MailDomainStatusChoices.PENDING,
        enums.MailDomainStatusChoices.ENABLED,
        enums.MailDomainStatusChoices.ACTION_REQUIRED,
        enums.MailDomainStatusChoices.FAILED,
    ],
)
@responses.activate
def test_dimail__fetch_domain_status__switch_to_action_required(
    domain_status,
):
    """Domains should be in status action required when dimail check
    returns broken status for external checks."""
    domain = factories.MailDomainFactory(status=domain_status)
    body_domain_broken = CHECK_DOMAIN_BROKEN_EXTERNAL.copy()
    body_domain_broken["name"] = domain.name
    responses.add(
        responses.GET,
        re.compile(rf".*/domains/{domain.name}/check/"),
        body=json.dumps(body_domain_broken),
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
    dimail_client = DimailAPIClient()
    dimail_client.fetch_domain_status(domain)
    domain.refresh_from_db()
    assert domain.status == enums.MailDomainStatusChoices.ACTION_REQUIRED
    assert domain.last_check_details == body_domain_broken

    # Support team fixes their part of the problem
    # Now domain is OK again
    body_domain_ok = CHECK_DOMAIN_OK.copy()
    body_domain_ok["name"] = domain.name
    responses.add(
        responses.GET,
        re.compile(rf".*/domains/{domain.name}/check/"),
        body=json.dumps(body_domain_ok),
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
    dimail_client.fetch_domain_status(domain)
    domain.refresh_from_db()
    assert domain.status == enums.MailDomainStatusChoices.ENABLED
    assert domain.last_check_details == body_domain_ok


@pytest.mark.parametrize(
    "domain_status",
    [
        enums.MailDomainStatusChoices.PENDING,
        enums.MailDomainStatusChoices.ENABLED,
        enums.MailDomainStatusChoices.ACTION_REQUIRED,
    ],
)
@responses.activate
def test_dimail__fetch_domain_status__switch_to_failed(domain_status):
    """Domains should be in status failed when dimail check returns broken status
    for only internal checks dispite a fix call."""
    domain = factories.MailDomainFactory(status=domain_status)
    # nothing can be done by support team, domain should be in failed
    body_domain_broken = CHECK_DOMAIN_BROKEN_INTERNAL.copy()
    body_domain_broken["name"] = domain.name
    responses.add(
        responses.GET,
        re.compile(rf".*/domains/{domain.name}/check/"),
        body=json.dumps(body_domain_broken),
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
    # the endpoint fix is called and still returns KO for internal checks
    responses.add(
        responses.GET,
        re.compile(rf".*/domains/{domain.name}/fix/"),
        body=json.dumps(body_domain_broken),
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
    dimail_client = DimailAPIClient()
    dimail_client.fetch_domain_status(domain)
    domain.refresh_from_db()
    assert domain.status == enums.MailDomainStatusChoices.FAILED
    assert domain.last_check_details == body_domain_broken


@pytest.mark.parametrize(
    "domain_status",
    [
        enums.MailDomainStatusChoices.PENDING,
        enums.MailDomainStatusChoices.ENABLED,
        enums.MailDomainStatusChoices.ACTION_REQUIRED,
    ],
)
@responses.activate
def test_dimail__fetch_domain_status__full_fix_scenario(domain_status):
    """Domains should be enabled when dimail check returns ok status
    after a fix call."""
    domain = factories.MailDomainFactory(status=domain_status)
    # with all checks KO, domain should be in action required
    body_domain_broken = CHECK_DOMAIN_BROKEN.copy()
    body_domain_broken["name"] = domain.name
    responses.add(
        responses.GET,
        re.compile(rf".*/domains/{domain.name}/check/"),
        body=json.dumps(body_domain_broken),
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
    dimail_client = DimailAPIClient()
    dimail_client.fetch_domain_status(domain)
    domain.refresh_from_db()
    assert domain.status == enums.MailDomainStatusChoices.ACTION_REQUIRED
    assert domain.last_check_details == body_domain_broken

    # We assume that the support has fixed their part.
    # So now dimail returns OK for external checks but still KO for internal checks.
    # A call to dimail fix endpoint is necessary and will be done by
    # the fetch_domain_status call
    body_domain_broken_internal = CHECK_DOMAIN_BROKEN_INTERNAL.copy()
    body_domain_broken_internal["name"] = domain.name
    responses.add(
        responses.GET,
        re.compile(rf".*/domains/{domain.name}/check/"),
        body=json.dumps(body_domain_broken_internal),
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
    # the endpoint fix is called and returns OK. Hooray!
    body_domain_ok = CHECK_DOMAIN_OK.copy()
    body_domain_ok["name"] = domain.name
    responses.add(
        responses.GET,
        re.compile(rf".*/domains/{domain.name}/fix/"),
        body=json.dumps(body_domain_ok),
        status=status.HTTP_200_OK,
        content_type="application/json",
    )

    dimail_client.fetch_domain_status(domain)
    domain.refresh_from_db()
    assert domain.status == enums.MailDomainStatusChoices.ENABLED
    assert domain.last_check_details == body_domain_ok


def test_dimail__send_pending_mailboxes(caplog):
    """Status of pending mailboxes should switch to "enabled"
    when calling send_pending_mailboxes."""
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
        dimail_client.send_pending_mailboxes(domain=domain)

    mailbox1.refresh_from_db()
    mailbox2.refresh_from_db()
    assert mailbox1.status == enums.MailboxStatusChoices.ENABLED
    assert mailbox2.status == enums.MailboxStatusChoices.ENABLED

    log_messages = [msg.message for msg in caplog.records]
    assert "Token succesfully granted by mail-provisioning API." in log_messages
    assert (
        f"Mailbox successfully created on domain {domain.name} by user None"
        in log_messages
    )
    assert (
        f"Information for mailbox mock@{domain.name} sent to {mailbox2.secondary_email}."
        in log_messages
    )
    assert (
        f"Mailbox successfully created on domain {domain.name} by user None"
        in log_messages
    )
    assert (
        f"Information for mailbox mock@{domain.name} sent to {mailbox1.secondary_email}."
        in log_messages
    )
