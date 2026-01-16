"""
Tests for MailDomainInvitations API endpoint in People's app mailbox_manager.
Focus on "refresh" action.
"""

import time

from django.conf import settings

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories

pytestmark = pytest.mark.django_db
from freezegun import freeze_time


def test_api_domain_invitations__anonymous_cannot_refresh():
    pass


def test_api_domain_invitations__viewer_cannot_refresh():
    pass


def test_api_domain_invitations__admins_can_refresh():
    """Admins can refresh expired invitations."""
    with freeze_time("2025-12-16"):
        existing_invitation = factories.MailDomainInvitationFactory()

    access = factories.MailDomainAccessFactory(
        domain=existing_invitation.domain, role=enums.MailDomainRoleChoices.OWNER
    )

    client = APIClient()
    client.force_login(access.user)
    response = client.post(
        f"/api/v1.0/mail-domains/{existing_invitation.domain.slug}/invitations/{existing_invitation.id}/refresh/",
        format="json",
    )
    import pdb

    pdb.set_trace()
    assert response.status_code == status.HTTP_200_OK
    assert existing_invitation.is_expired == False
    assert 1 == 2


def test_api_domain_invitations__cannot_refresh_valid_invitation():
    pass
