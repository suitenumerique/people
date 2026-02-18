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
    DOMAIN_SPEC,
    TOKEN_OK,
    response_mailbox_created,
)


@pytest.mark.parametrize(
    "domain_status",
    [
        enums.MailDomainStatusChoices.PENDING,
        enums.MailDomainStatusChoices.FAILED,
        enums.MailDomainStatusChoices.DISABLED,
    ],
)
@pytest.mark.django_db
def test_sync_mailboxes__should_not_sync_if_domain_is_not_enabled(
    domain_status, client
):
    """Mailboxes should not be sync'ed on non-enabled domains."""
    admin = core_factories.UserFactory(is_staff=True, is_superuser=True)
    client.force_login(admin)
    domain = factories.MailDomainFactory(status=domain_status)
    data = {
        "action": "sync_mailboxes_from_dimail",
        "_selected_action": [domain.id],
    }
    url = reverse("admin:mailbox_manager_maildomain_changelist")

    with responses.RequestsMock():
        # No call expected
        response = client.post(url, data, follow=True)
    assert response.status_code == status.HTTP_200_OK
    assert (
        f"Sync require enabled domains. Excluded domains: {domain}"
        in response.content.decode("utf-8")
    )


@responses.activate
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
    body_content_domain1 = CHECK_DOMAIN_BROKEN.copy()
    body_content_domain1["name"] = domain1.name
    body_content_domain2 = CHECK_DOMAIN_BROKEN.copy()
    body_content_domain2["name"] = domain2.name
    responses.add(
        responses.GET,
        re.compile(rf".*/domains/{domain1.name}/check/"),
        body=json.dumps(body_content_domain1),
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        re.compile(rf".*/domains/{domain2.name}/check/"),
        body=json.dumps(body_content_domain2),
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
    response = client.post(url, data, follow=True)
    assert response.status_code == status.HTTP_200_OK
    domain1.refresh_from_db()
    domain2.refresh_from_db()
    assert domain1.status == enums.MailDomainStatusChoices.ACTION_REQUIRED
    assert domain2.status == enums.MailDomainStatusChoices.ACTION_REQUIRED
    assert "Check domains done with success" in response.content.decode("utf-8")


@responses.activate
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

    body_content_domain1 = CHECK_DOMAIN_OK.copy()
    body_content_domain1["name"] = domain1.name

    responses.add(
        responses.GET,
        re.compile(rf".*/domains/{domain1.name}/check/"),
        body=json.dumps(body_content_domain1),
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
    # we need to get a token to create mailboxes
    responses.add(
        responses.GET,
        re.compile(r".*/token/"),
        body=TOKEN_OK,
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
    responses.add(
        responses.POST,
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


@pytest.mark.parametrize(
    "domain_status",
    [
        enums.MailDomainStatusChoices.PENDING,
        enums.MailDomainStatusChoices.FAILED,
        enums.MailDomainStatusChoices.ENABLED,
    ],
)
@responses.activate
@pytest.mark.django_db
def test_fetch_domain_expected_config(client, domain_status):
    """Test admin action to fetch domain expected config from dimail."""
    admin = core_factories.UserFactory(is_staff=True, is_superuser=True)
    client.force_login(admin)
    domain = factories.MailDomainFactory(status=domain_status)
    data = {
        "action": "fetch_domain_expected_config_from_dimail",
        "_selected_action": [domain.id],
    }
    responses.add(
        responses.GET,
        re.compile(rf".*/domains/{domain.name}/spec/"),
        body=json.dumps(DOMAIN_SPEC),
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
    url = reverse("admin:mailbox_manager_maildomain_changelist")
    response = client.post(url, data, follow=True)
    assert response.status_code == status.HTTP_200_OK
    domain.refresh_from_db()
    assert domain.expected_config == DOMAIN_SPEC


@pytest.mark.django_db
def test_fetch_domain_expected_config__should_not_fetch_for_disabled_domain(client):
    """Test admin action to fetch domain expected config from dimail."""
    admin = core_factories.UserFactory(is_staff=True, is_superuser=True)
    client.force_login(admin)
    domain = factories.MailDomainFactory(status=enums.MailDomainStatusChoices.DISABLED)
    data = {
        "action": "fetch_domain_expected_config_from_dimail",
        "_selected_action": [domain.id],
    }
    url = reverse("admin:mailbox_manager_maildomain_changelist")
    response = client.post(url, data, follow=True)
    assert response.status_code == status.HTTP_200_OK
    domain.refresh_from_db()
    assert domain.expected_config is None
    assert "Domains disabled are excluded from fetch" in response.content.decode(
        "utf-8"
    )


@responses.activate
@pytest.mark.django_db
def test_send_pending_mailboxes(client):
    """Test admin action to send pending mailboxes to dimail."""
    admin = core_factories.UserFactory(is_staff=True, is_superuser=True)
    client.force_login(admin)
    domain = factories.MailDomainFactory(status=enums.MailDomainStatusChoices.ENABLED)
    mailboxes = factories.MailboxFactory.create_batch(
        3, status=enums.MailboxStatusChoices.PENDING, domain=domain
    )
    data = {
        "action": "send_pending_mailboxes",
        "_selected_action": [domain.id],
    }

    url = reverse("admin:mailbox_manager_maildomain_changelist")
    for mailbox in mailboxes:
        responses.add(
            responses.GET,
            re.compile(r".*/token/"),
            body=TOKEN_OK,
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        responses.add(
            responses.POST,
            re.compile(rf".*/domains/{domain.name}/mailboxes/"),
            body=response_mailbox_created(f"{mailbox.local_part}@{domain.name}"),
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )
    response = client.post(url, data, follow=True)

    assert response.status_code == status.HTTP_200_OK
    for mailbox in mailboxes:
        mailbox.refresh_from_db()
        assert mailbox.status == enums.MailboxStatusChoices.ENABLED


@responses.activate
@pytest.mark.django_db
def test_send_pending_mailboxes__listing_failed_mailboxes(client):
    """Test admin action to send pending mailboxes to dimail."""
    admin = core_factories.UserFactory(is_staff=True, is_superuser=True)
    client.force_login(admin)
    domain = factories.MailDomainFactory(status=enums.MailDomainStatusChoices.ENABLED)
    mailbox = factories.MailboxFactory(
        status=enums.MailboxStatusChoices.PENDING, domain=domain
    )
    data = {
        "action": "send_pending_mailboxes",
        "_selected_action": [domain.id],
    }

    url = reverse("admin:mailbox_manager_maildomain_changelist")
    responses.add(
        responses.GET,
        re.compile(r".*/token/"),
        body=TOKEN_OK,
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
    responses.add(
        responses.POST,
        re.compile(rf".*/domains/{domain.name}/mailboxes/"),
        body=response_mailbox_created(f"{mailbox.local_part}@{domain.name}"),
        status=status.HTTP_409_CONFLICT,
        content_type="application/json",
    )
    response = client.post(url, data, follow=True)

    assert response.status_code == status.HTTP_200_OK
    assert (
        f"Failed to send the following mailboxes : {str(mailbox)}"
        in response.content.decode("utf-8")
    )
    mailbox.refresh_from_db()
    assert mailbox.status == enums.MailboxStatusChoices.PENDING


@pytest.mark.django_db
def test_export_domains_contact_list(client):
    """Test admin action to export."""

    admin = core_factories.UserFactory(is_staff=True, is_superuser=True)
    client.force_login(admin)

    domain = factories.MailDomainFactory(status=enums.MailDomainStatusChoices.ENABLED)
    owner = factories.MailDomainAccessFactory(domain=domain, role="owner")
    admin = factories.MailDomainAccessFactory(domain=domain, role="administrator")
    sorted_mails = sorted([owner.user.email, admin.user.email])

    data = {
        "action": "export_domains_contact_list",
        "_selected_action": [domain.id],
    }
    url = reverse("admin:mailbox_manager_maildomain_changelist")
    response = client.post(url, data, follow=True)

    domains_lines = response.content.decode("utf-8").split("\r\n")
    assert domains_lines == [
        "name,status,support_email,admins",
        f'{domain.name},{domain.status},{domain.support_email},"{", ".join(sorted_mails)}"',
        "",
    ]
