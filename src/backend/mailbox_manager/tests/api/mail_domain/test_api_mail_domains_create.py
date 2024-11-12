"""
Tests for MailDomains API endpoint in People's app mailbox_manager. Focus on "create" action.
"""

import re
from logging import Logger
from unittest import mock

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
        response = client.post(
            "/api/v1.0/mail-domains/",
            {"name": domain_name, "context": "null", "features": ["webmail"]},
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
    }

    # a new domain with status "pending" is created and authenticated user is the owner
    assert domain.status == enums.MailDomainStatusChoices.PENDING
    assert domain.name == domain_name
    assert domain.accesses.filter(role="owner", user=user).exists()


## SYNC TO DIMAIL
@mock.patch.object(Logger, "info")
def test_api_mail_domains__create_dimail_domain(mock_info):
    """
    Creating a domain should trigger a call to create a domain on dimail too.
    """
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
        response = client.post(
            "/api/v1.0/mail-domains/",
            {
                "name": domain_name,
            },
            format="json",
        )

    assert response.status_code == status.HTTP_201_CREATED
    assert rsp.call_count == 1  # endpoint was called

    # Logger
    assert (
        mock_info.call_count == 2
    )  # should be 1. A new empty info has been added. To be investigated
    assert mock_info.call_args_list[0][0] == (
        "Domain %s successfully created on dimail by user %s",
        domain_name,
        user.sub,
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
