"""
Test for mail_domain accesses API endpoints in People's core app : retrieve
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories

pytestmark = pytest.mark.django_db


def test_api_mail_domain__accesses_retrieve_anonymous():
    """
    Anonymous users should not be allowed to retrieve a mail_domain access.
    """
    access = factories.MailDomainAccessFactory()

    response = APIClient().get(
        f"/api/v1.0/mail-domains/{access.domain.slug}/accesses/{access.id!s}/",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_mail_domain__accesses_retrieve_authenticated_unrelated():
    """
    Authenticated users should not be allowed to retrieve a mail_domain access for
    a mail_domain to which they are not related.
    """
    user = core_factories.UserFactory()
    access = factories.MailDomainAccessFactory(domain=factories.MailDomainFactory())

    client = APIClient()
    client.force_login(user)
    response = client.get(
        f"/api/v1.0/mail-domains/{access.domain.slug}/accesses/{access.id!s}/",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No MailDomain matches the given query."}

    # Accesses related to another mail_domain should be excluded even if the user is related to it
    for other_access in [
        factories.MailDomainAccessFactory(),
        factories.MailDomainAccessFactory(user=user),
    ]:
        response = client.get(
            f"/api/v1.0/mail-domains/{access.domain.slug}/accesses/{other_access.id!s}/",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "No MailDomain matches the given query."}


def test_api_mail_domain__accesses_retrieve_authenticated_related():
    """
    A user who is related to a mail_domain should be allowed to retrieve the
    associated mail_domain user accesses.
    """
    owner = core_factories.UserFactory()
    mail_domain = factories.MailDomainFactory()
    access = factories.MailDomainAccessFactory(
        domain=mail_domain, user=owner, role=enums.MailDomainRoleChoices.OWNER
    )

    client = APIClient()
    client.force_login(owner)
    response = client.get(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/accesses/{access.id!s}/",
    )

    results = {
        "id": str(access.id),
        "user": {
            "id": str(access.user.id),
            "email": str(owner.email),
            "name": str(owner.name),
        },
        "role": str(access.role),
        "can_set_role_to": [
            enums.MailDomainRoleChoices.ADMIN,
            enums.MailDomainRoleChoices.VIEWER,
        ],
    }
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == results

    admin = factories.MailDomainAccessFactory(
        domain=mail_domain, role=enums.MailDomainRoleChoices.ADMIN
    ).user
    client.force_login(admin)
    response = client.get(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/accesses/{access.id!s}/",
    )
    # admin can't change role of an owner
    results["can_set_role_to"] = []
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == results

    viewer = factories.MailDomainAccessFactory(
        domain=mail_domain, role=enums.MailDomainRoleChoices.VIEWER
    ).user
    client.force_login(viewer)
    response = client.get(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/accesses/{access.id!s}/",
    )
    # viewer can't change anyone's role
    results["can_set_role_to"] = []
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == results
