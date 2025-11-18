"""
Unit tests for the mailbox API
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories

pytestmark = pytest.mark.django_db


def test_api_mailboxes_patch__anonymous_forbidden():
    """Anonymous users should not be able to update a mailbox."""
    mailbox = factories.MailboxFactory()
    saved_secondary = mailbox.secondary_email

    response = APIClient().patch(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/",
        {"secondary_email": "updated@example.com"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    mailbox.refresh_from_db()
    assert mailbox.secondary_email == saved_secondary


def test_api_mailboxes_patch__no_access_forbidden_not_found():
    """Authenticated but unauthoriezd users should not be able to update mailboxes."""
    mailbox = factories.MailboxFactory()
    saved_secondary = mailbox.secondary_email

    client = APIClient()
    client.force_login(core_factories.UserFactory())
    response = client.patch(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.local_part}/",
        {"secondary_email": "updated@example.com"},
        format="json",
    )
    # permission denied at domain level
    assert response.status_code == status.HTTP_404_NOT_FOUND
    mailbox.refresh_from_db()
    assert mailbox.secondary_email == saved_secondary


def test_api_mailboxes_patch__viewer_forbidden():
    """User having viewer access on a domain should not be able to update
    anything on a mailbox that's not theirs."""
    viewer = core_factories.UserFactory()
    mailbox = factories.MailboxFactory()
    factories.MailDomainAccessFactory(
        user=viewer,
        domain=mailbox.domain,
        role=enums.MailDomainRoleChoices.VIEWER,
    )

    client = APIClient()
    client.force_login(viewer)

    # should not be able to update any field
    # we only try one field as 403 is global in our implementation
    old_value = mailbox.secondary_email
    response = client.patch(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/",
        {"secondary_email": "updated@example.com"},
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mailbox.refresh_from_db()
    assert mailbox.secondary_email == old_value


def test_api_mailboxes_patch__unauthorized_no_mailbox():
    """No mailbox returns a 404."""
    access = factories.MailDomainAccessFactory(role=enums.MailDomainRoleChoices.ADMIN)

    client = APIClient()
    client.force_login(access.user)
    response = client.patch(
        f"/api/v1.0/mail-domains/{access.domain.slug}/mailboxes/nonexistent_mailbox_pk/",
        {"secondary_email": "updated@example.com"},
        format="json",
    )

    # permission denied at domain level
    # the existence of the mailbox is not checked
    assert response.status_code == status.HTTP_404_NOT_FOUND


# UPDATABLE FIELDS : SECONDARY EMAIL FIRST NAME AND LAST NAME
@pytest.mark.parametrize(
    "role",
    ["owner", "administrator"],
)
def test_api_mailboxes_patch__admins_can_update_mailboxes(role):
    """Domain owners and admins should be allowed to update secondary email on a mailbox"""
    mailbox = factories.MailboxFactory()
    user = core_factories.UserFactory()
    factories.MailDomainAccessFactory(
        user=user,
        domain=mailbox.domain,
        role=role,
    )

    client = APIClient()
    client.force_login(user)

    valid_new_values = {
        "secondary_email": "updated_mail@validformat.com",
        "first_name": "Marsha",
        "last_name": "Johnson",
    }
    for field_name in ["first_name", "last_name", "secondary_email"]:
        response = client.patch(
            f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/",
            {field_name: valid_new_values[field_name]},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        mailbox.refresh_from_db()
        assert getattr(mailbox, field_name) == valid_new_values[field_name]


def test_api_mailboxes_patch__viewer_can_update_own_mailbox():
    """Domain owners and admins should be allowed to update secondary email on a mailbox"""
    mailbox = factories.MailboxFactory()
    user = core_factories.UserFactory(email=f"{mailbox.local_part}@{mailbox.domain}")
    factories.MailDomainAccessFactory(
        user=user,
        domain=mailbox.domain,
        role=enums.MailDomainRoleChoices.VIEWER,
    )

    client = APIClient()
    client.force_login(user)

    valid_new_values = {
        "secondary_email": "updated_mail@validformat.com",
        "first_name": "Marsha",
        "last_name": "Johnson",
    }
    for field_name in ["first_name", "last_name", "secondary_email"]:
        response = client.patch(
            f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/",
            {field_name: valid_new_values[field_name]},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        mailbox.refresh_from_db()
        assert getattr(mailbox, field_name) == valid_new_values[field_name]


# DOMAIN AND LOCAL PART
@pytest.mark.parametrize(
    "role",
    ["viewer", "owner", "administrator"],
)
def test_api_mailboxes_patch__no_updating_domain_or_local_part(role):
    """Domain and local parts should not be updated."""
    mailbox = factories.MailboxFactory()
    user = core_factories.UserFactory()
    if role == "viewer":
        # viewer has similar privileges as admins on own mailbox
        user = core_factories.UserFactory(
            email=f"{mailbox.local_part}@{mailbox.domain}"
        )
    access = factories.MailDomainAccessFactory(
        user=user,
        domain=mailbox.domain,
        role=role,
    )

    client = APIClient()
    client.force_login(user)

    other_domain = factories.MailDomainEnabledFactory()
    local_part = mailbox.local_part
    response = client.patch(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/",
        {"local_part": "new.local.part", "domain": other_domain.name},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK  # a 400 would be better
    mailbox.refresh_from_db()
    assert mailbox.local_part == local_part
    assert mailbox.domain == access.domain
