"""
Unit tests for the mailbox API
"""

import json
import re
from logging import Logger
from unittest import mock

from django.test.utils import override_settings

import pytest
import responses
from requests.exceptions import HTTPError
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories, models
from mailbox_manager.api.client import serializers
from mailbox_manager.tests.fixtures.dimail import (
    TOKEN_OK,
    response_mailbox_created,
)

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
            body=TOKEN_OK,
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(rf".*/domains/{mail_domain.name}/mailboxes/"),
            body=response_mailbox_created(
                f"{mailbox_values['local_part']}@{mail_domain.name}"
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
        "status": enums.MailboxStatusChoices.ENABLED,
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
            body=TOKEN_OK,
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(rf".*/domains/{mail_domain.name}/mailboxes/"),
            body=response_mailbox_created(
                f"{mailbox_values['local_part']}@{mail_domain.name}"
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
        "status": enums.MailboxStatusChoices.ENABLED,
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


@pytest.mark.parametrize(
    "role",
    [
        enums.MailDomainRoleChoices.OWNER,
        enums.MailDomainRoleChoices.ADMIN,
    ],
)
def test_api_mailboxes__cannot_create_on_disabled_domain(role):
    """Admin and owner users should not be able to create mailboxes for a disabled domain"""
    mail_domain = factories.MailDomainFactory(
        status=enums.MailDomainStatusChoices.DISABLED
    )
    access = factories.MailDomainAccessFactory(role=role, domain=mail_domain)

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
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not models.Mailbox.objects.exists()
    assert response.json() == [
        "You can't create or update a mailbox for a disabled domain."
    ]


def test_api_mailboxes__no_dimail_call_if_mailbox_creation_failed():
    """Duplication case fails on our side at creation step thanks to unique_together
    on Mailbox model and no dimail call should be made."""
    mail_domain = factories.MailDomainEnabledFactory()
    mailbox = factories.MailboxFactory(domain=mail_domain)
    access = factories.MailDomainAccessFactory(
        role=enums.MailDomainRoleChoices.ADMIN, domain=mail_domain
    )

    client = APIClient()
    client.force_login(access.user)

    # now we try to make the same mailbox
    mailbox_data = serializers.MailboxSerializer(mailbox).data
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        rsps.add(
            rsps.GET,
            re.compile(r".*/token/"),
            body=TOKEN_OK,
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        rsps.add(
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
        # try to create duplicate mailbox but django validation does not agree
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # no new mailbox should be created
        assert models.Mailbox.objects.count() == 1
        # no dimail call should be made
        assert len(rsps.calls) == 0


def test_api_mailboxes__same_local_part_on_different_domains():
    """A domain admin should be able to create a mailbox with the same local part
    of another mailbox, on different domain."""
    # a mailbox exists on another domain
    existing_mailbox = factories.MailboxFactory()

    access = factories.MailDomainAccessFactory(
        role=enums.MailDomainRoleChoices.ADMIN,
        domain=factories.MailDomainEnabledFactory(),
    )
    client = APIClient()
    client.force_login(access.user)

    # create a full dict with same local part as another existing mailbox
    mailbox_values = serializers.MailboxSerializer(
        factories.MailboxFactory.build(local_part=existing_mailbox.local_part)
    ).data

    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.GET,
            re.compile(r".*/token/"),
            body=TOKEN_OK,
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(rf".*/domains/{access.domain.name}/mailboxes/"),
            body=response_mailbox_created(
                f"{mailbox_values['local_part']}@{access.domain.name}"
            ),
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )
        response = client.post(
            f"/api/v1.0/mail-domains/{access.domain.slug}/mailboxes/",
            mailbox_values,
            format="json",
        )

    assert response.status_code == status.HTTP_201_CREATED
    assert (
        len(models.Mailbox.objects.filter(local_part=existing_mailbox.local_part)) == 2
    )


@pytest.mark.parametrize(
    "domain_status",
    [
        enums.MailDomainStatusChoices.PENDING,
        enums.MailDomainStatusChoices.FAILED,
    ],
)
def test_api_mailboxes__create_pending_mailboxes(domain_status):
    """
    Admin and owner users should be able to create mailboxes, including on pending and failed
    domains.
    Mailboxes created on pending and failed domains should have the "pending" status
    """
    mail_domain = factories.MailDomainFactory(status=domain_status)
    access = factories.MailDomainAccessFactory(
        role=enums.MailDomainRoleChoices.ADMIN, domain=mail_domain
    )

    client = APIClient()
    client.force_login(access.user)

    mailbox_values = serializers.MailboxSerializer(
        factories.MailboxFactory.build()
    ).data
    with responses.RequestsMock():
        # We add no response in RequestsMock
        # because we expect no outside calls to be made
        response = client.post(
            f"/api/v1.0/mail-domains/{mail_domain.slug}/mailboxes/",
            mailbox_values,
            format="json",
        )
    assert response.status_code == status.HTTP_201_CREATED
    mailbox = models.Mailbox.objects.get()
    assert mailbox.status == "pending"


### REACTING TO DIMAIL-API
### We mock dimail's responses to avoid testing dimail's container too


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


@mock.patch.object(Logger, "error")
def test_api_mailboxes__async_dimail_unauthorized(mock_error):
    """
    Dimail should raise an error if token has been successfully granted
    but mailbox creation request returns a 403.
    i.e. user exists on dimail-api but has no permission on that domain
    """
    # creating all needed objects

    # this access somehow exists solely in our database but not in dimail
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
            body=TOKEN_OK,
            status=status.HTTP_200_OK,  # user is in dimail-api
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(
                rf".*/domains/{access.domain.name}/mailboxes/{mailbox_data['local_part']}"
            ),
            status=status.HTTP_403_FORBIDDEN,
            content_type="application/json",
        )

        response = client.post(
            f"/api/v1.0/mail-domains/{access.domain.slug}/mailboxes/",
            mailbox_data,
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    assert mock_error.call_count == 1
    assert mock_error.call_args_list[0][0] == (
        "[DIMAIL] 403 Forbidden: you cannot access domain %s",
        access.domain.name,
    )


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
    Succesfull 201 response from dimail should trigger mailbox creation on our side.
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
            body=TOKEN_OK,
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        rsp = rsps.add(
            rsps.POST,
            re.compile(rf".*/domains/{access.domain.name}/mailboxes/"),
            body=response_mailbox_created(
                f"{mailbox_data['local_part']}@{access.domain.name}"
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
        "status": enums.MailboxStatusChoices.ENABLED,
    }
    assert mailbox.first_name == mailbox_data["first_name"]
    assert mailbox.last_name == mailbox_data["last_name"]
    assert mailbox.local_part == mailbox_data["local_part"]
    assert mailbox.secondary_email == mailbox_data["secondary_email"]


@override_settings(MAIL_PROVISIONING_API_CREDENTIALS="wrongCredentials")
def test_api_mailboxes__dimail_token_permission_denied(caplog):
    """
    API should raise a clear "permission denied" error
    when receiving a permission denied from dimail upon requesting token.
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
            "detail": "Token denied. Please check your MAIL_PROVISIONING_API_CREDENTIALS."
        }
        # mailbox was created in our side only and in pending status
        mailbox = models.Mailbox.objects.get()
        assert mailbox.status == enums.MailboxStatusChoices.PENDING

        # Check error logger was called
        log_messages = [msg.message for msg in caplog.records]
        assert (
            "[DIMAIL] 403 Forbidden: Could not retrieve a token,\
please check 'MAIL_PROVISIONING_API_CREDENTIALS' setting."
            in log_messages
        )


def test_api_mailboxes__user_unrelated_to_domain():
    """
    API should raise a clear "permission denied" when dimail returns a permission denied
    on mailbox creation. This means token was granted for this user
    but user is not allowed to modify this domain (i.e. does not have a allow)
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
            body=TOKEN_OK,
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
            "detail": "Permission denied. Please check your MAIL_PROVISIONING_API_CREDENTIALS."
        }
        # mailbox was created in our side only and in pending status
        mailbox = models.Mailbox.objects.get()
        assert mailbox.status == enums.MailboxStatusChoices.PENDING


def test_api_mailboxes__handling_dimail_unexpected_error(caplog):
    """
    API should raise a clear error when dimail returns an unexpected response.
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
            body=TOKEN_OK,
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(rf".*/domains/{access.domain.name}/mailboxes/"),
            body='{"detail": "Internal server error"}',
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content_type="application/json",
        )

        with pytest.raises(HTTPError):
            response = client.post(
                f"/api/v1.0/mail-domains/{access.domain.slug}/mailboxes/",
                mailbox_data,
                format="json",
            )
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json() == {
                "detail": "Unexpected response from dimail: {'details': 'Internal server error'}"
            }

        # mailbox was created in our side only and in pending status
        mailbox = models.Mailbox.objects.get()
        assert mailbox.status == enums.MailboxStatusChoices.PENDING

        # Check error logger was called
        assert caplog.records[0].levelname == "ERROR"
        assert (
            caplog.records[0].message
            == "[DIMAIL] unexpected error : 500 {'detail': 'Internal server error'}"
        )


@mock.patch.object(Logger, "error")
@mock.patch.object(Logger, "info")
def test_api_mailboxes__send_correct_logger_infos(mock_info, mock_error):
    """
    Upon requesting mailbox creation, la régie should impersonate
    querying user in dimail and log things correctly.
    """
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
            body=TOKEN_OK,
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(rf".*/domains/{access.domain.name}/mailboxes/"),
            body=response_mailbox_created(
                f"{mailbox_data['local_part']}@{access.domain.name}"
            ),
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )

        response = client.post(
            f"/api/v1.0/mail-domains/{access.domain.slug}/mailboxes/",
            mailbox_data,
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED

        # user sub is sent to payload as a parameter
        assert rsps.calls[0].request.params == {"username": access.user.sub}

    # Logger
    assert not mock_error.called
    # Check all expected log messages are present, order doesn't matter
    expected_messages = {
        ("Token succesfully granted by mail-provisioning API.",),
        (
            "Mailbox successfully created on domain %s by user %s",
            str(access.domain),
            access.user.sub,
        ),
    }
    actual_messages = {args for args, _ in mock_info.call_args_list}
    assert expected_messages.issubset(actual_messages)


@mock.patch.object(Logger, "info")
def test_api_mailboxes__sends_new_mailbox_notification(mock_info):
    """
    Creating a new mailbox should send confirmation email
    to secondary email.
    """
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
            body=TOKEN_OK,
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
        rsps.add(
            rsps.POST,
            re.compile(rf".*/domains/{access.domain.name}/mailboxes/"),
            body=response_mailbox_created(
                f"{mailbox_data['local_part']}@{access.domain}"
            ),
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )
        with mock.patch("django.core.mail.send_mail") as mock_send:
            client.post(
                f"/api/v1.0/mail-domains/{access.domain.slug}/mailboxes/",
                mailbox_data,
                format="json",
            )

        assert mock_send.call_count == 1
        assert mock_send.mock_calls[0][1][0] == "Your new mailbox information"
        assert mock_send.mock_calls[0][1][3][0] == mailbox_data["secondary_email"]

    expected_messages = {
        (
            "Information for mailbox %s sent to %s.",
            f"{mailbox_data['local_part']}@{access.domain.name}",
            mailbox_data["secondary_email"],
        )
    }
    actual_messages = {args for args, _ in mock_info.call_args_list}
    assert expected_messages.issubset(actual_messages)
