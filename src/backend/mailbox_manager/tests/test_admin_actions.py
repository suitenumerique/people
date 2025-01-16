"""
Unit tests for admin actions
"""

import json
import re

from django.urls import reverse

import pytest
import responses
from rest_framework import status

from core import factories as core_factories

from mailbox_manager import enums, factories, models

from .fixtures.dimail import (
    CHECK_DOMAIN_BROKEN,
    CHECK_DOMAIN_OK,
    TOKEN_OK,
    response_mailbox_created,
)


@pytest.mark.django_db
def test_fetch_domain_status__should_switch_to_failed_when_domain_broken(client):
    """Test admin action to check health of some domains"""
    admin = core_factories.UserFactory(is_staff=True, is_superuser=True)
    client.force_login(admin)
    domain1 = factories.MailDomainEnabledFactory()
    domain2 = factories.MailDomainEnabledFactory()
    data = {
        "action": "fetch_domain_status_from_dimail",
        "_selected_action": [
            domain1.id,
            domain2.id,
        ],
    }
    url = reverse("admin:mailbox_manager_maildomain_changelist")

    with responses.RequestsMock() as rsps:
        body_content_domain1 = CHECK_DOMAIN_BROKEN.copy()
        body_content_domain1["name"] = domain1.name
        body_content_domain2 = CHECK_DOMAIN_BROKEN.copy()
        body_content_domain2["name"] = domain2.name
        rsps.add(
            rsps.GET,
            re.compile(rf".*/domains/{domain1.name}/check/"),
            body=json.dumps(body_content_domain1),
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        rsps.add(
            rsps.GET,
            re.compile(rf".*/domains/{domain2.name}/check/"),
            body=json.dumps(body_content_domain2),
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        response = client.post(url, data, follow=True)
        assert response.status_code == status.HTTP_200_OK
        domain1.refresh_from_db()
        domain2.refresh_from_db()
        assert domain1.status == enums.MailDomainStatusChoices.FAILED
        assert domain2.status == enums.MailDomainStatusChoices.FAILED
        assert "Check domains done with success" in response.content.decode("utf-8")


@pytest.mark.django_db
def test_fetch_domain_status__should_switch_to_enabled_when_domain_ok(client):
    """Test admin action should switch domain state to ENABLED
    when dimail's response is "ok". It should also activate any pending mailbox."""
    admin = core_factories.UserFactory(is_staff=True, is_superuser=True)
    client.force_login(admin)
    domain1 = factories.MailDomainFactory()
    factories.MailboxFactory.create_batch(3, domain=domain1)

    domain2 = factories.MailDomainFactory()
    data = {
        "action": "fetch_domain_status_from_dimail",
        "_selected_action": [domain1.id],
    }
    url = reverse("admin:mailbox_manager_maildomain_changelist")

    with responses.RequestsMock() as rsps:
        body_content_domain1 = CHECK_DOMAIN_OK.copy()
        body_content_domain1["name"] = domain1.name

        rsps.add(
            rsps.GET,
            re.compile(rf".*/domains/{domain1.name}/check/"),
            body=json.dumps(body_content_domain1),
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        rsps.add(
            rsps.GET,
            re.compile(r".*/token/"),
            body=TOKEN_OK,
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(rf".*/domains/{domain1.name}/mailboxes/"),
            body=response_mailbox_created(f"truc@{domain1.name}"),
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )

        response = client.post(url, data, follow=True)
    assert response.status_code == status.HTTP_200_OK
    domain1.refresh_from_db()
    domain2.refresh_from_db()
    assert domain1.status == enums.MailDomainStatusChoices.ENABLED
    assert domain2.status == enums.MailDomainStatusChoices.PENDING
    assert "Check domains done with success" in response.content.decode("utf-8")
    for mailbox in models.Mailbox.objects.filter(domain=domain1):
        assert mailbox.status == enums.MailboxStatusChoices.ENABLED
