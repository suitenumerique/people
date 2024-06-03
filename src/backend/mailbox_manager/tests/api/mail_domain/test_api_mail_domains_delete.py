"""
Tests for MailDomains API endpoint, in People's mailbox manager app. Focus on "delete" action.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import factories, models

pytestmark = pytest.mark.django_db


def test_api_mail_domains__delete_anonymous():
    """Anonymous users should not be allowed to destroy a team."""
    domain = factories.MailDomainFactory()

    response = APIClient().delete(
        f"/api/v1.0/mail-domains/{domain.slug}/",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert models.MailDomain.objects.count() == 1


def test_api_mail_domains__delete_authenticated_unrelated():
    """
    Authenticated users should not be allowed to delete a domain to which they are not
    related.
    """
    identity = core_factories.IdentityFactory()
    domain = factories.MailDomainFactory()

    client = APIClient()
    client.force_login(identity.user)
    response = client.delete(
        f"/api/v1.0/mail-domains/{domain.slug}/",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No MailDomain matches the given query."}
    assert models.MailDomain.objects.count() == 1


def test_api_mail_domains__delete_authenticated_member():
    """
    Authenticated users should not be allowed to delete a domain
    to which they are only a member.
    """
    identity = core_factories.IdentityFactory()
    user = identity.user
    domain = factories.MailDomainFactory(users=[(user, "member")])

    client = APIClient()
    client.force_login(user)
    response = client.delete(
        f"/api/v1.0/mail-domains/{domain.slug}/",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "You do not have permission to perform this action."
    }
    assert models.MailDomain.objects.count() == 1


def test_api_mail_domains__delete_authenticated_administrator():
    """
    Authenticated users should not be allowed to delete a domain
    for which they are administrator.
    """
    identity = core_factories.IdentityFactory()
    user = identity.user
    domain = factories.MailDomainFactory(users=[(user, "administrator")])

    client = APIClient()
    client.force_login(user)
    response = client.delete(
        f"/api/v1.0/mail-domains/{domain.slug}/",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "You do not have permission to perform this action."
    }
    assert models.MailDomain.objects.count() == 1


def test_api_mail_domains__delete_authenticated_owner():
    """
    Authenticated users should be able to delete a domain
    for which they are directly owner.
    """
    identity = core_factories.IdentityFactory()
    user = identity.user
    domain = factories.MailDomainFactory(users=[(user, "owner")])

    client = APIClient()
    client.force_login(user)
    response = client.delete(
        f"/api/v1.0/mail-domains/{domain.slug}/",
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert models.MailDomain.objects.exists() is False
