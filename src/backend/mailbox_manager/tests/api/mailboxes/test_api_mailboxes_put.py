"""
Unit tests for the mailbox API
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories

pytestmark = pytest.mark.django_db


def test_api_mailboxes_put__anonymous_forbidden():
    """Anonymous users should not be able to update a mailbox."""
    mailbox = factories.MailboxFactory()
    saved_secondary = mailbox.secondary_email
    APIClient().get(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/"
    )
    response = APIClient().patch(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/",
        {"something": "updated"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    mailbox.refresh_from_db()
    assert mailbox.secondary_email == saved_secondary


def test_api_mailboxes_put__unauthorized_forbidden():
    """Authenticated but unauthoriezd users should not be able to update mailboxes."""
    client = APIClient()
    client.force_login(core_factories.UserFactory())

    mailbox = factories.MailboxFactory()
    saved_secondary = mailbox.secondary_email
    response = client.put(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/",
        {"something": "updated"},
        format="json",
    )

    # permission denied at domain level
    assert response.status_code == status.HTTP_403_FORBIDDEN
    mailbox.refresh_from_db()
    assert mailbox.secondary_email == saved_secondary


def test_api_mailboxes_put__unauthorized_no_mailbox():
    """Authenticated but unauthoriezd users should not be able to update mailboxes."""
    client = APIClient()
    client.force_login(core_factories.UserFactory())

    domain = factories.MailDomainEnabledFactory()
    response = client.put(
        f"/api/v1.0/mail-domains/{domain.slug}/mailboxes/nonexistent_mailbox_pk/",
        {"something": "updated"},
        format="json",
    )

    # permission denied at domain level
    # the existence of the mailbox is not checked
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_api_mailboxes_put__viewer_forbidden():
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
    for field_name in [
        "secondary_email",
        "first_name",
        "last_name",
        "domain",
        "local_part",
    ]:
        old_value = getattr(mailbox, field_name)
        response = client.put(
            f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/",
            {field_name: "something_else"},
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        mailbox.refresh_from_db()
        assert getattr(mailbox, field_name) == old_value


# UPDATABLE FIELDS : SECONDARY EMAIL, FIRST NAME AND LAST NAME
@pytest.mark.parametrize(
    "role",
    ["owner", "administrator"],
)
def test_api_mailboxes_put__admins_can_update_mailboxes(role):
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
        "secondary_email": "marsha.p@social.us",
        "first_name": "Marsha",
        "last_name": "Johnson",
    }
    response = client.put(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/",
        {
            "first_name": valid_new_values["first_name"],
            "last_name": valid_new_values["last_name"],
            "secondary_email": valid_new_values["secondary_email"],
        },
        format="json",
    )
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    mailbox.refresh_from_db()
    assert result["first_name"] == valid_new_values["first_name"]
    assert result["last_name"] == valid_new_values["last_name"]
    assert result["secondary_email"] == valid_new_values["secondary_email"]


# DOMAIN AND LOCAL PART
@pytest.mark.parametrize(
    "role",
    ["viewer", "owner", "administrator"],
)
def test_api_mailboxes_put__no_updating_domain_or_local_part(role):
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
    old_local_part = mailbox.local_part
    response = client.put(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/",
        {"local_part": "new.local.part", "domain": other_domain.name},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    mailbox.refresh_from_db()
    assert mailbox.local_part == old_local_part
    assert mailbox.domain == access.domain
