"""
Tests for MailDomains API endpoint in People's app mailbox_manager. Focus on "create" action.
"""

import json
import logging
import re

import pytest
import responses
from requests.exceptions import HTTPError
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories, models
from mailbox_manager.tests.fixtures.dimail import (
    CHECK_DOMAIN_BROKEN,
    CHECK_DOMAIN_OK,
    DOMAIN_SPEC,
)

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


@responses.activate
def test_api_mail_domains__create_authenticated():
    """
    Authenticated users should be able to create mail domains
    and should automatically be added as owner of the newly created domain.
    """
    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    domain_name = "test.domain.fr"

    responses.add(
        responses.POST,
        re.compile(r".*/domains/"),
        body=str(
            {
                "name": domain_name,
            }
        ),
        status=status.HTTP_201_CREATED,
        content_type="application/json",
    )
    responses.add(
        responses.POST,
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
    responses.add(
        responses.POST,
        re.compile(r".*/allows/"),
        body=str({"user": "request-user-sub", "domain": str(domain_name)}),
        status=status.HTTP_201_CREATED,
        content_type="application/json",
    )
    body_content_domain1 = CHECK_DOMAIN_BROKEN.copy()
    body_content_domain1["name"] = domain_name
    responses.add(
        responses.GET,
        re.compile(rf".*/domains/{domain_name}/check/"),
        body=json.dumps(body_content_domain1),
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        re.compile(rf".*/domains/{domain_name}/spec/"),
        body=json.dumps(DOMAIN_SPEC),
        status=status.HTTP_200_OK,
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
        "status": enums.MailDomainStatusChoices.ACTION_REQUIRED,
        "created_at": domain.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": domain.updated_at.isoformat().replace("+00:00", "Z"),
        "abilities": domain.get_abilities(user),
        "count_mailboxes": 0,
        "support_email": domain.support_email,
        "last_check_details": body_content_domain1,
        "action_required_details": {
            "cname_imap": "Il faut un CNAME 'imap.example.fr' qui renvoie vers "
            "'imap.ox.numerique.gouv.fr.'",
            "cname_smtp": "Le CNAME pour 'smtp.example.fr' n'est pas bon, "
            "il renvoie vers 'ns0.ovh.net.' et je veux 'smtp.ox.numerique.gouv.fr.'",
            "cname_webmail": "Il faut un CNAME 'webmail.example.fr' qui "
            "renvoie vers 'webmail.ox.numerique.gouv.fr.'",
            "dkim": "Il faut un DKIM record, avec la bonne clef",
            "mx": "Je veux que le MX du domaine soit mx.ox.numerique.gouv.fr., "
            "or je trouve example-fr.mail.protection.outlook.com.",
            "spf": "Le SPF record ne contient pas include:_spf.ox.numerique.gouv.fr",
        },
        "expected_config": DOMAIN_SPEC,
    }

    # a new domain with status "action required" is created and authenticated user is the owner
    assert domain.status == enums.MailDomainStatusChoices.ACTION_REQUIRED
    assert domain.last_check_details == body_content_domain1
    assert domain.name == domain_name
    assert domain.accesses.filter(role="owner", user=user).exists()


@responses.activate
def test_api_mail_domains__create_authenticated__dimail_failure(caplog):
    """
    Despite a dimail failure for user and/or allow creation,
    an authenticated user should be able to create a mail domain
    and should automatically be added as owner of the newly created domain.
    """
    caplog.set_level(logging.ERROR)
    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    domain_name = "test.domain.fr"

    responses.add(
        responses.POST,
        re.compile(r".*/domains/"),
        body=str(
            {
                "name": domain_name,
            }
        ),
        status=status.HTTP_201_CREATED,
        content_type="application/json",
    )
    responses.add(
        responses.POST,
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
    responses.add(
        responses.POST,
        re.compile(r".*/allows/"),
        body=str({"user": "request-user-sub", "domain": str(domain_name)}),
        status=status.HTTP_403_FORBIDDEN,
        content_type="application/json",
    )
    dimail_error = {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "Not authorized",
    }
    responses.add(
        responses.GET,
        re.compile(rf".*/domains/{domain_name}/check/"),
        body=json.dumps(dimail_error),
        status=dimail_error["status_code"],
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
        "last_check_details": None,
        "action_required_details": {},
        "expected_config": None,
    }

    # a new domain with status "failed" is created and authenticated user is the owner
    assert domain.status == enums.MailDomainStatusChoices.FAILED
    assert domain.name == domain_name
    assert domain.accesses.filter(role="owner", user=user).exists()
    assert caplog.records[0].levelname == "ERROR"
    assert "Not authorized" in caplog.records[0].message


## SYNC TO DIMAIL
@responses.activate
def test_api_mail_domains__create_dimail_domain(caplog):
    """
    Creating a domain should trigger a call to create a domain on dimail too.
    """
    caplog.set_level(logging.INFO)

    user = core_factories.UserFactory()
    client = APIClient()
    client.force_login(user)
    domain_name = "test.fr"

    responses.add(
        responses.POST,
        re.compile(r".*/domains/"),
        body=str(
            {
                "name": domain_name,
            }
        ),
        status=status.HTTP_201_CREATED,
        content_type="application/json",
    )
    responses.add(
        responses.POST,
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
    responses.add(
        responses.POST,
        re.compile(r".*/allows/"),
        body=str({"user": "request-user-sub", "domain": str(domain_name)}),
        status=status.HTTP_201_CREATED,
        content_type="application/json",
    )

    body_content_domain1 = CHECK_DOMAIN_OK.copy()
    body_content_domain1["name"] = domain_name
    responses.add(
        responses.GET,
        re.compile(rf".*/domains/{domain_name}/check/"),
        body=json.dumps(body_content_domain1),
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        re.compile(rf".*/domains/{domain_name}/spec/"),
        body=json.dumps(DOMAIN_SPEC),
        status=status.HTTP_200_OK,
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

    # Logger
    log_messages = [msg.message for msg in caplog.records]
    assert (
        f"Domain {domain_name} successfully created on dimail by user {user.sub}"
        in log_messages
    )
    assert f'[DIMAIL] User "{user.sub}" successfully created on dimail' in log_messages
    assert (
        f'[DIMAIL] Permissions granted for user "{user.sub}" on domain {domain_name}.'
        in log_messages
    )


@responses.activate
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
    responses.add(
        responses.POST,
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
    responses.add(
        responses.POST,
        re.compile(r".*/allows/"),
        body=str({"user": "request-user-sub", "domain": str(domain_name)}),
        status=status.HTTP_201_CREATED,
        content_type="application/json",
    )
    responses.add(
        responses.POST,
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

        assert response.status_code == dimail_error["status_code"]
        assert response.json() == {"detail": dimail_error["detail"]}

    # check logs
    record = caplog.records[0]
    assert record.levelname == "ERROR"
    assert (
        record.message
        == "[DIMAIL] unexpected error : 409 {'detail': 'Domain already exists'}"
    )
