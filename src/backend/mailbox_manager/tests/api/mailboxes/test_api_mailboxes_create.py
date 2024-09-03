"""
Unit tests for the mailbox API
"""

import json
import re

import pytest
import responses
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories, models
from mailbox_manager.api import serializers

pytestmark = pytest.mark.django_db


def test_api_mailboxes__create_anonymous_forbidden():
    """Anonymous users should not be able to create a new mailbox via the API."""
    mail_domain = factories.MailDomainEnabledFactory()
    mailbox_values = serializers.MailboxSerializer(
        factories.MailboxFactory.build()
    ).data
    response = APIClient().post(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/",
        mailbox_values,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not models.Mailbox.objects.exists()


def test_api_mailboxes__create_authenticated_failure():
    """Authenticated users should not be able to create mailbox
    without specific role on mail domain."""
    user = core_factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    mailbox_values = serializers.MailboxSerializer(
        factories.MailboxFactory.build()
    ).data
    mail_domain = factories.MailDomainEnabledFactory()
    response = client.post(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/",
        mailbox_values,
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not models.Mailbox.objects.exists()


def test_api_mailboxes__create_viewer_failure():
    """Users with viewer role should not be able to create mailbox on the mail domain."""
    mail_domain = factories.MailDomainEnabledFactory()
    access = factories.MailDomainAccessFactory(
        role=enums.MailDomainRoleChoices.VIEWER, domain=mail_domain
    )

    client = APIClient()
    client.force_login(access.user)

    mailbox_values = serializers.MailboxSerializer(
        factories.MailboxFactory.build()
    ).data
    response = client.post(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/",
        mailbox_values,
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not models.Mailbox.objects.exists()


@pytest.mark.parametrize(
    "role",
    [enums.MailDomainRoleChoices.OWNER, enums.MailDomainRoleChoices.ADMIN],
)
def test_api_mailboxes__create_roles_success(role):
    """Users with owner or admin role should be able to create mailbox on the mail domain."""
    mail_domain = factories.MailDomainEnabledFactory()
    access = factories.MailDomainAccessFactory(role=role, domain=mail_domain)

    client = APIClient()
    client.force_login(access.user)

    mailbox_values = serializers.MailboxSerializer(
        factories.MailboxFactory.build()
    ).data
    with responses.RequestsMock() as rsps:
        # Ensure successful response using "responses":
        rsps.add(
            rsps.GET,
            re.compile(r".*/token/"),
            body='{"access_token": "domain_owner_token"}',
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(rf".*/domains/{mail_domain.name}/mailboxes/"),
            body=str(
                {
                    "email": f"{mailbox_values['local_part']}@{mail_domain.name}",
                    "password": "newpass",
                    "uuid": "uuid",
                }
            ),
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )
        response = client.post(
            f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/",
            mailbox_values,
            format="json",
        )

    assert response.status_code == status.HTTP_201_CREATED
    mailbox = models.Mailbox.objects.get()

    assert mailbox.local_part == mailbox_values["local_part"]
    assert mailbox.secondary_email == mailbox_values["secondary_email"]
    assert response.json() == {
        "id": str(mailbox.id),
        "first_name": str(mailbox.first_name),
        "last_name": str(mailbox.last_name),
        "local_part": str(mailbox.local_part),
        "secondary_email": str(mailbox.secondary_email),
    }


@pytest.mark.parametrize(
    "role",
    [enums.MailDomainRoleChoices.OWNER, enums.MailDomainRoleChoices.ADMIN],
)
def test_api_mailboxes__create_with_accent_success(role):
    """Users with proper abilities should be able to create mailbox on the mail domain with a
    first_name accentuated."""
    mail_domain = factories.MailDomainEnabledFactory()
    access = factories.MailDomainAccessFactory(role=role, domain=mail_domain)

    client = APIClient()
    client.force_login(access.user)

    mailbox_values = serializers.MailboxSerializer(
        factories.MailboxFactory.build(first_name="Aimé")
    ).data
    with responses.RequestsMock() as rsps:
        # Ensure successful response using "responses":
        rsps.add(
            rsps.GET,
            re.compile(r".*/token/"),
            body='{"access_token": "domain_owner_token"}',
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(rf".*/domains/{mail_domain.name}/mailboxes/"),
            body=str(
                {
                    "email": f"{mailbox_values['local_part']}@{mail_domain.name}",
                    "password": "newpass",
                    "uuid": "uuid",
                }
            ),
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )
        response = client.post(
            f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/",
            mailbox_values,
            format="json",
        )
    assert response.status_code == status.HTTP_201_CREATED
    mailbox = models.Mailbox.objects.get()

    assert mailbox.local_part == mailbox_values["local_part"]
    assert mailbox.secondary_email == mailbox_values["secondary_email"]
    assert response.json() == {
        "id": str(mailbox.id),
        "first_name": str(mailbox.first_name),
        "last_name": str(mailbox.last_name),
        "local_part": str(mailbox.local_part),
        "secondary_email": str(mailbox.secondary_email),
    }


def test_api_mailboxes__create_administrator_missing_fields():
    """
    Administrator users should not be able to create mailboxes
    without local part or secondary mail.
    """
    mail_domain = factories.MailDomainEnabledFactory()
    access = factories.MailDomainAccessFactory(
        role=enums.MailDomainRoleChoices.ADMIN, domain=mail_domain
    )
    client = APIClient()
    client.force_login(access.user)

    mailbox_values = serializers.MailboxSerializer(
        factories.MailboxFactory.build()
    ).data
    del mailbox_values["local_part"]
    response = client.post(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/",
        mailbox_values,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not models.Mailbox.objects.exists()
    assert response.json() == {"local_part": ["This field is required."]}

    mailbox_values = serializers.MailboxSerializer(
        factories.MailboxFactory.build()
    ).data
    del mailbox_values["secondary_email"]
    response = client.post(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/",
        mailbox_values,
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not models.Mailbox.objects.exists()
    assert response.json() == {"secondary_email": ["This field is required."]}


### SYNC TO PROVISIONING API


def test_api_mailboxes__unrelated_user_provisioning_api_not_called():
    """
    Provisioning API should not be called if an user tries
    to create a mailbox on a domain they have no access to.
    """
    domain = factories.MailDomainEnabledFactory()

    client = APIClient()
    client.force_login(core_factories.UserFactory())  # user with no access
    body_values = serializers.MailboxSerializer(
        factories.MailboxFactory.build(domain=domain)
    ).data
    with responses.RequestsMock():
        # We add no simulated response in RequestsMock
        # because we expected no "outside" calls to be made
        response = client.post(
            f"/api/v1.0/mail-domains/{domain.slug}/mailboxes/",
            body_values,
            format="json",
        )
        # No exception raised by RequestsMock means no call was sent
        # our API blocked the request before sending it
        assert response.status_code == status.HTTP_403_FORBIDDEN


def test_api_mailboxes__domain_viewer_provisioning_api_not_called():
    """
    Provisioning API should not be called if a domain viewer tries
    to create a mailbox on a domain they are not owner/admin of.
    """
    access = factories.MailDomainAccessFactory(
        domain=factories.MailDomainEnabledFactory(),
        user=core_factories.UserFactory(),
        role=enums.MailDomainRoleChoices.VIEWER,
    )

    client = APIClient()
    client.force_login(access.user)
    body_values = serializers.MailboxSerializer(factories.MailboxFactory.build()).data
    with responses.RequestsMock():
        # We add no simulated response in RequestsMock
        # because we expected no "outside" calls to be made
        response = client.post(
            f"/api/v1.0/mail-domains/{access.domain.slug}/mailboxes/",
            body_values,
            format="json",
        )
        # No exception raised by RequestsMock means no call was sent
        # our API blocked the request before sending it
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "role",
    [enums.MailDomainRoleChoices.ADMIN, enums.MailDomainRoleChoices.OWNER],
)
def test_api_mailboxes__domain_owner_or_admin_successful_creation_and_provisioning(
    role,
):
    """
    Domain owner/admin should be able to create mailboxes.
    Provisioning API should be called when owner/admin makes a call.
    Expected response contains new email and password.
    """
    # creating all needed objects
    access = factories.MailDomainAccessFactory(role=role)

    client = APIClient()
    client.force_login(access.user)
    mailbox_data = serializers.MailboxSerializer(
        factories.MailboxFactory.build(domain=access.domain)
    ).data

    with responses.RequestsMock() as rsps:
        # Ensure successful response using "responses":
        rsps.add(
            rsps.GET,
            re.compile(r".*/token/"),
            body='{"access_token": "domain_owner_token"}',
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        rsp = rsps.add(
            rsps.POST,
            re.compile(rf".*/domains/{access.domain.name}/mailboxes/"),
            body=str(
                {
                    "email": f"{mailbox_data['local_part']}@{access.domain.name}",
                    "password": "newpass",
                    "uuid": "uuid",
                }
            ),
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )

        response = client.post(
            f"/api/v1.0/mail-domains/{access.domain.slug}/mailboxes/",
            mailbox_data,
            format="json",
        )

        # Checks payload sent to email-provisioning API
        payload = json.loads(rsps.calls[1].request.body)
        assert payload == {
            "displayName": f"{mailbox_data['first_name']} {mailbox_data['last_name']}",
            "givenName": mailbox_data["first_name"],
            "surName": mailbox_data["last_name"],
        }

        # Checks response
        assert response.status_code == status.HTTP_201_CREATED
        assert rsp.call_count == 1

    mailbox = models.Mailbox.objects.get()
    assert response.json() == {
        "id": str(mailbox.id),
        "first_name": str(mailbox_data["first_name"]),
        "last_name": str(mailbox_data["last_name"]),
        "local_part": str(mailbox_data["local_part"]),
        "secondary_email": str(mailbox_data["secondary_email"]),
    }
    assert mailbox.first_name == mailbox_data["first_name"]
    assert mailbox.last_name == mailbox_data["last_name"]
    assert mailbox.local_part == mailbox_data["local_part"]
    assert mailbox.secondary_email == mailbox_data["secondary_email"]


def test_api_mailboxes__wrong_secret_no_token_error():
    """
    API should raise a clear "permission denied" error
    when receiving a 403_forbidden from dimail.
    """
    # creating all needed objects
    access = factories.MailDomainAccessFactory(role=enums.MailDomainRoleChoices.OWNER)
    access.domain.secret = "nottherealsecret"

    client = APIClient()
    client.force_login(access.user)
    mailbox_data = serializers.MailboxSerializer(
        factories.MailboxFactory.build(domain=access.domain)
    ).data

    with responses.RequestsMock() as rsps:
        # Ensure successful response using "responses":
        rsps.add(
            rsps.GET,
            re.compile(r".*/token/"),
            body='{"details": "Permission denied"}',
            status=status.HTTP_403_FORBIDDEN,
            content_type="application/json",
        )

        response = client.post(
            f"/api/v1.0/mail-domains/{access.domain.slug}/mailboxes/",
            mailbox_data,
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": f"Token denied - Wrong secret on mail domain {access.domain.name}"
        }
        assert not models.Mailbox.objects.exists()


def test_api_mailboxes__secret_unrelated_to_domain():
    """
    API should raise a clear "permission denied"
    when secret allows for a token but is not linked to queried domain on dimail-api.
    """
    # creating all needed objects
    access = factories.MailDomainAccessFactory(role=enums.MailDomainRoleChoices.OWNER)

    client = APIClient()
    client.force_login(access.user)
    mailbox_data = serializers.MailboxSerializer(
        factories.MailboxFactory.build(domain=access.domain)
    ).data

    with responses.RequestsMock() as rsps:
        # Ensure successful response using "responses":
        rsps.add(
            rsps.GET,
            re.compile(r".*/token/"),
            body='{"access_token": "domain_owner_token"}',
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(rf".*/domains/{access.domain.name}/mailboxes/"),
            body='{"details": "Permission denied"}',
            status=status.HTTP_403_FORBIDDEN,
            content_type="application/json",
        )

        response = client.post(
            f"/api/v1.0/mail-domains/{access.domain.slug}/mailboxes/",
            mailbox_data,
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": f"Secret not valid for this domain {access.domain.name}"
        }
        assert not models.Mailbox.objects.exists()


def test_api_mailboxes__handling_dimail_unexpected_error():
    """
    API should raise a clear error when dimail gives an unexpected response.
    """
    # creating all needed objects
    access = factories.MailDomainAccessFactory(role=enums.MailDomainRoleChoices.OWNER)

    client = APIClient()
    client.force_login(access.user)
    mailbox_data = serializers.MailboxSerializer(
        factories.MailboxFactory.build(domain=access.domain)
    ).data

    with responses.RequestsMock() as rsps:
        # Ensure successful response using "responses":
        rsps.add(
            rsps.GET,
            re.compile(r".*/token/"),
            body='{"access_token": "domain_owner_token"}',
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(rf".*/domains/{access.domain.name}/mailboxes/"),
            body='{"details": "Internal server error"}',
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content_type="application/json",
        )

        with pytest.raises(SystemError):
            response = client.post(
                f"/api/v1.0/mail-domains/{access.domain.slug}/mailboxes/",
                mailbox_data,
                format="json",
            )
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json() == {
                "detail": "Unexpected response from dimail: {'details': 'Internal server error'}"
            }
        assert not models.Mailbox.objects.exists()
