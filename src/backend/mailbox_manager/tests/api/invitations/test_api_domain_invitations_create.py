"""
Tests for DomainInvitations API endpoint in People's app mailbox_manager. Focus on "create" action.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories
from mailbox_manager.api.client import serializers

pytestmark = pytest.mark.django_db


def test_api_domain_invitations__create__anonymous():
    """Anonymous users should not be able to create invitations."""
    domain = factories.MailDomainEnabledFactory()
    invitation_values = serializers.DomainInvitationSerializer(
        factories.DomainInvitationFactory.build()
    ).data

    response = APIClient().post(
        f"/api/v1.0/mail-domains/{domain.slug}/invitations/",
        invitation_values,
        format="json",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_domain_invitations__create__authenticated_outsider():
    """Users should not be permitted to send domain management invitations
    for a domain they don't manage."""
    user = core_factories.UserFactory()
    domain = factories.MailDomainEnabledFactory()
    invitation_values = serializers.DomainInvitationSerializer(
        factories.DomainInvitationFactory.build()
    ).data

    client = APIClient()
    client.force_login(user)

    response = client.post(
        f"/api/v1.0/mail-domains/{domain.slug}/invitations/",
        invitation_values,
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "role",
    ["owner", "administrator"],
)
def test_api_domain_invitations__admin_should_create_invites(role):
    """Owners and administrators should be able to invite new domain managers."""
    user = core_factories.UserFactory()
    domain = factories.MailDomainEnabledFactory()
    factories.MailDomainAccessFactory(domain=domain, user=user, role=role)

    invitation_values = serializers.DomainInvitationSerializer(
        factories.DomainInvitationFactory.build()
    ).data

    client = APIClient()
    client.force_login(user)

    response = client.post(
        f"/api/v1.0/mail-domains/{domain.slug}/invitations/",
        invitation_values,
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED


def test_api_domain_invitations__viewers_should_not_invite_to_manage_domains():
    """
    Domain viewers should not be able to invite new domain managers.
    """
    user = core_factories.UserFactory()
    domain = factories.MailDomainEnabledFactory()
    factories.MailDomainAccessFactory(
        domain=domain, user=user, role=enums.MailDomainRoleChoices.VIEWER
    )

    invitation_values = serializers.DomainInvitationSerializer(
        factories.DomainInvitationFactory.build()
    ).data

    client = APIClient()
    client.force_login(user)

    response = client.post(
        f"/api/v1.0/mail-domains/{domain.slug}/invitations/",
        invitation_values,
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "You are not allowed to manage invitations for this domain."
    }


def test_api_domain_invitations__should_not_create_duplicate_invitations():
    """An email should not be invited multiple times to the same domain."""
    existing_invitation = factories.DomainInvitationFactory()
    domain = existing_invitation.domain

    # Grant privileged role on the domain to the user
    user = core_factories.UserFactory()
    factories.MailDomainAccessFactory(
        domain=domain, user=user, role=enums.MailDomainRoleChoices.OWNER
    )

    # Create a new invitation to the same domain with the exact same email address
    duplicated_invitation = serializers.DomainInvitationSerializer(
        factories.DomainInvitationFactory.build(email=existing_invitation.email)
    ).data

    client = APIClient()
    client.force_login(user)
    response = client.post(
        f"/api/v1.0/mail-domains/{domain.slug}/invitations/",
        duplicated_invitation,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["__all__"] == [
        "Domain invitation with this Email address and Domain already exists."
    ]
