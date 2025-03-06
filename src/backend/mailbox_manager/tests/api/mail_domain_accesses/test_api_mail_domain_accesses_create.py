"""
Test for mail domain accesses API endpoints in People's core app : create
"""

import logging
import random
import re

import pytest
import responses
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories, models

pytestmark = pytest.mark.django_db


def test_api_mail_domain__accesses_create_anonymous():
    """Anonymous users should not be allowed to create mail domain accesses."""
    user = core_factories.UserFactory()
    mail_domain = factories.MailDomainFactory()
    for role in [role[0] for role in enums.MailDomainRoleChoices.choices]:
        response = APIClient().post(
            f"/api/v1.0/mail-domains/{mail_domain.slug}/accesses/",
            {
                "user": str(user.id),
                "role": role,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {
            "detail": "Authentication credentials were not provided."
        }
        assert models.MailDomainAccess.objects.exists() is False


def test_api_mail_domain__accesses_create_authenticated_unrelated():
    """
    Authenticated users should not be allowed to create domain accesses for a domain to
    which they are not related.
    """
    user = core_factories.UserFactory()
    other_user = core_factories.UserFactory()
    domain = factories.MailDomainFactory()

    client = APIClient()
    client.force_login(user)
    for role in [role[0] for role in enums.MailDomainRoleChoices.choices]:
        response = client.post(
            f"/api/v1.0/mail-domains/{domain.slug}/accesses/",
            {
                "user": str(other_user.id),
                "role": role,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": "You are not allowed to manage accesses for this domain."
        }
        assert not models.MailDomainAccess.objects.filter(user=other_user).exists()


def test_api_mail_domain__accesses_create_authenticated_viewer():
    """Viewer of a mail domain should not be allowed to create mail domain accesses."""
    authenticated_user = core_factories.UserFactory()
    mail_domain = factories.MailDomainFactory(
        users=[(authenticated_user, enums.MailDomainRoleChoices.VIEWER)]
    )
    other_user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(authenticated_user)
    for role in [role[0] for role in enums.MailDomainRoleChoices.choices]:
        response = client.post(
            f"/api/v1.0/mail-domains/{mail_domain.slug}/accesses/",
            {
                "user": str(other_user.id),
                "role": role,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": "You are not allowed to manage accesses for this domain."
        }

    assert not models.MailDomainAccess.objects.filter(user=other_user).exists()


def test_api_mail_domain__accesses_create_authenticated_administrator():
    """
    Administrators of a domain should be able to create mail domain accesses
    except for the "owner" role.
    """
    authenticated_user = core_factories.UserFactory()
    mail_domain = factories.MailDomainFactory(
        users=[(authenticated_user, enums.MailDomainRoleChoices.ADMIN)]
    )
    other_user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(authenticated_user)

    with responses.RequestsMock() as rsps:
        # It should not be allowed to create an owner access
        response = client.post(
            f"/api/v1.0/mail-domains/{mail_domain.slug}/accesses/",
            {
                "user": str(other_user.id),
                "role": enums.MailDomainRoleChoices.OWNER,
            },
            format="json",
        )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "Only owners of a domain can assign other users as owners."
    }

    # It should be allowed to create a lower access
    for role in [enums.MailDomainRoleChoices.ADMIN, enums.MailDomainRoleChoices.VIEWER]:
        other_user = core_factories.UserFactory()
        with responses.RequestsMock() as rsps:
            if role != enums.MailDomainRoleChoices.VIEWER:
                # viewers don't have allows in dimail
                rsps.add(
                    rsps.POST,
                    re.compile(r".*/users/"),
                    body=str(
                        {
                            "name": str(other_user.sub),
                            "is_admin": "false",
                            "uuid": "71f60d74-a3ad-46bc-bc2b-20d79a2e36fb",
                            "perms": [],
                        }
                    ),
                    status=status.HTTP_201_CREATED,
                    content_type="application/json",
                )
                rsps.add(
                    rsps.POST,
                    re.compile(r".*/allows/"),
                    body=str({"user": other_user.sub, "domain": str(mail_domain.name)}),
                    status=status.HTTP_201_CREATED,
                    content_type="application/json",
                )
            response = client.post(
                f"/api/v1.0/mail-domains/{mail_domain.slug}/accesses/",
                {
                    "user": str(other_user.id),
                    "role": role,
                },
                format="json",
            )
        assert response.status_code == status.HTTP_201_CREATED
        new_mail_domain_access = models.MailDomainAccess.objects.filter(
            user=other_user
        ).last()

        assert response.json()["id"] == str(new_mail_domain_access.id)
        assert response.json()["role"] == role
    assert models.MailDomainAccess.objects.filter(domain=mail_domain).count() == 3


def test_api_mail_domain__accesses_create_authenticated_owner():
    """
    Owners of a mail domain should be able to create mail domain accesses whatever the role.
    """
    authenticated_user = core_factories.UserFactory()
    mail_domain = factories.MailDomainFactory(
        users=[(authenticated_user, enums.MailDomainRoleChoices.OWNER)]
    )
    other_user = core_factories.UserFactory()
    role = random.choice([role[0] for role in enums.MailDomainRoleChoices.choices])

    client = APIClient()
    client.force_login(authenticated_user)
    with responses.RequestsMock() as rsps:
        if role != enums.MailDomainRoleChoices.VIEWER:
            rsps.add(
                rsps.POST,
                re.compile(r".*/users/"),
                body=str(
                    {
                        "name": str(other_user.sub),
                        "is_admin": "false",
                        "uuid": "71f60d74-a3ad-46bc-bc2b-20d79a2e36fb",
                        "perms": [],
                    }
                ),
                status=status.HTTP_201_CREATED,
                content_type="application/json",
            )
            rsps.add(
                rsps.POST,
                re.compile(r".*/allows/"),
                body=str({"user": other_user.sub, "domain": str(mail_domain.name)}),
                status=status.HTTP_201_CREATED,
                content_type="application/json",
            )
        response = client.post(
            f"/api/v1.0/mail-domains/{mail_domain.slug}/accesses/",
            {
                "user": str(other_user.id),
                "role": role,
            },
            format="json",
        )

    assert response.status_code == status.HTTP_201_CREATED
    assert models.MailDomainAccess.objects.filter(user=other_user).count() == 1
    new_mail_domain_access = models.MailDomainAccess.objects.filter(
        user=other_user
    ).get()
    assert response.json()["id"] == str(new_mail_domain_access.id)
    assert response.json()["role"] == role


## INTEROP WITH DIMAIL
def test_api_mail_domains_accesses__create_dimail_allows(caplog):
    """
    Creating a domain access on our API should trigger a request to create an access on dimail too.
    """
    caplog.set_level(logging.INFO)

    authenticated_user = core_factories.UserFactory()
    domain = factories.MailDomainFactory(status="enabled")
    factories.MailDomainAccessFactory(
        domain=domain, user=authenticated_user, role=enums.MailDomainRoleChoices.OWNER
    )
    client = APIClient()
    client.force_login(authenticated_user)

    allowed_user = core_factories.UserFactory()
    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.POST,
            re.compile(r".*/users/"),
            body=str(
                {
                    "name": str(allowed_user.sub),
                    "is_admin": "false",
                    "uuid": "71f60d74-a3ad-46bc-bc2b-20d79a2e36fb",
                    "perms": [],
                }
            ),
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(r".*/allows/"),
            body=str({"user": allowed_user.sub, "domain": str(domain.name)}),
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )
        response = client.post(
            f"/api/v1.0/mail-domains/{domain.slug}/accesses/",
            {
                "user": str(allowed_user.id),
                "role": enums.MailDomainRoleChoices.ADMIN,
            },
            format="json",
        )

    assert response.status_code == status.HTTP_201_CREATED

    log_messages = [msg.message for msg in caplog.records]
    # check logs
    assert (
        f'[DIMAIL] User "{allowed_user.sub}" successfully created on dimail'
        in log_messages
    )
    assert (
        f'[DIMAIL] Permissions granted for user "{allowed_user.sub}" on domain {domain.name}.'
        in log_messages
    )


def test_api_mail_domains_accesses__dont_create_dimail_allows_for_viewer():
    """Dimail should not be called when creating an access to a simple viewer."""

    authenticated_user = core_factories.UserFactory()
    domain = factories.MailDomainFactory(status="enabled")
    factories.MailDomainAccessFactory(
        domain=domain, user=authenticated_user, role=enums.MailDomainRoleChoices.OWNER
    )
    client = APIClient()
    client.force_login(authenticated_user)

    allowed_user = core_factories.UserFactory()
    with responses.RequestsMock():
        # No call expected
        response = client.post(
            f"/api/v1.0/mail-domains/{domain.slug}/accesses/",
            {
                "user": str(allowed_user.id),
                "role": enums.MailDomainRoleChoices.VIEWER,
            },
            format="json",
        )

    assert response.status_code == status.HTTP_201_CREATED


def test_api_mail_domains_accesses__user_already_on_dimail(caplog):
    """The expected allow should be created when an user already exists on dimail
    (i.e. previous admin/owner of same domain or current on another domain)."""
    caplog.set_level(logging.INFO)

    authenticated_user = core_factories.UserFactory()
    domain = factories.MailDomainFactory()
    factories.MailDomainAccessFactory(
        domain=domain, user=authenticated_user, role=enums.MailDomainRoleChoices.OWNER
    )
    client = APIClient()
    client.force_login(authenticated_user)

    allowed_user = core_factories.UserFactory()

    with responses.RequestsMock() as rsps:
        # No call expected
        rsps.add(
            rsps.POST,
            re.compile(r".*/users/"),
            body=str(
                {"detail": "User already exists"}
            ),  # the user is already on dimail
            status=status.HTTP_409_CONFLICT,
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(r".*/allows/"),
            body=str({"user": allowed_user.sub, "domain": str(domain.name)}),
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )
        response = client.post(
            f"/api/v1.0/mail-domains/{domain.slug}/accesses/",
            {
                "user": str(allowed_user.id),
                "role": enums.MailDomainRoleChoices.ADMIN,
            },
            format="json",
        )

    assert response.status_code == status.HTTP_201_CREATED

    # check logs
    log_messages = [msg.message for msg in caplog.records]
    assert (
        f'[DIMAIL] Attempt to create user "{allowed_user.sub}" which already exists.'
        in log_messages
    )
    assert (
        f'[DIMAIL] Permissions granted for user "{allowed_user.sub}" on domain {domain.name}.'
        in log_messages
    )
