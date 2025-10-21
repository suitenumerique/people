"""
Tests for aliases API endpoint in People's app mailbox_manager.
Focus on "list" action.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories, models

pytestmark = pytest.mark.django_db


def test_api_aliases_delete__anonymous():
    """Anonymous user should not be able to delete aliases."""
    alias = factories.AliasFactory()

    response = APIClient().delete(
        f"/api/v1.0/mail-domains/{alias.domain.slug}/aliases/{alias.local_part}/",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert models.Alias.objects.count() == 1


def test_api_aliases_delete__no_access_forbidden():
    """
    Authenticated users should not be allowed to delete an alias in a
    mail domain to which they are not related.
    """
    authenticated_user = core_factories.UserFactory()
    alias = factories.AliasFactory()

    client = APIClient()
    client.force_login(authenticated_user)
    response = client.delete(
        f"/api/v1.0/mail-domains/{alias.domain.slug}/aliases/{alias.local_part}/",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert models.Alias.objects.count() == 1


def test_api_aliases_delete__viewer_forbidden():
    """
    Authenticated users should not be allowed to delete a mail domain access for a
    mail domain in which they are a simple viewer.
    """
    authenticated_user = core_factories.UserFactory()
    mail_domain = factories.MailDomainFactory(
        users=[(authenticated_user, enums.MailDomainRoleChoices.VIEWER)]
    )
    access = factories.MailDomainAccessFactory(domain=mail_domain)

    client = APIClient()
    client.force_login(authenticated_user)
    response = client.delete(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/accesses/{access.id!s}/",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert models.MailDomainAccess.objects.count() == 2
    assert models.MailDomainAccess.objects.filter(user=access.user).exists()
