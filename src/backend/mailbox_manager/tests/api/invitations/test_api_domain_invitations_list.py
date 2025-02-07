"""
Tests for DomainInvitations API endpoint in People's app mailbox_manager. Focus on "list" action.
"""

import time

from django.conf import settings

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories

pytestmark = pytest.mark.django_db


def test_api_domain_invitations__anonymous_user_should_not_list_invitations():
    """Anonymous users should not be able to list invitations."""
    domain = factories.MailDomainEnabledFactory()
    response = APIClient().get(f"/api/v1.0/mail-domains/{domain.slug}/invitations/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_api_domain_invitations__domain_managers_should_list_invitations():
    """
    Authenticated user should be able to list invitations
    in domains they manage, including from other issuers.
    """
    auth_user, other_user = core_factories.UserFactory.create_batch(2)
    domain = factories.MailDomainEnabledFactory()
    factories.MailDomainAccessFactory(
        domain=domain, user=auth_user, role=enums.MailDomainRoleChoices.ADMIN
    )
    factories.MailDomainAccessFactory(
        domain=domain, user=other_user, role=enums.MailDomainRoleChoices.OWNER
    )
    invitation = factories.DomainInvitationFactory(
        domain=domain, role=enums.MailDomainRoleChoices.ADMIN, issuer=auth_user
    )
    other_invitations = factories.DomainInvitationFactory.create_batch(
        2, domain=domain, role=enums.MailDomainRoleChoices.VIEWER, issuer=other_user
    )

    # expired invitations should be listed too
    # override settings to accelerate validation expiration
    settings.INVITATION_VALIDITY_DURATION = 1  # second
    expired_invitation = factories.DomainInvitationFactory(
        domain=domain, role=enums.MailDomainRoleChoices.VIEWER, issuer=auth_user
    )
    time.sleep(1)

    # invitations from other teams should not be listed
    other_domain = factories.MailDomainEnabledFactory()
    factories.DomainInvitationFactory.create_batch(
        2, domain=other_domain, role=enums.MailDomainRoleChoices.OWNER
    )

    client = APIClient()
    client.force_login(auth_user)
    response = client.get(
        f"/api/v1.0/mail-domains/{domain.slug}/invitations/",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 4
    assert sorted(response.json()["results"], key=lambda x: x["created_at"]) == sorted(
        [
            {
                "id": str(i.id),
                "created_at": i.created_at.isoformat().replace("+00:00", "Z"),
                "email": str(i.email),
                "domain": str(domain.id),
                "role": str(i.role),
                "issuer": str(i.issuer.id),
                "is_expired": i.is_expired,
            }
            for i in [invitation, *other_invitations, expired_invitation]
        ],
        key=lambda x: x["created_at"],
    )
