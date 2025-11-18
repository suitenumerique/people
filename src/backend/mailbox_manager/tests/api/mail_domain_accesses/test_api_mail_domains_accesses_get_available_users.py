"""
Tests for MailDomainAccess API endpoint in People's mailbox manager app.
Focus on get available users.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories
from core import models as core_models

from mailbox_manager import enums, factories

pytestmark = pytest.mark.django_db


def test_api_mail_domain__available_users_anonymous():
    """Anonymous users should not be allowed to list users."""
    maildomain = factories.MailDomainFactory()

    response = APIClient().get(
        f"/api/v1.0/mail-domains/{maildomain.slug}/accesses/users/"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_mail_domain__available_users_forbidden():
    """Users with no access should not be able to list available users."""
    authenticated_user = core_factories.UserFactory()
    client = APIClient()
    client.force_login(authenticated_user)
    maildomain = factories.MailDomainFactory()

    response = client.get(f"/api/v1.0/mail-domains/{maildomain.slug}/accesses/users/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "role",
    [
        enums.MailDomainRoleChoices.OWNER,
        enums.MailDomainRoleChoices.ADMIN,
    ],
)
def test_api_mail_domain__list_available_users__with_abilities(role):
    """Authenticated users with roles owner and admin should be allowed to list available users
    for a domain.
    """
    dave = core_factories.UserFactory(email="bowbow@example.com", name="David Bowman")
    nicole = core_factories.UserFactory(
        email="nicole_foole@example.com", name="Nicole Foole"
    )
    frank = core_factories.UserFactory(
        email="frank_poole@example.com", name="Frank Poole"
    )
    mary = core_factories.UserFactory(email="mary_pol@example.com", name="Mary Pol")

    expected_ids = {str(user.id) for user in core_models.User.objects.all()}

    authenticated_user = core_factories.UserFactory(name="Owen Rights")
    client = APIClient()
    client.force_login(authenticated_user)

    maildomain = factories.MailDomainFactory(name="example.com")
    factories.MailDomainAccessFactory(
        user=authenticated_user,
        domain=maildomain,
        role=role,
    )

    response = client.get(f"/api/v1.0/mail-domains/{maildomain.slug}/accesses/users/")
    assert response.status_code == status.HTTP_200_OK
    results = response.json()
    assert len(results) == 4
    results_id = {result["id"] for result in results}
    assert expected_ids == results_id

    # now test filter user
    response = client.get(
        f"/api/v1.0/mail-domains/{maildomain.slug}/accesses/users/?q=OL"
    )
    assert response.status_code == status.HTTP_200_OK
    expected_ids = {str(user.id) for user in [nicole, frank, mary]}
    results = response.json()
    assert len(results) == 3
    results_id = {result["id"] for result in results}
    assert expected_ids == results_id

    # filter on email info
    response = client.get(
        f"/api/v1.0/mail-domains/{maildomain.slug}/accesses/users/?q=bowbow"
    )
    assert response.status_code == status.HTTP_200_OK
    results = response.json()
    assert len(results) == 1
    assert results[0]["id"] == str(dave.id)


def test_api_mail_domain__list_available_users__viewer():
    """A viewer should not be allowed to list available users for a domain."""
    core_factories.UserFactory.create_batch(10)

    authenticated_user = core_factories.UserFactory()
    client = APIClient()
    client.force_login(authenticated_user)

    maildomain = factories.MailDomainFactory(name="example.com")
    factories.MailDomainAccessFactory(
        user=authenticated_user,
        domain=maildomain,
        role=enums.MailDomainRoleChoices.VIEWER,
    )

    response = client.get(f"/api/v1.0/mail-domains/{maildomain.slug}/accesses/users/")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "role",
    [
        enums.MailDomainRoleChoices.OWNER,
        enums.MailDomainRoleChoices.ADMIN,
    ],
)
def test_api_mail_domain__list_available_users__organization(role):
    """If an authenticated owner or admin of a domain has an organization,
    only users from the same organization are available.
    """
    organization = core_factories.OrganizationFactory(with_registration_id=True)
    other_organization = core_factories.OrganizationFactory(with_registration_id=True)
    authenticated_user = core_factories.UserFactory(
        name="Owen Rights", organization=organization
    )

    client = APIClient()
    client.force_login(authenticated_user)

    maildomain = factories.MailDomainFactory(name="example.com")
    factories.MailDomainAccessFactory(
        user=authenticated_user,
        domain=maildomain,
        role=role,
    )

    dave = core_factories.UserFactory(
        email="bowbow@example.com",
        name="David Bowman",
        organization=organization,
    )
    nicole = core_factories.UserFactory(
        email="nicole_foole@example.com",
        name="Nicole Foole",
        organization=organization,
    )
    core_factories.UserFactory(
        email="frank_poole@example.com",
        name="Frank Poole",
        organization=other_organization,
    )
    core_factories.UserFactory(
        email="mary_pol@example.com",
        name="Mary Pol",
        organization=other_organization,
    )

    expected_ids = sorted([str(nicole.id), str(dave.id)])
    response = client.get(f"/api/v1.0/mail-domains/{maildomain.slug}/accesses/users/")
    assert response.status_code == status.HTTP_200_OK
    results = response.json()
    assert len(results) == 2
    results_id = sorted({result["id"] for result in results})
    assert expected_ids == results_id


def test_api_mail_domain__list_available_users__organization_viewer():
    """A viewer should not be allowed to list available users for a domain."""
    organization = core_factories.OrganizationFactory(with_registration_id=True)
    other_organization = core_factories.OrganizationFactory(with_registration_id=True)
    authenticated_user = core_factories.UserFactory(organization=organization)

    client = APIClient()
    client.force_login(authenticated_user)

    maildomain = factories.MailDomainFactory()
    factories.MailDomainAccessFactory(
        user=authenticated_user,
        domain=maildomain,
        role=enums.MailDomainRoleChoices.VIEWER,
    )

    core_factories.UserFactory.create_batch(10, organization=organization)
    core_factories.UserFactory.create_batch(5, organization=other_organization)

    response = client.get(f"/api/v1.0/mail-domains/{maildomain.slug}/accesses/users/")
    assert response.status_code == status.HTTP_403_FORBIDDEN
