"""Test the `fetch_domain_status_from_dimail` management command"""

import json
import re
from io import StringIO

from django.core.management import call_command

import pytest
import responses
from rest_framework import status

from mailbox_manager import enums, factories
from mailbox_manager.tests.fixtures.dimail import (
    CHECK_DOMAIN_BROKEN,
    CHECK_DOMAIN_OK,
)

pytestmark = pytest.mark.django_db


@responses.activate
def test_fetch_domain_status():
    """Test fetch domain status from dimail"""
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
        # mock dimail API
        responses.get(
            re.compile(rf".*/domains/{domain.name}/check/"),
            body=json.dumps(body_content),
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
    output = StringIO()
    call_command("fetch_domain_status", verbosity=2, stdout=output)
    domain_enabled1.refresh_from_db()
    domain_enabled2.refresh_from_db()
    domain_disabled.refresh_from_db()
    domain_failed.refresh_from_db()
    # nothing change for the first domain enable
    assert domain_enabled1.status == enums.MailDomainStatusChoices.ENABLED
    # status of the second activated domain has changed to action required
    assert domain_enabled2.status == enums.MailDomainStatusChoices.ACTION_REQUIRED
    # status of the failed domain has changed to enabled
    assert domain_failed.status == enums.MailDomainStatusChoices.ENABLED
    # disabled domain was excluded
    assert domain_disabled.status == enums.MailDomainStatusChoices.DISABLED
    assert output.getvalue().count("CHECKED") == 1
    assert output.getvalue().count("UPDATED") == 2
