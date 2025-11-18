"""
Tests for MailDomainInvitations API endpoint in People's app mailbox_manager.
Focus on "create" action.
"""

from django.core import mail

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
    invitation_values = serializers.MailDomainInvitationSerializer(
        factories.MailDomainInvitationFactory.build()
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


def test_api_domain_invitations__create__no_access_forbidden_not_found():
    """Users should not be permitted to send domain management invitations
    for a domain they don't manage."""
    user = core_factories.UserFactory()
    domain = factories.MailDomainEnabledFactory()
    invitation_values = serializers.MailDomainInvitationSerializer(
        factories.MailDomainInvitationFactory.build()
    ).data

    client = APIClient()
    client.force_login(user)

    response = client.post(
        f"/api/v1.0/mail-domains/{domain.slug}/invitations/",
        invitation_values,
        format="json",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "role",
    ["owner", "administrator"],
)
def test_api_domain_invitations__admin_should_create_invites(role):
    """Owners and administrators should be able to invite new domain managers."""
    user = core_factories.UserFactory(language="fr-fr")
    domain = factories.MailDomainEnabledFactory()
    factories.MailDomainAccessFactory(domain=domain, user=user, role=role)

    invitation_values = serializers.MailDomainInvitationSerializer(
        factories.MailDomainInvitationFactory.build()
    ).data

    client = APIClient()
    client.force_login(user)

    assert len(mail.outbox) == 0

    response = client.post(
        f"/api/v1.0/mail-domains/{domain.slug}/invitations/",
        invitation_values,
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert email.to == [invitation_values["email"]]
    assert email.subject == "[La Suite] Vous avez été invité(e) à rejoindre la Régie"


def test_api_domain_invitations__no_access_forbidden_not_found():
    """
    Domain viewers should not be able to invite new domain managers.
    """
    user = core_factories.UserFactory()
    domain = factories.MailDomainEnabledFactory()
    factories.MailDomainAccessFactory(
        domain=domain, user=user, role=enums.MailDomainRoleChoices.VIEWER
    )

    invitation_values = serializers.MailDomainInvitationSerializer(
        factories.MailDomainInvitationFactory.build()
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
        "detail": "You do not have permission to perform this action."
    }


def test_api_domain_invitations__should_not_create_duplicate_invitations():
    """An email should not be invited multiple times to the same domain."""
    existing_invitation = factories.MailDomainInvitationFactory()
    domain = existing_invitation.domain

    # Grant privileged role on the domain to the user
    user = core_factories.UserFactory()
    factories.MailDomainAccessFactory(
        domain=domain, user=user, role=enums.MailDomainRoleChoices.OWNER
    )

    # Create a new invitation to the same domain with the exact same email address
    duplicated_invitation = serializers.MailDomainInvitationSerializer(
        factories.MailDomainInvitationFactory.build(email=existing_invitation.email)
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
        "Mail domain invitation with this Email address and Domain already exists."
    ]


def test_api_domain_invitations__should_not_invite_when_user_already_exists():
    """Already existing users should not be invited but given access directly."""
    existing_user = core_factories.UserFactory()

    # Grant privileged role on the domain to the user
    access = factories.MailDomainAccessFactory(role=enums.MailDomainRoleChoices.OWNER)

    client = APIClient()
    client.force_login(access.user)
    invitation_values = serializers.MailDomainInvitationSerializer(
        factories.MailDomainInvitationFactory.build(email=existing_user.email)
    ).data
    response = client.post(
        f"/api/v1.0/mail-domains/{access.domain.slug}/invitations/",
        invitation_values,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["email"] == [
        "This email is already associated to a registered user."
    ]
