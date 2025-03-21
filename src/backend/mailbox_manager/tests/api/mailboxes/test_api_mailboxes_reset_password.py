"""
Unit tests for the mailbox API
"""

import pytest
import responses
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories

pytestmark = pytest.mark.django_db


def test_api_mailboxes__reset_password_anonymous_unauthorized():
    """Anonymous users should not be able to reset mailboxes password."""
    mailbox = factories.MailboxFactory(status=enums.MailboxStatusChoices.ENABLED)
    response = APIClient().post(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/reset_password/",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_api_mailboxes__reset_password_unrelated_forbidden():
    """Authenticated users not managing the domain
    should not be able to reset its mailboxes password."""
    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    mailbox = factories.MailboxFactory(status=enums.MailboxStatusChoices.ENABLED)

    response = client.post(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/reset_password/"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "You do not have permission to perform this action."
    }


def test_api_mailboxes__reset_password_viewer_forbidden():
    """Domain viewers should not be able to reset passwords on mailboxes."""
    mailbox = factories.MailboxEnabledFactory()
    viewer_access = factories.MailDomainAccessFactory(
        role=enums.MailDomainRoleChoices.VIEWER, domain=mailbox.domain
    )

    client = APIClient()
    client.force_login(viewer_access.user)

    response = client.post(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/reset_password/"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "You do not have permission to perform this action."
    }


@pytest.mark.parametrize(
    "role",
    [
        enums.MailDomainRoleChoices.OWNER,
        enums.MailDomainRoleChoices.ADMIN,
    ],
)
@responses.activate
def test_api_mailboxes__reset_password_admin_successful(role):
    """Owner, admin and viewer users should be able to list mailboxes"""
    mail_domain = factories.MailDomainEnabledFactory()
    mailbox = factories.MailboxEnabledFactory(domain=mail_domain)

    access = factories.MailDomainAccessFactory(role=role, domain=mail_domain)
    client = APIClient()
    client.force_login(access.user)

    responses.add(
        responses.POST,
        f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/{mailbox.pk}/reset_password/",
        status=200,
    )
    response = client.post(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/{mailbox.pk}/reset_password/"
    )
    assert response.status_code == status.HTTP_200_OK
    # relevant to test if password has changed ?
    # or irrelevant because it's dimail's job ?


def test_api_mailboxes__reset_password_non_existing():
    """
    User gets a 404 when trying to reset password of mailboxes which does not exist.
    """
    user = core_factories.UserFactory()
    client = APIClient()
    client.force_login(user)

    response = client.get("/api/v1.0/mail-domains/nonexistent.domain/mailboxes/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
