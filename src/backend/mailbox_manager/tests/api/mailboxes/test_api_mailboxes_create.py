"""
Unit tests for the mailbox API
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories, models
from mailbox_manager.api import serializers

pytestmark = pytest.mark.django_db


def test_api_mailboxes__create_anonymous_forbidden():
    """Anonymous users should not be able to create a new mailbox via the API."""
    mail_domain = factories.MailDomainEnabledFactory()
    mailbox_values = serializers.MailboxSerializer(
        factories.MailboxFactory.build()
    ).data
    response = APIClient().post(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/",
        mailbox_values,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not models.Mailbox.objects.exists()


def test_api_mailboxes__create_authenticated_failure():
    """Authenticated users should not be able to create mailbox
    without specific role on mail domain."""
    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    mailbox_values = serializers.MailboxSerializer(
        factories.MailboxFactory.build()
    ).data
    mail_domain = factories.MailDomainEnabledFactory()
    response = client.post(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/",
        mailbox_values,
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not models.Mailbox.objects.exists()


def test_api_mailboxes__create_viewer_failure():
    """Users with viewer role should not be able to create mailbox on the mail domain."""
    mail_domain = factories.MailDomainEnabledFactory()
    access = factories.MailDomainAccessFactory(
        role=enums.MailDomainRoleChoices.VIEWER, domain=mail_domain
    )

    client = APIClient()
    client.force_login(access.user)

    mailbox_values = serializers.MailboxSerializer(
        factories.MailboxFactory.build()
    ).data
    response = client.post(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/",
        mailbox_values,
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not models.Mailbox.objects.exists()


@pytest.mark.parametrize(
    "role",
    [
        enums.MailDomainRoleChoices.OWNER,
        enums.MailDomainRoleChoices.ADMIN,
    ],
)
def test_api_mailboxes__create_roles_success(role):
    """Users with owner or admin role should be able to create mailbox on the mail domain."""
    mail_domain = factories.MailDomainEnabledFactory()
    access = factories.MailDomainAccessFactory(role=role, domain=mail_domain)

    client = APIClient()
    client.force_login(access.user)

    mailbox_values = serializers.MailboxSerializer(
        factories.MailboxFactory.build()
    ).data
    response = client.post(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/",
        mailbox_values,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    mailbox = models.Mailbox.objects.get()

    assert mailbox.local_part == mailbox_values["local_part"]
    assert mailbox.secondary_email == mailbox_values["secondary_email"]
    assert response.json() == {
        "id": str(mailbox.id),
        "first_name": str(mailbox.first_name),
        "last_name": str(mailbox.last_name),
        "local_part": str(mailbox.local_part),
        "secondary_email": str(mailbox.secondary_email),
    }


@pytest.mark.parametrize(
    "role",
    [
        enums.MailDomainRoleChoices.OWNER,
        enums.MailDomainRoleChoices.ADMIN,
    ],
)
def test_api_mailboxes__create_with_accent_success(role):
    """Users with proper abilities should be able to create mailbox on the mail domain with a
    first_name accentuated."""
    mail_domain = factories.MailDomainEnabledFactory()
    access = factories.MailDomainAccessFactory(role=role, domain=mail_domain)

    client = APIClient()
    client.force_login(access.user)

    mailbox_values = serializers.MailboxSerializer(
        factories.MailboxFactory.build(first_name="Aimé")
    ).data
    response = client.post(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/",
        mailbox_values,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    mailbox = models.Mailbox.objects.get()

    assert mailbox.local_part == mailbox_values["local_part"]
    assert mailbox.secondary_email == mailbox_values["secondary_email"]
    assert response.json() == {
        "id": str(mailbox.id),
        "first_name": str(mailbox.first_name),
        "last_name": str(mailbox.last_name),
        "local_part": str(mailbox.local_part),
        "secondary_email": str(mailbox.secondary_email),
    }


def test_api_mailboxes__create_administrator_missing_fields():
    """
    Administrator users should not be able to create mailboxes
    without local part or secondary mail.
    """
    mail_domain = factories.MailDomainEnabledFactory()
    access = factories.MailDomainAccessFactory(
        role=enums.MailDomainRoleChoices.ADMIN, domain=mail_domain
    )
    client = APIClient()
    client.force_login(access.user)

    mailbox_values = serializers.MailboxSerializer(
        factories.MailboxFactory.build()
    ).data
    del mailbox_values["local_part"]
    response = client.post(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/",
        mailbox_values,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not models.Mailbox.objects.exists()
    assert response.json() == {"local_part": ["This field is required."]}

    mailbox_values = serializers.MailboxSerializer(
        factories.MailboxFactory.build()
    ).data
    del mailbox_values["secondary_email"]
    response = client.post(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/",
        mailbox_values,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not models.Mailbox.objects.exists()
    assert response.json() == {"secondary_email": ["This field is required."]}
