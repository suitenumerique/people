"""
Tests for aliases API endpoint in People's app mailbox_manager.
Focus on "list" action.
"""

import re

import pytest
import responses
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
    Authenticated users should not be allowed to delete aliases for a
    mail domain in which they are a simple viewer.
    """
    authenticated_user = core_factories.UserFactory()
    mail_domain = factories.MailDomainFactory(
        users=[(authenticated_user, enums.MailDomainRoleChoices.VIEWER)]
    )
    alias = factories.AliasFactory(domain=mail_domain)

    client = APIClient()
    client.force_login(authenticated_user)
    response = client.delete(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/aliases/{alias.local_part}/",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert models.Alias.objects.count() == 1


def test_api_aliases_delete__viewer_can_delete_self_alias():
    """
    Authenticated users should be allowed to delete aliases when linking
    to their own mailbox.
    """
    authenticated_user = core_factories.UserFactory()
    mail_domain = factories.MailDomainFactory(
        users=[(authenticated_user, enums.MailDomainRoleChoices.VIEWER)]
    )
    alias = factories.AliasFactory(
        domain=mail_domain, destination=authenticated_user.email
    )

    client = APIClient()
    client.force_login(authenticated_user)
    response = client.delete(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/aliases/{alias.local_part}/",
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not models.Alias.objects.exists()


@responses.activate
def test_api_aliases_delete__administrators_allowed():
    """
    Administrators of a mail domain should be allowed to delete accesses excepted owner accesses.
    """
    authenticated_user = core_factories.UserFactory()
    mail_domain = factories.MailDomainFactory(
        users=[(authenticated_user, enums.MailDomainRoleChoices.ADMIN)]
    )
    alias = factories.AliasFactory(domain=mail_domain)

    # Mock dimail response
    responses.add(
        responses.POST,
        re.compile(r".*/aliases/"),
        status=status.HTTP_204_NO_CONTENT,
        content_type="application/json",
    )

    client = APIClient()
    client.force_login(authenticated_user)
    response = client.delete(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/aliases/{alias.local_part}/",
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not models.Alias.objects.exists()
