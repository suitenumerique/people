"""
Tests for mailbox Aliases API endpoint in People's app mailbox_manager.
Focus on "create" action.
"""

import json
import re

import pytest
import responses
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories, models
from mailbox_manager.tests.fixtures.dimail import TOKEN_OK

pytestmark = pytest.mark.django_db


def test_api_aliases_create__anonymous():
    """Anonymous user should not create aliases"""
    domain = factories.MailDomainEnabledFactory()

    response = APIClient().post(
        f"/api/v1.0/mail-domains/{domain.slug}/aliases/",
        {"whatever": "this should not be updated"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not models.Alias.objects.exists()


def test_api_aliases_create__no_access_forbidden():
    """User authenticated but not having domain permission should not create aliases."""
    domain = factories.MailDomainEnabledFactory()

    client = APIClient()
    client.force_login(core_factories.UserFactory())
    response = client.post(
        f"/api/v1.0/mail-domains/{domain.slug}/aliases/",
        {"local_part": "intrusive", "destination": "intrusive@mail.com"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not models.Alias.objects.exists()


def test_api_aliases_create__viewer_forbidden():
    """Domain viewers should not create aliases."""
    domain = factories.MailDomainEnabledFactory()
    access = factories.MailDomainAccessFactory(role="viewer", domain=domain)

    client = APIClient()
    client.force_login(access.user)
    response = client.post(
        f"/api/v1.0/mail-domains/{domain.slug}/aliases/",
        {"local_part": "intrusive", "destination": "intrusive@mail.com"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not models.Alias.objects.exists()


def test_api_aliases_create__duplicate_forbidden():
    """Cannot create alias if same local part + destination."""
    access = factories.MailDomainAccessFactory(
        role="owner", domain=factories.MailDomainEnabledFactory()
    )

    existing_alias = factories.AliasFactory(domain=access.domain)
    client = APIClient()
    client.force_login(access.user)
    response = client.post(
        f"/api/v1.0/mail-domains/{access.domain.slug}/aliases/",
        {
            "local_part": existing_alias.local_part,
            "destination": existing_alias.destination,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert models.Alias.objects.filter(domain=access.domain).count() == 1


def test_api_aliases_create__existing_mailbox_bad_request():
    """Cannot create alias if local_part is already used by a mailbox."""
    access = factories.MailDomainAccessFactory(
        role="owner", domain=factories.MailDomainEnabledFactory()
    )
    mailbox = factories.MailboxFactory(domain=access.domain)

    client = APIClient()
    client.force_login(access.user)
    response = client.post(
        f"/api/v1.0/mail-domains/{access.domain.slug}/aliases/",
        {"local_part": mailbox.local_part, "destination": "someone@outsidedomain.com"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not models.Alias.objects.exists()


@responses.activate
@pytest.mark.parametrize(
    "role",
    [enums.MailDomainRoleChoices.OWNER, enums.MailDomainRoleChoices.ADMIN],
)
def test_api_aliases_create__admins_ok(role):
    """Domain admins should be able to create aliases."""
    access = factories.MailDomainAccessFactory(role=role)

    client = APIClient()
    client.force_login(access.user)
    # Prepare responses
    responses.add(
        responses.GET,
        re.compile(r".*/token/"),
        body=TOKEN_OK,
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
    responses.add(
        responses.POST,
        re.compile(rf".*/domains/{access.domain.name}/aliases/"),
        body=json.dumps(
            {
                "username": "contact",
                "domain": access.domain.name,
                "destination": "someone@outsidedomain.com",
                "allow_to_send": True,
            }
        ),
        status=status.HTTP_201_CREATED,
        content_type="application/json",
    )

    response = client.post(
        f"/api/v1.0/mail-domains/{access.domain.slug}/aliases/",
        {"local_part": "contact", "destination": "someone@outsidedomain.com"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    alias = models.Alias.objects.get()
    assert alias.local_part == "contact"
    assert alias.destination == "someone@outsidedomain.com"
