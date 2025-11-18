"""
Test for mail_domain accesses API endpoints in People's core app : delete
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories, models

pytestmark = pytest.mark.django_db


def test_api_domain_accesses_delete__anonymous_forbidden():
    """Anonymous users should not be allowed to destroy a mail domain access."""
    access = factories.MailDomainAccessFactory()

    response = APIClient().delete(
        f"/api/v1.0/mail-domains/{access.domain.slug}/accesses/{access.id!s}/",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert models.MailDomainAccess.objects.count() == 1


def test_api_domain_accesses_delete__unrelated_notfound():
    """
    Authenticated users should not be allowed to delete a mail domain access for a
    mail domain to which they are not related.
    """
    authenticated_user = core_factories.UserFactory()
    access = factories.MailDomainAccessFactory()

    client = APIClient()
    client.force_login(authenticated_user)
    response = client.delete(
        f"/api/v1.0/mail-domains/{access.domain.slug}/accesses/{access.id!s}/",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert models.MailDomainAccess.objects.count() == 1


def test_api_domain_accesses_delete__viewer_forbidden():
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


def test_api_domain_accesses_delete__administrators_successful():
    """
    Administrators of a mail domain should be allowed to delete accesses excepted owner accesses.
    """
    authenticated_user = core_factories.UserFactory()
    mail_domain = factories.MailDomainFactory(
        users=[(authenticated_user, enums.MailDomainRoleChoices.ADMIN)]
    )
    for role in [enums.MailDomainRoleChoices.VIEWER, enums.MailDomainRoleChoices.ADMIN]:
        access = factories.MailDomainAccessFactory(domain=mail_domain, role=role)

        assert models.MailDomainAccess.objects.count() == 2
        assert models.MailDomainAccess.objects.filter(user=access.user).exists()

        client = APIClient()
        client.force_login(authenticated_user)
        response = client.delete(
            f"/api/v1.0/mail-domains/{mail_domain.slug}/accesses/{access.id!s}/",
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert models.MailDomainAccess.objects.count() == 1


def test_api_domain_accesses_delete__owners_successful():
    """
    An owner should be able to delete the mail domain access of another user including
    a owner access.
    """
    authenticated_user = core_factories.UserFactory()
    mail_domain = factories.MailDomainFactory(
        users=[(authenticated_user, enums.MailDomainRoleChoices.OWNER)]
    )
    for role in [role[0] for role in enums.MailDomainRoleChoices.choices]:
        access = factories.MailDomainAccessFactory(domain=mail_domain, role=role)

        assert models.MailDomainAccess.objects.count() == 2
        assert models.MailDomainAccess.objects.filter(user=access.user).exists()

        client = APIClient()
        client.force_login(authenticated_user)
        response = client.delete(
            f"/api/v1.0/mail-domains/{mail_domain.slug}/accesses/{access.id!s}/",
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert models.MailDomainAccess.objects.count() == 1


def test_api_domain_accesses_delete__last_owner_forbidden():
    """
    It should not be possible to delete the last owner access from a mail domain
    """
    authenticated_user = core_factories.UserFactory()
    mail_domain = factories.MailDomainFactory()
    access = factories.MailDomainAccessFactory(
        domain=mail_domain,
        user=authenticated_user,
        role=enums.MailDomainRoleChoices.OWNER,
    )
    factories.MailDomainAccessFactory.create_batch(9)
    assert models.MailDomainAccess.objects.count() == 10

    client = APIClient()
    client.force_login(authenticated_user)

    response = client.delete(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/accesses/{access.id!s}/",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert models.MailDomainAccess.objects.count() == 10
