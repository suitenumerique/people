"""
Unit tests for mailbox manager tasks.
"""

import json
import re
from unittest import mock

from django.conf import settings
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.test import override_settings

import pytest
import responses

from mailbox_manager import enums, factories, tasks

from .fixtures.dimail import (
    CHECK_DOMAIN_BROKEN_EXTERNAL,
    CHECK_DOMAIN_BROKEN_INTERNAL,
    CHECK_DOMAIN_OK,
)

pytestmark = pytest.mark.django_db


@override_settings(MAIL_CHECK_DOMAIN_INTERVAL=0)
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
    domain_pending = factories.MailDomainFactory(
        status=enums.MailDomainStatusChoices.PENDING
    )

    body_content_ok1 = CHECK_DOMAIN_OK.copy()
    body_content_ok1["name"] = domain_enabled1.name

    body_content_broken_internal = CHECK_DOMAIN_BROKEN_INTERNAL.copy()
    body_content_broken_internal["name"] = domain_enabled2.name

    body_content_broken_external = CHECK_DOMAIN_BROKEN_EXTERNAL.copy()
    body_content_broken_external["name"] = domain_pending.name

    body_content_ok2 = CHECK_DOMAIN_OK.copy()
    body_content_ok2["name"] = domain_disabled.name

    body_content_ok3 = CHECK_DOMAIN_OK.copy()
    body_content_ok3["name"] = domain_failed.name
    for domain, body_content in [
        (domain_enabled1, body_content_ok1),
        (domain_enabled2, body_content_broken_internal),
        (domain_pending, body_content_broken_external),
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
        body=json.dumps(body_content_broken_internal),
        status=200,
        content_type="application/json",
    )
    with mock.patch("django.core.mail.send_mail") as mock_send:
        tasks.fetch_domains_status_task(enums.MailDomainStatusChoices.ENABLED)
        tasks.fetch_domains_status_task(enums.MailDomainStatusChoices.FAILED)
        tasks.fetch_domains_status_task(enums.MailDomainStatusChoices.ACTION_REQUIRED)
        tasks.fetch_domains_status_task(enums.MailDomainStatusChoices.PENDING)
    domain_enabled1.refresh_from_db()
    domain_enabled2.refresh_from_db()
    domain_disabled.refresh_from_db()
    domain_failed.refresh_from_db()
    domain_pending.refresh_from_db()
    # Nothing change for the first domain enable
    assert domain_enabled1.status == enums.MailDomainStatusChoices.ENABLED
    # Status of the second activated domain has changed to failure
    assert domain_enabled2.status == enums.MailDomainStatusChoices.FAILED
    # Status of the failed domain has changed to enabled
    assert domain_failed.status == enums.MailDomainStatusChoices.ENABLED
    # Disabled domain was excluded
    assert domain_disabled.status == enums.MailDomainStatusChoices.DISABLED
    # Pending domain has changed to action required
    assert domain_pending.status == enums.MailDomainStatusChoices.ACTION_REQUIRED

    # Check that the notification email was sent
    assert mock_send.call_count == 3
    domain_enabled2_context = {
        "title": "[La Suite] Your domain has failed",
        "domain_name": domain_enabled2.name,
        "manage_domain_url": (
            f"{Site.objects.get_current().domain}/mail-domains/{domain_enabled2.slug}/"
        ),
    }
    domain_pending_context = {
        "title": "[La Suite] Your domain requires action",
        "domain_name": domain_pending.name,
        "manage_domain_url": (
            f"{Site.objects.get_current().domain}/mail-domains/{domain_pending.slug}/"
        ),
    }
    domain_failed_context = {
        "title": "[La Suite] Your domain is ready",
        "domain_name": domain_failed.name,
        "manage_domain_url": (
            f"{Site.objects.get_current().domain}/mail-domains/{domain_failed.slug}/"
        ),
    }
    calls = [
        mock.call(
            "[La Suite] Your domain has failed",
            render_to_string(
                "mail/text/maildomain_failed.txt", domain_enabled2_context
            ),
            settings.EMAIL_FROM,
            [domain_enabled2.support_email],
            html_message=render_to_string(
                "mail/html/maildomain_failed.html", domain_enabled2_context
            ),
            fail_silently=False,
        ),
        mock.call(
            "[La Suite] Your domain requires action",
            render_to_string(
                "mail/text/maildomain_action_required.txt", domain_pending_context
            ),
            settings.EMAIL_FROM,
            [domain_pending.support_email],
            html_message=render_to_string(
                "mail/html/maildomain_action_required.html", domain_pending_context
            ),
            fail_silently=False,
        ),
        mock.call(
            "[La Suite] Your domain is ready",
            render_to_string("mail/text/maildomain_enabled.txt", domain_failed_context),
            settings.EMAIL_FROM,
            [domain_failed.support_email],
            html_message=render_to_string(
                "mail/html/maildomain_enabled.html", domain_failed_context
            ),
            fail_silently=False,
        ),
    ]
    mock_send.assert_has_calls(calls, any_order=True)


@override_settings(MAIL_CHECK_DOMAIN_INTERVAL=0)
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
