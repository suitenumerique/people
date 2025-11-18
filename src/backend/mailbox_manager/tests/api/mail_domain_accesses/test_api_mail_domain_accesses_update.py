"""
Test for mail_domain accesses API endpoints in People's core app : update
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories

pytestmark = pytest.mark.django_db


def test_api_mail_domain__accesses_update_anonymous():
    """An anonymous users should not be allowed to update a mail domain access."""
    access = factories.MailDomainAccessFactory(role=enums.MailDomainRoleChoices.VIEWER)

    response = APIClient().put(
        f"/api/v1.0/mail-domains/{access.domain.slug}/accesses/{access.id!s}/",
        data={"role": enums.MailDomainRoleChoices.ADMIN},
        format="json",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    access.refresh_from_db()
    assert access.role == enums.MailDomainRoleChoices.VIEWER


def test_api_mail_domain__accesses_update_no_access_forbidden_not_found():
    """
    An authenticated user should not be allowed to update a mail domain access
    for a mail_domain to which they are not related.
    """
    authenticated_user = core_factories.UserFactory()
    access = factories.MailDomainAccessFactory(role=enums.MailDomainRoleChoices.VIEWER)

    client = APIClient()
    client.force_login(authenticated_user)
    response = client.put(
        f"/api/v1.0/mail-domains/{access.domain.slug}/accesses/{access.id!s}/",
        {"role": enums.MailDomainRoleChoices.ADMIN},
        format="json",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    access.refresh_from_db()
    assert access.role == enums.MailDomainRoleChoices.VIEWER


def test_api_mail_domain__accesses_update_authenticated_viewer():
    """A viewer of a mail domain should not be allowed to update accesses."""
    authenticated_user = core_factories.UserFactory()
    mail_domain = factories.MailDomainFactory(
        users=[(authenticated_user, enums.MailDomainRoleChoices.VIEWER)]
    )
    access = factories.MailDomainAccessFactory(
        domain=mail_domain,
        role=enums.MailDomainRoleChoices.VIEWER,
    )
    client = APIClient()
    client.force_login(authenticated_user)
    response = client.put(
        f"/api/v1.0/mail-domains/{access.domain.slug}/accesses/{access.id!s}/",
        {"role": enums.MailDomainRoleChoices.ADMIN},
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    access.refresh_from_db()
    assert access.role == enums.MailDomainRoleChoices.VIEWER


def test_api_mail_domain__accesses_update_authenticated_viewer_themself():
    """A viewer of a mail domain should not be allowed to update its accesses."""
    authenticated_user = core_factories.UserFactory()
    access = factories.MailDomainAccessFactory(
        user=authenticated_user,
        role=enums.MailDomainRoleChoices.VIEWER,
    )
    client = APIClient()
    client.force_login(authenticated_user)
    response = client.put(
        f"/api/v1.0/mail-domains/{access.domain.slug}/accesses/{access.id!s}/",
        {"role": enums.MailDomainRoleChoices.ADMIN},
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    access.refresh_from_db()
    assert access.role == enums.MailDomainRoleChoices.VIEWER


def test_api_mail_domain__accesses_update_administrator_except_owner():
    """
    An administrator of a mail domain should be allowed to update a user
    access for this mail domain, as long as they don't try to set the role to owner.
    """
    authenticated_user = core_factories.UserFactory()
    mail_domain = factories.MailDomainFactory(
        users=[(authenticated_user, enums.MailDomainRoleChoices.ADMIN)]
    )
    admin_access = factories.MailDomainAccessFactory(
        domain=mail_domain, role=enums.MailDomainRoleChoices.ADMIN
    )
    viewer_access = factories.MailDomainAccessFactory(
        domain=mail_domain, role=enums.MailDomainRoleChoices.VIEWER
    )

    client = APIClient()
    client.force_login(authenticated_user)
    response = client.put(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/accesses/{admin_access.id!s}/",
        data={"role": enums.MailDomainRoleChoices.OWNER},
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    admin_access.refresh_from_db()
    assert admin_access.role == enums.MailDomainRoleChoices.ADMIN

    response = client.put(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/accesses/{admin_access.id!s}/",
        data={"role": enums.MailDomainRoleChoices.VIEWER},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    admin_access.refresh_from_db()
    assert admin_access.role == enums.MailDomainRoleChoices.VIEWER

    response = client.put(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/accesses/{viewer_access.id!s}/",
        data={"role": enums.MailDomainRoleChoices.OWNER},
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    viewer_access.refresh_from_db()
    assert viewer_access.role == enums.MailDomainRoleChoices.VIEWER

    response = client.put(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/accesses/{viewer_access.id!s}/",
        data={"role": enums.MailDomainRoleChoices.ADMIN},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    viewer_access.refresh_from_db()
    assert viewer_access.role == enums.MailDomainRoleChoices.ADMIN


def test_api_mail_domain__accesses_update_administrator_from_owner():
    """
    An administrator for a mail domain, should not be allowed to update
    the user access of an "owner" for this mail domain.
    """
    authenticated_user = core_factories.UserFactory()
    mail_domain = factories.MailDomainFactory(
        users=[(authenticated_user, enums.MailDomainRoleChoices.ADMIN)]
    )
    owner = core_factories.UserFactory()
    owner_access = factories.MailDomainAccessFactory(
        domain=mail_domain, user=owner, role=enums.MailDomainRoleChoices.OWNER
    )

    client = APIClient()
    client.force_login(authenticated_user)
    response = client.put(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/accesses/{owner_access.id!s}/",
        data={"role": enums.MailDomainRoleChoices.ADMIN},
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    owner_access.refresh_from_db()
    assert owner_access.role == enums.MailDomainRoleChoices.OWNER


def test_api_mail_domain__accesses_update_owner():
    """
    An owner of a mail domain should be allowed to update
    a user access for this domain.
    """
    owner_authenticated = core_factories.UserFactory()
    mail_domain = factories.MailDomainFactory(
        users=[(owner_authenticated, enums.MailDomainRoleChoices.OWNER)]
    )
    user_access1 = factories.MailDomainAccessFactory(
        domain=mail_domain, role=enums.MailDomainRoleChoices.ADMIN
    )
    user_access2 = factories.MailDomainAccessFactory(
        domain=mail_domain, role=enums.MailDomainRoleChoices.VIEWER
    )

    client = APIClient()
    client.force_login(owner_authenticated)
    # turn admin in viewer
    response = client.put(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/accesses/{user_access1.id!s}/",
        data={"role": enums.MailDomainRoleChoices.VIEWER},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    user_access1.refresh_from_db()
    assert user_access1.role == enums.MailDomainRoleChoices.VIEWER

    # turn viewer in owner
    response = client.put(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/accesses/{user_access1.id!s}/",
        data={"role": enums.MailDomainRoleChoices.OWNER},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    user_access1.refresh_from_db()
    assert user_access1.role == enums.MailDomainRoleChoices.OWNER

    # turn viewer in admin
    response = client.put(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/accesses/{user_access2.id!s}/",
        data={"role": enums.MailDomainRoleChoices.ADMIN},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    user_access2.refresh_from_db()
    assert user_access2.role == enums.MailDomainRoleChoices.ADMIN


def test_api_mail_domain__accesses_update_owner_for_owners():
    """
    An owner of a mail domain should be allowed to update
    an existing owner access for this mail domain.
    """
    owner_authenticated = core_factories.UserFactory()
    mail_domain = factories.MailDomainFactory(
        users=[(owner_authenticated, enums.MailDomainRoleChoices.OWNER)]
    )
    other_owner_access = factories.MailDomainAccessFactory(
        domain=mail_domain, role=enums.MailDomainRoleChoices.OWNER
    )

    client = APIClient()
    client.force_login(owner_authenticated)
    for new_role in [
        enums.MailDomainRoleChoices.ADMIN,
        enums.MailDomainRoleChoices.VIEWER,
    ]:
        response = client.patch(
            f"/api/v1.0/mail-domains/{mail_domain.slug}/accesses/{other_owner_access.id!s}/",
            data={"role": new_role},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        other_owner_access.refresh_from_db()
        assert other_owner_access.role == new_role


def test_api_mail_domain__accesses_update_owner_self():
    """
    An owner of a mail domain should be allowed to update
    their own user access provided there are other owners in the mail domain.
    """
    owner_authenticated = core_factories.UserFactory()
    access = factories.MailDomainAccessFactory(
        user=owner_authenticated, role=enums.MailDomainRoleChoices.OWNER
    )

    client = APIClient()
    client.force_login(owner_authenticated)
    for new_role in [
        enums.MailDomainRoleChoices.ADMIN,
        enums.MailDomainRoleChoices.VIEWER,
    ]:
        response = client.patch(
            f"/api/v1.0/mail-domains/{access.domain.slug}/accesses/{access.id!s}/",
            data={"role": new_role},
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.json()["role"]
            == "Cannot change the role to a non-owner role for the last owner access."
        )
        access.refresh_from_db()
        assert access.role == enums.MailDomainRoleChoices.OWNER

    # Add another owner and it should now work
    factories.MailDomainAccessFactory(
        domain=access.domain, role=enums.MailDomainRoleChoices.OWNER
    )
    for new_role in [
        enums.MailDomainRoleChoices.ADMIN,
        enums.MailDomainRoleChoices.VIEWER,
    ]:
        response = client.patch(
            f"/api/v1.0/mail-domains/{access.domain.slug}/accesses/{access.id!s}/",
            data={"role": new_role},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        access.refresh_from_db()
        assert access.role == new_role
