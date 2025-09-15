"""
Tests for MailDomainInvitations API endpoint in People's app mailbox_manager.
Focus on "create" action.
"""

from django.core import mail

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories, models

pytestmark = pytest.mark.django_db


def test_api_domain_invitations__create__anonymous():
    """Anonymous users should not be able to create invitations."""
    domain = factories.MailDomainEnabledFactory()
    response = APIClient().post(
        f"/api/v1.0/mail-domains/{domain.slug}/invitations/",
        {
            "email": "some.email@domain.com",
            "role": "admin",
        },
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

    client = APIClient()
    client.force_login(user)
    response = client.post(
        f"/api/v1.0/mail-domains/{domain.slug}/invitations/",
        {
            "email": "some.email@domain.com",
            "role": "viewer",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "role",
    ["owner", "administrator"],
)
def test_api_domain_invitations__admin_should_create_invites(role):
    """Owners and administrators should be able to invite new domain managers."""
    user = core_factories.UserFactory(language="fr-fr")
    domain = factories.MailDomainEnabledFactory()
    factories.MailDomainAccessFactory(domain=domain, user=user, role=role)

    client = APIClient()
    client.force_login(user)
    assert len(mail.outbox) == 0
    response = client.post(
        f"/api/v1.0/mail-domains/{domain.slug}/invitations/",
        {
            "email": "some.email@domain.com",
            "role": "owner",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert email.to == ["some.email@domain.com"]
    assert email.subject == "[La Suite] Vous avez été invité(e) à rejoindre la Régie"


def test_api_domain_invitations__viewers_should_not_invite_to_manage_domains():
    """
    Domain viewers should not be able to invite new domain managers.
    """
    user = core_factories.UserFactory()
    domain = factories.MailDomainEnabledFactory()
    factories.MailDomainAccessFactory(
        domain=domain, user=user, role=enums.MailDomainRoleChoices.VIEWER
    )

    client = APIClient()
    client.force_login(user)
    response = client.post(
        f"/api/v1.0/mail-domains/{domain.slug}/invitations/",
        {
            "email": "some.email@domain.com",
            "role": "viewer",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "You are not allowed to manage invitations for this domain."
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

    # New invitation to the same domain with the exact same email address
    client = APIClient()
    client.force_login(user)
    response = client.post(
        f"/api/v1.0/mail-domains/{domain.slug}/invitations/",
        {
            "email": existing_invitation.email,
            "role": "owner",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["__all__"] == [
        "Mail domain invitation with this Email address and Domain already exists."
    ]
    assert models.MailDomainInvitation.objects.count() == 1  # and specifically, not 2


def test_api_domain_invitations__should_not_invite_when_user_already_exists():
    """Already existing users should not be invited but given access directly."""
    existing_user = core_factories.UserFactory()
    access = factories.MailDomainAccessFactory(role=enums.MailDomainRoleChoices.OWNER)

    client = APIClient()
    client.force_login(access.user)
    response = client.post(
        f"/api/v1.0/mail-domains/{access.domain.slug}/invitations/",
        {
            "email": existing_user.email,
            "role": "owner",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        "This email is already associated to a registered user. Access created."
    ]

    assert not models.MailDomainInvitation.objects.exists()
    assert models.MailDomainAccess.objects.filter(user=existing_user).exists()
