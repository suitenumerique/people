"""
Unit tests for the mailbox API
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories

pytestmark = pytest.mark.django_db


def test_api_mailboxes__update_anonymous_forbidden():
    """Anonymous users should not be able to update a mailbox via the API."""
    mailbox = factories.MailboxFactory()
    saved_secondary = mailbox.secondary_email
    APIClient().get(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/"
    )
    response = APIClient().patch(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/",
        {"secondary_email": "new_secondary@newdomain.fr"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    mailbox.refresh_from_db()
    assert mailbox.secondary_email == saved_secondary


def test_api_mailboxes__update_unauthorized_failure():
    """Authenticated but unauthoriezd users should not be able to update mailbox."""
    client = APIClient()
    client.force_login(core_factories.UserFactory())

    mailbox = factories.MailboxFactory()
    saved_secondary = mailbox.secondary_email
    response = client.patch(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/mailboxes/{mailbox.pk}/",
        {"secondary_email": "new_secondary@newdomain.fr"},
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mailbox.refresh_from_db()
    assert mailbox.secondary_email == saved_secondary


### UPDATE SECONDARY EMAIL


def test_api_mailboxes__update_reader():
    """User having viewer access on a domain should not be able to update
    secondary email on a mailbox, except theirs."""
    # setup user, around which the test revolves
    user = core_factories.UserFactory()
    domain = factories.MailDomainEnabledFactory(name=user.email.split("@")[1])
    factories.MailDomainAccessFactory(
        user=user,
        domain=domain,
        role=enums.MailDomainRoleChoices.VIEWER,
    )
    client = APIClient()
    client.force_login(user)

    # update someone else's secondary email fails
    mailbox = factories.MailboxFactory(domain=domain)
    saved_secondary = mailbox.secondary_email
    response = client.patch(
        f"/api/v1.0/mail-domains/{domain.slug}/mailboxes/{mailbox.pk}/",
        {"secondary_email": "new_secondary@newdomain.fr"},
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mailbox.refresh_from_db()
    assert mailbox.secondary_email == saved_secondary

    # updating your own secondary email succeeds
    own_mailbox = factories.MailboxFactory(
        local_part=user.email.split("@")[0], domain=domain
    )
    new_secondary_email = "new_secondary@newdomain.fr"

    response = client.patch(
        f"/api/v1.0/mail-domains/{domain.slug}/mailboxes/{own_mailbox.pk}/",
        {"secondary_email": new_secondary_email},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    mailbox.refresh_from_db()
    assert mailbox.secondary_email == new_secondary_email


@pytest.mark.parametrize(
    "role",
    ["owner", "administrator"],
)
def test_api_mailboxes__update_admin(role):
    """Admin and owners of a domain should be allowed to update secondary email on a mailbox."""
    access = factories.MailDomainAccessFactory(
        role=role,
    )
    mailbox = factories.MailboxFactory(domain=access.domain)

    client = APIClient()
    client.force_login(access.user)
    response = client.patch(
        f"/api/v1.0/mail-domains/{access.domain.slug}/mailboxes/{mailbox.pk}/",
        {"secondary_email": "new_secondary@newdomain.fr"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    mailbox.refresh_from_db()
    assert mailbox.secondary_email == "new_secondary@newdomain.fr"


## DOMAIN AND LOCAL PART


@pytest.mark.parametrize(
    "role",
    ["viewer", "owner", "administrator"],
)
def test_api_mailboxes__no_updating_domain(role):
    """Domain should not be updated."""
    access = factories.MailDomainAccessFactory(
        role=role,
    )
    mailbox = factories.MailboxFactory(domain=access.domain)
    other_domain = factories.MailDomainEnabledFactory()

    client = APIClient()
    client.force_login(access.user)
    response = client.patch(
        f"/api/v1.0/mail-domains/{access.domain.slug}/mailboxes/{mailbox.pk}/",
        {"domain": other_domain.name},
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mailbox.refresh_from_db()
    assert mailbox.domain == access.domain


@pytest.mark.parametrize(
    "role",
    ["viewer", "owner", "administrator"],
)
def test_api_mailboxes__no_updating_local_part(role):
    """Local parts should not be updated."""
    access = factories.MailDomainAccessFactory(
        role=role,
    )
    mailbox = factories.MailboxFactory(domain=access.domain)
    mailbox_local_part = mailbox.local_part

    client = APIClient()
    client.force_login(access.user)
    response = client.patch(
        f"/api/v1.0/mail-domains/{access.domain.slug}/mailboxes/{mailbox.pk}/",
        {"local_part": "new_username"},
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mailbox.refresh_from_db()
    assert mailbox.local_part == mailbox_local_part
