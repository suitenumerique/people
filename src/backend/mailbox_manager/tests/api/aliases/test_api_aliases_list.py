"""
Tests for aliases API endpoint in People's app mailbox_manager.
Focus on "list" action.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories

pytestmark = pytest.mark.django_db


def test_api_aliases_list__anonymous():
    """Anonymous user should not be able to list aliases"""
    domain = factories.MailDomainEnabledFactory()
    factories.AliasFactory.create_batch(3, domain=domain)

    response = APIClient().get(
        f"/api/v1.0/mail-domains/{domain.slug}/aliases/",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_api_aliases_list__no_access_forbidden():
    """User authenticated but not having domain permission should not list aliases."""
    factories.MailDomainAccessFactory()  # access to another domain
    domain = factories.MailDomainEnabledFactory()
    factories.AliasFactory.create_batch(3, domain=domain)

    client = APIClient()
    client.force_login(core_factories.UserFactory())
    response = client.get(
        f"/api/v1.0/mail-domains/{domain.slug}/aliases/",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "role",
    [
        enums.MailDomainRoleChoices.OWNER,
        enums.MailDomainRoleChoices.ADMIN,
        enums.MailDomainRoleChoices.VIEWER,
    ],
)
def test_api_aliases_list__authorized_ok(role):
    """Domain viewers and admins should be able to list aliases."""
    access = factories.MailDomainAccessFactory(role=role)
    factories.AliasFactory.create_batch(2, local_part="support", domain=access.domain)
    factories.AliasFactory.create_batch(3, domain=access.domain)

    client = APIClient()
    client.force_login(access.user)
    response = client.get(
        f"/api/v1.0/mail-domains/{access.domain.slug}/aliases/",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 5
