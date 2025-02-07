"""
Tests for DomainInvitations API endpoint. Focus on "retrieve" action.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories

pytestmark = pytest.mark.django_db


def test_api_domain_invitations__anonymous_user_should_not_retrieve_invitations():
    """
    Anonymous user should not be able to retrieve invitations.
    """

    invitation = factories.DomainInvitationFactory()
    response = APIClient().get(
        f"/api/v1.0/mail-domains/{invitation.domain.slug}/invitations/",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_api_domain_invitations__unrelated_user_should_not_retrieve_invitations():
    """
    Authenticated unrelated users should not be able to retrieve invitations.
    """
    auth_user = core_factories.UserFactory()
    invitation = factories.DomainInvitationFactory()

    client = APIClient()
    client.force_login(auth_user)

    response = client.get(
        f"/api/v1.0/mail-domains/{invitation.domain.slug}/invitations/",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 0


def test_api_domain_invitations__domain_managers_should_list_invitations():
    """
    Authenticated domain managers should be able to retrieve invitations
    whatever their role in the domain.
    """
    auth_user = core_factories.UserFactory()
    invitation = factories.DomainInvitationFactory()
    factories.MailDomainAccessFactory(
        domain=invitation.domain, user=auth_user, role=enums.MailDomainRoleChoices.ADMIN
    )

    client = APIClient()
    client.force_login(auth_user)
    response = client.get(
        f"/api/v1.0/mail-domains/{invitation.domain.slug}/invitations/{invitation.id}/",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(invitation.id),
        "created_at": invitation.created_at.isoformat().replace("+00:00", "Z"),
        "email": invitation.email,
        "domain": str(invitation.domain.id),
        "role": str(invitation.role),
        "issuer": str(invitation.issuer.id),
        "is_expired": False,
    }
