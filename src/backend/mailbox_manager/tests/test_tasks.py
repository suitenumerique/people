"""
Unit tests for mailbox manager tasks.
"""

import json
import re

import pytest
import responses

from mailbox_manager import enums, factories, tasks

from .fixtures.dimail import CHECK_DOMAIN_BROKEN_INTERNAL, CHECK_DOMAIN_OK

pytestmark = pytest.mark.django_db


@responses.activate
def test_fetch_domain_status_task_success():  # pylint: disable=too-many-locals
    """Test fetch domain status from dimail task"""

    domain_enabled1 = factories.MailDomainEnabledFactory()
    domain_enabled2 = factories.MailDomainEnabledFactory()
    domain_disabled = factories.MailDomainFactory(
        status=enums.MailDomainStatusChoices.DISABLED
    )
    domain_failed = factories.MailDomainFactory(
        status=enums.MailDomainStatusChoices.FAILED
    )

    body_content_ok1 = CHECK_DOMAIN_OK.copy()
    body_content_ok1["name"] = domain_enabled1.name

    body_content_broken = CHECK_DOMAIN_BROKEN_INTERNAL.copy()
    body_content_broken["name"] = domain_enabled2.name

    body_content_ok2 = CHECK_DOMAIN_OK.copy()
    body_content_ok2["name"] = domain_disabled.name

    body_content_ok3 = CHECK_DOMAIN_OK.copy()
    body_content_ok3["name"] = domain_failed.name
    for domain, body_content in [
        (domain_enabled1, body_content_ok1),
        (domain_enabled2, body_content_broken),
        (domain_failed, body_content_ok3),
    ]:
        # Mock dimail API with success response
        responses.add(
            responses.GET,
            re.compile(rf".*/domains/{domain.name}/check/"),
            body=json.dumps(body_content),
            status=200,
            content_type="application/json",
        )
    # domain_enabled2 is broken with internal error, we try to fix it
    responses.add(
        responses.GET,
        re.compile(rf".*/domains/{domain_enabled2.name}/fix/"),
        body=json.dumps(body_content_broken),
        status=200,
        content_type="application/json",
    )
    tasks.fetch_domains_status_task(enums.MailDomainStatusChoices.ENABLED)
    tasks.fetch_domains_status_task(enums.MailDomainStatusChoices.FAILED)
    tasks.fetch_domains_status_task(enums.MailDomainStatusChoices.ACTION_REQUIRED)
    tasks.fetch_domains_status_task(enums.MailDomainStatusChoices.PENDING)
    domain_enabled1.refresh_from_db()
    domain_enabled2.refresh_from_db()
    domain_disabled.refresh_from_db()
    domain_failed.refresh_from_db()
    # Nothing change for the first domain enable
    assert domain_enabled1.status == enums.MailDomainStatusChoices.ENABLED
    # Status of the second activated domain has changed to failure
    assert domain_enabled2.status == enums.MailDomainStatusChoices.FAILED
    # Status of the failed domain has changed to enabled
    assert domain_failed.status == enums.MailDomainStatusChoices.ENABLED
    # Disabled domain was excluded
    assert domain_disabled.status == enums.MailDomainStatusChoices.DISABLED


@responses.activate
def test_fetch_domains_status_error_handling(caplog):
    """Test fetch domain status from dimail task with error"""
    caplog.set_level("ERROR")

    domain = factories.MailDomainEnabledFactory()

    # Mock dimail API with error response
    responses.add(
        responses.GET,
        re.compile(rf".*/domains/{domain.name}/check/"),
        body=json.dumps({"error": "Internal Server Error"}),
        status=500,
        content_type="application/json",
    )

    tasks.fetch_domains_status_task(enums.MailDomainStatusChoices.ENABLED)
    domain.refresh_from_db()

    # Domain status should remain unchanged
    assert domain.status == enums.MailDomainStatusChoices.ENABLED
    # Check that error was logged
    assert f"Failed to fetch status for domain {domain.name}" in caplog.text
