"""
Unit tests for dimail client
"""

# pylint: disable=W0613

import logging
import re

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
    response_mailbox_created,
)

pytestmark = pytest.mark.django_db


@responses.activate
def test_dimail_synchronization__already_sync(dimail_token_ok):
    """
    No mailbox should be created when everything is already synced.
    """
    domain = factories.MailDomainEnabledFactory()
    factories.MailboxFactory.create_batch(3, domain=domain)

    pre_sync_mailboxes = models.Mailbox.objects.filter(domain=domain)
    assert pre_sync_mailboxes.count() == 3

    dimail_client = DimailAPIClient()

    # Ensure successful response using "responses":
    # token response in fixtures
    responses.get(
        re.compile(rf".*/v2/domains/{domain.name}/mailboxes/"),
        json=[
            {
                "type": "mailbox",
                "active": "yes",
                "email": f"{mailbox.local_part}@{domain.name}",
                "features": ["ox"],
                "extras": {
                    "ox": {
                        "given_name": mailbox.first_name,
                        "sur_name": mailbox.last_name,
                        "display_name": f"{mailbox.first_name} {mailbox.last_name}",
                    },
                    "schedule": None,
                },
                "dirty_quirks": {"ox-config": {}},
                "additionalSenders": [],
                "rate_limit": None,
                "quota": None,
            }
            for mailbox in pre_sync_mailboxes
        ],
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
    imported_mailboxes = dimail_client.import_mailboxes(domain)

    post_sync_mailboxes = models.Mailbox.objects.filter(domain=domain)
    assert post_sync_mailboxes.count() == 3
    assert imported_mailboxes == []
    assert set(models.Mailbox.objects.filter(domain=domain)) == set(pre_sync_mailboxes)


@responses.activate
def test_dimail_import_mailboxes(caplog, dimail_token_ok):  # pylint: disable=W0613, R0914
    """Importing mailboxes from dimail should synchronize valid mailboxes
    and log errors for invalid ones."""
    caplog.set_level(logging.INFO)

    domain = factories.MailDomainEnabledFactory()

    existing_alias = factories.AliasFactory(domain=domain)

    dimail_client = DimailAPIClient()
    # Ensure successful response using "responses":
    # successful token in fixtures
    mailbox_valid = {
        "type": "mailbox",
        "active": "yes",
        "email": f"michael.roch@{domain.name}",
        "features": ["ox"],
        "extras": {
            "ox": {
                "given_name": "Michael",
                "sur_name": "Roch",
                "display_name": "Michael Roch",
            },
            "schedule": None,
        },
        "dirty_quirks": {"ox-config": {}},
        "additionalSenders": [],
        "rate_limit": None,
        "quota": None,
    }
    mailbox_oxadmin = {
        "type": "mailbox",
        "active": "yes",
        "email": f"oxadmin@{domain.name}",
        "features": ["ox"],
        "extras": {
            "ox": {
                "given_name": "Admin",
                "sur_name": "Context",
                "display_name": "Context Admin",
            },
            "schedule": None,
        },
        "dirty_quirks": {"ox-config": {}},
        "additionalSenders": [],
        "rate_limit": None,
        "quota": None,
    }
    mailbox_with_invalid_local_part = {
        "type": "mailbox",
        "active": "yes",
        "email": f"obalmaské@{domain.name}",
        "features": ["ox"],
        "extras": {
            "ox": {
                "given_name": "Jean",
                "sur_name": "Vang",
                "display_name": "Jean Vang",
            },
            "schedule": None,
        },
        "dirty_quirks": {"ox-config": {}},
        "additionalSenders": [],
        "rate_limit": None,
        "quota": None,
    }
    mailbox_existing_alias = {
        "type": "mailbox",
        "active": "yes",
        "email": f"{existing_alias.local_part}@{domain.name}",
        "features": ["ox"],
        "extras": {
            "ox": {
                "given_name": "Support",
                "sur_name": "email",
                "display_name": "Support email",
            },
            "schedule": None,
        },
        "dirty_quirks": {"ox-config": {}},
        "additionalSenders": [],
        "rate_limit": None,
        "quota": None,
    }
    functional_mailbox = {
        "type": "mailbox",
        "active": "yes",
        "email": f"functional_mailbox@{domain.name}",
        "features": [],
        "extras": {"ox": None, "schedule": None},
        "dirty_quirks": None,
        "additionalSenders": [],
        "rate_limit": None,
        "quota": None,
    }

    responses.get(
        re.compile(rf".*/v2/domains/{domain.name}/mailboxes/"),
        json=[
            mailbox_valid,  # successful
            mailbox_oxadmin,  # technical
            mailbox_with_invalid_local_part,  # failed
            mailbox_existing_alias,  # successful
            functional_mailbox,  # failed - not implemented yet
        ],
        status=status.HTTP_200_OK,
        content_type="application/json",
    )

    imported_mailboxes = dimail_client.import_mailboxes(domain)

    # 2 successful not in log
    # 2 technical + 2 failed = 4 records
    assert len(caplog.records) == 4
    log_messages = [record.message for record in caplog.records]

    expected_messages = [
        "Token successfully granted by mail-provisioning API.",
        f"Not importing OX technical address: oxadmin@{domain.name}",
        f"Import of email {mailbox_with_invalid_local_part['email']} failed with error local-part \
contains non-ASCII characters)",
        f"Skipping functional mailbox: '{functional_mailbox['email']}'",
    ]
    for message in expected_messages:
        assert message in log_messages

    assert models.Mailbox.objects.count() == 2
    assert imported_mailboxes == [
        mailbox_valid["email"],
        mailbox_existing_alias["email"],
    ]


@responses.activate
def test_dimail_synchronization__synchronize_aliases(dimail_token_ok):  # pylint: disable=unused-argument
    """Importing aliases from dimail should synchronize valid aliases
    and log errors for invalid ones."""
    alias = factories.AliasFactory()
    dimail_client = DimailAPIClient()

    existing_mailbox = factories.MailboxFactory(domain=alias.domain)

    # Ensure successful response using "responses":
    # token response in fixtures
    incoming_aliases = [
        {
            "username": "contact",
            "domain": alias.domain.name,
            "destination": alias.destination,  # same destination = ok
            "allow_to_send": False,
        },
        {
            "username": alias.local_part,  # same username = ok
            "domain": alias.domain.name,
            "destination": "maheius.endorecles@somethingelse.com",
            "allow_to_send": False,
        },
        {  # same username + same destination = big nono
            "username": alias.local_part,
            "domain": alias.domain.name,
            "destination": alias.destination,
            "allow_to_send": False,
        },
        {  # mailbox with same username = ok
            "username": existing_mailbox.local_part,
            "domain": alias.domain.name,
            "destination": existing_mailbox.secondary_email,
            "allow_to_send": False,
        },
        {  # alias to devnull@devnull
            "username": "spam",
            "domain": alias.domain.name,
            "destination": "devnull@devnull",
            "allow_to_send": False,
        },
    ]
    responses.get(
        re.compile(rf".*/domains/{alias.domain.name}/aliases/"),
        json=incoming_aliases,
        status=status.HTTP_200_OK,
        content_type="application/json",
    )

    imported_aliases = dimail_client.import_aliases(alias.domain)

    assert len(imported_aliases) == 4
    assert models.Alias.objects.count() == 5


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
    responses.get(
        re.compile(rf".*/domains/{domain.name}/check"),
        json=body_content,
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
    responses.get(
        re.compile(rf".*/domains/{domain.name}/check"),
        json=body_domain_broken,
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
    responses.get(
        re.compile(rf".*/domains/{domain.name}/check"),
        json=body_domain_ok,
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
    responses.get(
        re.compile(rf".*/domains/{domain.name}/check"),
        json=body_domain_broken,
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
    # the endpoint fix is called and still returns KO for internal checks
    responses.get(
        re.compile(rf".*/domains/{domain.name}/fix/"),
        json=body_domain_broken,
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
    responses.get(
        re.compile(rf".*/domains/{domain.name}/check"),
        json=body_domain_broken,
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
    responses.get(
        re.compile(rf".*/domains/{domain.name}/check"),
        json=body_domain_broken_internal,
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
    # the endpoint fix is called and returns OK. Hooray!
    body_domain_ok = CHECK_DOMAIN_OK.copy()
    body_domain_ok["name"] = domain.name
    responses.get(
        re.compile(rf".*/domains/{domain.name}/fix/"),
        json=body_domain_ok,
        status=status.HTTP_200_OK,
        content_type="application/json",
    )

    dimail_client.fetch_domain_status(domain)
    domain.refresh_from_db()
    assert domain.status == enums.MailDomainStatusChoices.ENABLED
    assert domain.last_check_details == body_domain_ok


@responses.activate
def test_dimail__send_pending_mailboxes(caplog, dimail_token_ok):
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

    # Ensure successful response using "responses":
    # token response in fixtures
    responses.post(
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
    assert "Token successfully granted by mail-provisioning API." in log_messages
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
