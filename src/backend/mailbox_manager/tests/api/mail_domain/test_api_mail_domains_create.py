"""
Tests for MailDomains API endpoint in People's app mailbox_manager. Focus on "create" action.
"""

import logging
import re

import pytest
import responses
from requests.exceptions import HTTPError
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories, models

pytestmark = pytest.mark.django_db


def test_api_mail_domains__create_anonymous():
    """Anonymous users should not be allowed to create mail domains."""

    response = APIClient().post(
        "/api/v1.0/mail-domains/",
        {
            "name": "mydomain.com",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not models.MailDomain.objects.exists()


def test_api_mail_domains__create_name_unique():
    """
    Creating domain should raise an error if already existing name.
    """
    factories.MailDomainFactory(name="existing_domain.com")
    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    response = client.post(
        "/api/v1.0/mail-domains/",
        {
            "name": "existing_domain.com",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["name"] == ["Mail domain with this name already exists."]


def test_api_mail_domains__create_authenticated():
    """
    Authenticated users should be able to create mail domains
    and should automatically be added as owner of the newly created domain.
    """
    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    domain_name = "test.domain.fr"

    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.POST,
            re.compile(r".*/domains/"),
            body=str(
                {
                    "name": domain_name,
                }
            ),
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(r".*/users/"),
            body=str(
                {
                    "name": "request-user-sub",
                    "is_admin": "false",
                    "uuid": "user-uuid-on-dimail",
                    "perms": [],
                }
            ),
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(r".*/allows/"),
            body=str({"user": "request-user-sub", "domain": str(domain_name)}),
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )
        response = client.post(
            "/api/v1.0/mail-domains/",
            {
                "name": domain_name,
                "context": "null",
                "features": ["webmail"],
                "support_email": f"support@{domain_name}",
            },
            format="json",
        )
    assert response.status_code == status.HTTP_201_CREATED
    domain = models.MailDomain.objects.get()

    # response is as expected
    assert response.json() == {
        "id": str(domain.id),
        "name": domain.name,
        "slug": domain.slug,
        "status": enums.MailDomainStatusChoices.PENDING,
        "created_at": domain.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": domain.updated_at.isoformat().replace("+00:00", "Z"),
        "abilities": domain.get_abilities(user),
        "count_mailboxes": 0,
        "support_email": domain.support_email,
    }

    # a new domain with status "pending" is created and authenticated user is the owner
    assert domain.status == enums.MailDomainStatusChoices.PENDING
    assert domain.name == domain_name
    assert domain.accesses.filter(role="owner", user=user).exists()


def test_api_mail_domains__create_authenticated__dimail_failure():
    """
    Despite a dimail failure for user and/or allow creation,
    an authenticated user should be able to create a mail domain
    and should automatically be added as owner of the newly created domain.
    """
    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    domain_name = "test.domain.fr"

    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.POST,
            re.compile(r".*/domains/"),
            body=str(
                {
                    "name": domain_name,
                }
            ),
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(r".*/users/"),
            body=str(
                {
                    "name": "request-user-sub",
                    "is_admin": "false",
                    "uuid": "user-uuid-on-dimail",
                    "perms": [],
                }
            ),
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(r".*/allows/"),
            body=str({"user": "request-user-sub", "domain": str(domain_name)}),
            status=status.HTTP_403_FORBIDDEN,
            content_type="application/json",
        )
        response = client.post(
            "/api/v1.0/mail-domains/",
            {
                "name": domain_name,
                "context": "null",
                "features": ["webmail"],
                "support_email": f"support@{domain_name}",
            },
            format="json",
        )
    domain = models.MailDomain.objects.get()

    # response is as expected
    assert response.json() == {
        "id": str(domain.id),
        "name": domain.name,
        "slug": domain.slug,
        "status": enums.MailDomainStatusChoices.FAILED,
        "created_at": domain.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": domain.updated_at.isoformat().replace("+00:00", "Z"),
        "abilities": domain.get_abilities(user),
        "count_mailboxes": 0,
        "support_email": domain.support_email,
    }

    # a new domain with status "failed" is created and authenticated user is the owner
    assert domain.status == enums.MailDomainStatusChoices.FAILED
    assert domain.name == domain_name
    assert domain.accesses.filter(role="owner", user=user).exists()


## SYNC TO DIMAIL
def test_api_mail_domains__create_dimail_domain(caplog):
    """
    Creating a domain should trigger a call to create a domain on dimail too.
    """
    caplog.set_level(logging.INFO)

    user = core_factories.UserFactory()
    client = APIClient()
    client.force_login(user)
    domain_name = "test.fr"

    with responses.RequestsMock() as rsps:
        rsp = rsps.add(
            rsps.POST,
            re.compile(r".*/domains/"),
            body=str(
                {
                    "name": domain_name,
                }
            ),
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(r".*/users/"),
            body=str(
                {
                    "name": "request-user-sub",
                    "is_admin": "false",
                    "uuid": "user-uuid-on-dimail",
                    "perms": [],
                }
            ),
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(r".*/allows/"),
            body=str({"user": "request-user-sub", "domain": str(domain_name)}),
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )
        response = client.post(
            "/api/v1.0/mail-domains/",
            {
                "name": domain_name,
                "support_email": f"support@{domain_name}",
            },
            format="json",
        )

    assert response.status_code == status.HTTP_201_CREATED
    assert rsp.call_count == 1  # endpoint was called

    # Logger
    assert len(caplog.records) == 4  # should be 3. Last empty info still here.
    assert (
        caplog.records[0].message
        == f"Domain {domain_name} successfully created on dimail by user {user.sub}"
    )
    assert (
        caplog.records[1].message
        == f'[DIMAIL] User "{user.sub}" successfully created on dimail'
    )
    assert (
        caplog.records[2].message
        == f'[DIMAIL] Permissions granted for user "{user.sub}" on domain {domain_name}.'
    )


def test_api_mail_domains__no_creation_when_dimail_duplicate(caplog):
    """No domain should be created when dimail returns a 409 conflict."""
    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)
    domain_name = "test.fr"
    dimail_error = {
        "status_code": status.HTTP_409_CONFLICT,
        "detail": "Domain already exists",
    }

    with responses.RequestsMock() as rsps:
        rsp = rsps.add(
            rsps.POST,
            re.compile(r".*/domains/"),
            body=str({"detail": dimail_error["detail"]}),
            status=dimail_error["status_code"],
            content_type="application/json",
        )
        with pytest.raises(HTTPError):
            response = client.post(
                "/api/v1.0/mail-domains/",
                {
                    "name": domain_name,
                    "support_email": f"support@{domain_name}",
                },
                format="json",
            )

            assert rsp.call_count == 1  # endpoint was called
            assert response.status_code == dimail_error["status_code"]
            assert response.json() == {"detail": dimail_error["detail"]}

    # check logs
    record = caplog.records[0]
    assert record.levelname == "ERROR"
    assert (
        record.message
        == "[DIMAIL] unexpected error : 409 {'detail': 'Domain already exists'}"
    )
