"""
Unit tests for the mailbox API
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import factories, models

pytestmark = pytest.mark.django_db


def test_api_mailboxes__create_anonymous_forbidden():
    """Anonymous users should not be able to create a new mailbox via the API."""
    mail_domain = factories.MailDomainFactory()

    response = APIClient().post(
        f"/api/v1.0/mail-domains/{mail_domain.id}/mailboxes/",
        {
            "first_name": "jean",
            "last_name": "doe",
            "local_part": "jean.doe",
            "secondary_email": "jean.doe@gmail.com",
            "phone_number": "+33150142700",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not models.Mailbox.objects.exists()


def test_api_mailboxes__create_authenticated_missing_fields():
    """
    Authenticated users should not be able to create mailboxes
    without local part or secondary mail.
    """
    user = core_factories.UserFactory(admin_email="tester@ministry.fr")
    core_factories.IdentityFactory(user=user, email=user.admin_email, name="john doe")

    client = APIClient()
    client.force_login(user)

    mail_domain = factories.MailDomainFactory()
    response = client.post(
        f"/api/v1.0/mail-domains/{mail_domain.id}/mailboxes/",
        {
            "first_name": "jean",
            "last_name": "doe",
            "secondary_email": "jean.doe@gmail.com",
            "phone_number": "+33150142700",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert models.Mailbox.objects.exists() is False
    assert response.json() == {"local_part": ["This field is required."]}

    response = client.post(
        f"/api/v1.0/mail-domains/{mail_domain.id}/mailboxes/",
        {
            "first_name": "jean",
            "last_name": "doe",
            "local_part": "jean.doe",
            "phone_number": "+33150142700",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert models.Mailbox.objects.exists() is False
    assert response.json() == {"secondary_email": ["This field is required."]}


def test_api_mailboxes__create_authenticated_successful():
    """Authenticated users should be able to create mailbox."""
    user = core_factories.UserFactory(admin_email="tester@ministry.fr")
    core_factories.IdentityFactory(user=user, email=user.admin_email, name="john doe")

    client = APIClient()
    client.force_login(user)

    mail_domain = factories.MailDomainFactory(name="saint-jean.collectivite.fr")
    response = client.post(
        f"/api/v1.0/mail-domains/{mail_domain.id}/mailboxes/",
        {
            "first_name": "jean",
            "last_name": "doe",
            "local_part": "jean.doe",
            "secondary_email": "jean.doe@gmail.com",
            "phone_number": "+33150142700",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    mailbox = models.Mailbox.objects.get()
    assert mailbox.local_part == "jean.doe"
    assert mailbox.secondary_email == "jean.doe@gmail.com"
    assert response.json() == {
        "id": str(mailbox.id),
        "local_part": str(mailbox.local_part),
        "secondary_email": str(mailbox.secondary_email),
    }
