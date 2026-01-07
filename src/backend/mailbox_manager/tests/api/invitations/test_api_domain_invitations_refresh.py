"""
Tests for MailDomainInvitations API endpoint in People's app mailbox_manager.
Focus on "refresh" action.
"""

import pytest
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories, models

pytestmark = pytest.mark.django_db


def test_api_domain_invitations__anonymous_cannot_refresh():
    """Anonymous are not allowed to refresh."""
    invitation = factories.MailDomainInvitationFactory()
    response = APIClient().post(
        f"/api/v1.0/mail-domains/{invitation.domain.slug}/invitations/{invitation.id}/refresh/"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_api_domain_invitations__no_access_cannot_see_invitation():
    """Users with no permission on the domain should be returned a 404 not found."""
    invitation = factories.MailDomainInvitationFactory()

    otro_access = factories.MailDomainAccessFactory(
        role=enums.MailDomainRoleChoices.ADMIN
    )

    client = APIClient()
    client.force_login(otro_access.user)
    response = client.post(
        f"/api/v1.0/mail-domains/{invitation.domain.slug}/invitations/{invitation.id}/refresh/"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_api_domain_invitations__viewer_cannot_refresh():
    """Viewers cannot refresh invitations."""
    invitation = factories.MailDomainInvitationFactory()
    access = factories.MailDomainAccessFactory(
        domain=invitation.domain, role=enums.MailDomainRoleChoices.VIEWER
    )

    client = APIClient()
    client.force_login(access.user)
    response = client.post(
        f"/api/v1.0/mail-domains/{invitation.domain.slug}/invitations/{invitation.id}/refresh/"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_api_domain_invitations__admins_can_refresh_expired_invitations():
    """Admins can refresh invitations."""
    with freeze_time("2025-12-16"):
        invitation = factories.MailDomainInvitationFactory()

    access = factories.MailDomainAccessFactory(
        domain=invitation.domain, role=enums.MailDomainRoleChoices.OWNER
    )

    assert invitation.is_expired is True  # check invitation is correctly expired
    client = APIClient()
    client.force_login(access.user)
    # can refresh expired invitations
    response = client.post(
        f"/api/v1.0/mail-domains/{invitation.domain.slug}/invitations/{invitation.id}/refresh/"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_expired"] is False
    assert models.MailDomainInvitation.objects.count() == 1

    invitation.refresh_from_db()

    # can also refresh valid
    response = client.post(
        f"/api/v1.0/mail-domains/{invitation.domain.slug}/invitations/{invitation.id}/refresh/"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_expired"] is False
    assert models.MailDomainInvitation.objects.count() == 1


def test_api_domain_invitations__refreshing_invitation_can_convert_to_access():
    """In the event of someone creating their account after their invitation expired,
    said invitation has not been converted to access.
    We don't want to create a new invitation but create an access instead."""
    with freeze_time("2025-12-16"):
        invitation = factories.MailDomainInvitationFactory()
    core_factories.UserFactory(email=invitation.email)

    access = factories.MailDomainAccessFactory(
        domain=invitation.domain, role=enums.MailDomainRoleChoices.OWNER
    )
    client = APIClient()
    client.force_login(access.user)
    response = client.post(
        f"/api/v1.0/mail-domains/{invitation.domain.slug}/invitations/{invitation.id}/refresh/"
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert (
        response.json()["detail"]
        == "Email already known. Invitation not sent but access created instead."
    )
    assert models.MailDomainAccess.objects.count() == 2
    assert not models.MailDomainInvitation.objects.exists()
