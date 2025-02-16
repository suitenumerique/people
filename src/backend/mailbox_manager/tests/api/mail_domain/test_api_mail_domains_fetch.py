"""
Tests for MailDomains API endpoint in People's mailbox manager app. Focus on "fetch" action.
"""

import json
import re

import pytest
import responses
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories
from mailbox_manager.tests.fixtures import dimail as dimail_fixtures

pytestmark = pytest.mark.django_db


@responses.activate
def test_api_mail_domains__fetch_from_dimail__anonymous():
    """
    Anonymous users should not be allowed to fetch a domain from dimail.
    """
    client = APIClient()

    domain = factories.MailDomainFactory()

    response = client.post(
        f"/api/v1.0/mail-domains/{domain.slug}/fetch/",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@responses.activate
def test_api_mail_domains__fetch_from_dimail__unrelated():
    """
    Authenticated users shouldn't be allowed to fetch
    a domain from dimail if they are not an owner or admin.
    """
    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    domain = factories.MailDomainFactory(
        status=enums.MailDomainStatusChoices.PENDING,
    )

    response = client.post(
        f"/api/v1.0/mail-domains/{domain.slug}/fetch/",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_api_mail_domains__fetch_from_dimail__viewer():
    """
    Authenticated users shouldn't be allowed to fetch a domain from dimail
    if they are a viewer.
    """
    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)
    access = factories.MailDomainAccessFactory(
        user=user,
        role=enums.MailDomainRoleChoices.VIEWER,
    )
    response = client.post(
        f"/api/v1.0/mail-domains/{access.domain.slug}/fetch/",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "role",
    [
        enums.MailDomainRoleChoices.ADMIN,
        enums.MailDomainRoleChoices.OWNER,
    ],
)
@responses.activate
def test_api_mail_domains__fetch_from_dimail(role):
    """
    Authenticated users should be allowed to fetch a domain
    from dimail if they are an owner or admin.
    """

    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    domain = factories.MailDomainFactory(
        status=enums.MailDomainStatusChoices.PENDING,
    )
    factories.MailDomainAccessFactory(
        domain=domain,
        user=user,
        role=role,
    )

    assert domain.expected_config is None
    assert domain.last_check_details is None

    responses.add(
        responses.GET,
        re.compile(rf".*/domains/{domain.name}/check/"),
        json=dimail_fixtures.CHECK_DOMAIN_OK,
        status=200,
    )
    responses.add(
        responses.GET,
        re.compile(rf".*/domains/{domain.name}/spec/"),
        json=dimail_fixtures.DOMAIN_SPEC,
        status=200,
    )

    response = client.post(
        f"/api/v1.0/mail-domains/{domain.slug}/fetch/",
    )

    domain.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(domain.id),
        "name": domain.name,
        "slug": domain.slug,
        "status": str(enums.MailDomainStatusChoices.ENABLED),
        "created_at": domain.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": domain.updated_at.isoformat().replace("+00:00", "Z"),
        "abilities": domain.get_abilities(user),
        "count_mailboxes": 0,
        "support_email": domain.support_email,
        "last_check_details": dimail_fixtures.CHECK_DOMAIN_OK,
        "action_required_details": {},
        "expected_config": dimail_fixtures.DOMAIN_SPEC,
    }
    assert domain.expected_config == dimail_fixtures.DOMAIN_SPEC
    assert domain.last_check_details == dimail_fixtures.CHECK_DOMAIN_OK
    assert domain.status == enums.MailDomainStatusChoices.ENABLED
