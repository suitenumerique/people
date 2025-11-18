"""
Tests for MailDomains API endpoint in People's mailbox manager app. Focus on "retrieve" action.
"""

import pytest
import responses
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories
from mailbox_manager.tests.fixtures import dimail as dimail_fixtures

pytestmark = pytest.mark.django_db


@responses.activate
def test_api_mail_domains__retrieve_anonymous():
    """Anonymous users should not be allowed to retrieve a domain."""

    domain = factories.MailDomainEnabledFactory()
    response = APIClient().get(f"/api/v1.0/mail-domains/{domain.slug}/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }
    # Verify no calls were made to dimail API
    assert len(responses.calls) == 0


@responses.activate
def test_api_domains__retrieve_non_existing():
    """
    Authenticated users should have an explicit error when trying to retrive
    a domain that doesn't exist.
    """
    client = APIClient()
    client.force_login(core_factories.UserFactory())

    response = client.get(
        "/api/v1.0/mail-domains/nonexistent.domain/",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Not found."}
    # Verify no calls were made to dimail API
    assert len(responses.calls) == 0


@responses.activate
def test_api_mail_domains__retrieve_authenticated_unrelated():
    """
    Authenticated users should not be allowed to retrieve a domain
    to which they have access.
    """
    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    domain = factories.MailDomainEnabledFactory()

    response = client.get(
        f"/api/v1.0/mail-domains/{domain.slug}/",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No MailDomain matches the given query."}


@responses.activate
def test_api_mail_domains__retrieve_authenticated_related_successful():
    """
    Authenticated users should be allowed to retrieve a domain
    to which they have access.
    """
    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    domain = factories.MailDomainEnabledFactory()
    factories.MailDomainAccessFactory(domain=domain, user=user)
    factories.MailboxFactory.create_batch(10, domain=domain)

    response = client.get(
        f"/api/v1.0/mail-domains/{domain.slug}/",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(domain.id),
        "name": domain.name,
        "slug": domain.slug,
        "status": domain.status,
        "created_at": domain.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": domain.updated_at.isoformat().replace("+00:00", "Z"),
        "abilities": domain.get_abilities(user),
        "count_mailboxes": 10,
        "support_email": domain.support_email,
        "last_check_details": None,
        "action_required_details": {},
        "expected_config": None,
    }


@responses.activate
def test_api_mail_domains__retrieve_authenticated_related_with_action_required():
    """
    Authenticated users should be allowed to retrieve a domain
    to which they have access and which has actions required to be done.
    """
    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    domain = factories.MailDomainFactory(
        status=enums.MailDomainStatusChoices.ACTION_REQUIRED,
        last_check_details=dimail_fixtures.CHECK_DOMAIN_BROKEN_EXTERNAL,
    )
    factories.MailDomainAccessFactory(domain=domain, user=user)

    response = client.get(
        f"/api/v1.0/mail-domains/{domain.slug}/",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(domain.id),
        "name": domain.name,
        "slug": domain.slug,
        "status": domain.status,
        "created_at": domain.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": domain.updated_at.isoformat().replace("+00:00", "Z"),
        "abilities": domain.get_abilities(user),
        "count_mailboxes": 0,
        "support_email": domain.support_email,
        "last_check_details": dimail_fixtures.CHECK_DOMAIN_BROKEN_EXTERNAL,
        "action_required_details": {
            "mx": "Je veux que le MX du domaine soit mx.ox.numerique.gouv.fr., "
            "or je trouve example-fr.mail.protection.outlook.com.",
        },
        "expected_config": None,
    }


@responses.activate
def test_api_mail_domains__retrieve_authenticated_related_with_ok_status():
    """
    Authenticated users should be allowed to retrieve a domain
    to which they have access and which has no actions required to be done.
    """
    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    domain = factories.MailDomainEnabledFactory(
        last_check_details=dimail_fixtures.CHECK_DOMAIN_OK,
    )
    factories.MailDomainAccessFactory(domain=domain, user=user)

    response = client.get(
        f"/api/v1.0/mail-domains/{domain.slug}/",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(domain.id),
        "name": domain.name,
        "slug": domain.slug,
        "status": domain.status,
        "created_at": domain.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": domain.updated_at.isoformat().replace("+00:00", "Z"),
        "abilities": domain.get_abilities(user),
        "count_mailboxes": 0,
        "support_email": domain.support_email,
        "last_check_details": dimail_fixtures.CHECK_DOMAIN_OK,
        "action_required_details": {},
        "expected_config": None,
    }


@responses.activate
def test_api_mail_domains__retrieve_authenticated_related_with_failed_status():
    """
    Authenticated users should be allowed to retrieve a domain
    to which they have access and which has failed status.
    """
    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    domain = factories.MailDomainFactory(
        status=enums.MailDomainStatusChoices.FAILED,
        last_check_details=dimail_fixtures.CHECK_DOMAIN_BROKEN_INTERNAL,
    )
    factories.MailDomainAccessFactory(domain=domain, user=user)

    response = client.get(
        f"/api/v1.0/mail-domains/{domain.slug}/",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(domain.id),
        "name": domain.name,
        "slug": domain.slug,
        "status": domain.status,
        "created_at": domain.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": domain.updated_at.isoformat().replace("+00:00", "Z"),
        "abilities": domain.get_abilities(user),
        "count_mailboxes": 0,
        "support_email": domain.support_email,
        "last_check_details": dimail_fixtures.CHECK_DOMAIN_BROKEN_INTERNAL,
        "action_required_details": {},
        "expected_config": None,
    }
