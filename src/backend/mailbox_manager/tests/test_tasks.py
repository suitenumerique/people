"""
Unit tests for mailbox manager tasks.
"""

import json
import re
from unittest import mock

from django.conf import settings

import pytest
import responses

from mailbox_manager import enums, factories, tasks

from .fixtures.dimail import CHECK_DOMAIN_BROKEN, CHECK_DOMAIN_OK

pytestmark = pytest.mark.django_db


@responses.activate
def test_fetch_domain_status_task_success():  # pylint: disable=too-many-locals
    """Test fetch domain status from dimail task"""

    domain_enabled1 = factories.MailDomainEnabledFactory()
    domain_enabled2 = factories.MailDomainEnabledFactory()
    owner_domain_enabled2 = factories.MailDomainAccessFactory(
        domain=domain_enabled2, role=enums.MailDomainRoleChoices.OWNER
    ).user
    admin_domain_enabled2 = factories.MailDomainAccessFactory(
        domain=domain_enabled2, role=enums.MailDomainRoleChoices.ADMIN
    ).user
    domain_disabled = factories.MailDomainFactory(
        status=enums.MailDomainStatusChoices.DISABLED
    )
    domain_failed = factories.MailDomainFactory(
        status=enums.MailDomainStatusChoices.FAILED
    )
    owner_domain_failed = factories.MailDomainAccessFactory(
        domain=domain_failed, role=enums.MailDomainRoleChoices.OWNER
    ).user
    admin_domain_failed = factories.MailDomainAccessFactory(
        domain=domain_failed, role=enums.MailDomainRoleChoices.ADMIN
    ).user
    body_content_ok1 = CHECK_DOMAIN_OK.copy()
    body_content_ok1["name"] = domain_enabled1.name

    body_content_broken = CHECK_DOMAIN_BROKEN.copy()
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
    with mock.patch("django.core.mail.send_mail") as mock_send:
        tasks.fetch_domains_status()
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
    # Check notification was sent to owners and admins
    assert mock_send.call_count == 4
    calls = [
        mock.call(
            "Domain status changed",
            f"Domain {domain_enabled2.name} is down",
            settings.DEFAULT_FROM_EMAIL,
            [owner_domain_enabled2.email],
        ),
        mock.call(
            "Domain status changed",
            f"Domain {domain_enabled2.name} is down",
            settings.DEFAULT_FROM_EMAIL,
            [admin_domain_enabled2.email],
        ),
        mock.call(
            "Domain status changed",
            f"Domain {domain_failed.name} is up",
            settings.DEFAULT_FROM_EMAIL,
            [owner_domain_failed.email],
        ),
        mock.call(
            "Domain status changed",
            f"Domain {domain_failed.name} is up",
            settings.DEFAULT_FROM_EMAIL,
            [admin_domain_failed.email],
        ),
    ]
    mock_send.assert_has_calls(calls, any_order=True)
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

    tasks.fetch_domains_status()
    domain.refresh_from_db()

    # Domain status should remain unchanged
    assert domain.status == enums.MailDomainStatusChoices.ENABLED
    # Check that error was logged
    assert f"Failed to fetch status for domain {domain.name}" in caplog.text
