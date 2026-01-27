"""
Tests for MailDomainInvitation API endpoint in People's app mailbox_manager.
Focus on "delete" action.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from mailbox_manager import factories, models

pytestmark = pytest.mark.django_db


def test_api_domain_invitations__delete__anonymous():
    """Anonymous users should not be able to delete invitations."""
    domain = factories.MailDomainEnabledFactory()
    invitation = factories.MailDomainInvitationFactory()

    response = APIClient().delete(
        f"/api/v1.0/mail-domains/{domain.slug}/invitations/{invitation.id}/",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }
    assert models.MailDomainInvitation.objects.count() == 1


def test_api_domain_invitations__delete__no_access_not_found():
    """Users should not be permitted to delete invitations
    on domains they don't manage."""
    domain = factories.MailDomainEnabledFactory()
    invitation = factories.MailDomainInvitationFactory()

    other_access = factories.MailDomainAccessFactory(role="owner")  # unrelated access
    client = APIClient()
    client.force_login(other_access.user)

    response = client.delete(
        f"/api/v1.0/mail-domains/{domain.slug}/invitations/{invitation.id}/",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert models.MailDomainInvitation.objects.count() == 1


def test_api_domain_invitations__delete__viewers_forbidden():
    """Domain viewers should not be permitted to delete invitations."""
    access = factories.MailDomainAccessFactory(role="viewer")
    invitation = factories.MailDomainInvitationFactory(domain=access.domain)

    client = APIClient()
    client.force_login(access.user)
    response = client.delete(
        f"/api/v1.0/mail-domains/{access.domain.slug}/invitations/{invitation.id}/",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert models.MailDomainInvitation.objects.count() == 1


@pytest.mark.parametrize(
    "role",
    ["owner", "administrator"],
)
def test_api_domain_invitations__delete_admins_ok(role):
    """Domain owners and admins should be able to delete invitations."""
    access = factories.MailDomainAccessFactory(role=role)
    invitation = factories.MailDomainInvitationFactory(domain=access.domain)

    client = APIClient()
    client.force_login(access.user)
    response = client.delete(
        f"/api/v1.0/mail-domains/{access.domain.slug}/invitations/{invitation.id}/",
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not models.MailDomainInvitation.objects.exists()
