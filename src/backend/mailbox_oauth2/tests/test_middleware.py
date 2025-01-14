"""
Tests for the mailbox_oauth2.middleware.one_time_email_authenticated_session
middleware.
"""

import pytest
from oauth2_provider.models import Application

from core import factories as core_factories

from mailbox_manager import factories

pytestmark = pytest.mark.django_db


@pytest.fixture(name="authorize_data")
def authorize_data_fixture():
    """Return the authorize data for the OIDC IdP process."""
    yield {
        "scope": "openid",
        "state": (
            "3C0yk2i25wrx6fNf9zn9287idFqFHGsGIu7UhuJaP0I"
            ".xYBWCFWCFmQ.hpSB0Fd0TmS8MP7cfFiVjw"
            ".eyJydSI6Imh0dHBzOi8vZGVzay4xMjcuMC4wLjEubml"
            "wLmlvL2FwaS92MS4wL2NhbGxiYWNrLyIsInJ0IjoiY29"
            "kZSIsInN0IjoiZ2MzazVSdzREZ0tySERBbHlYaW9vaXg"
            "wa2IzVkMyMTMifQ"
        ),
        "response_type": "code",
        "client_id": "people-idp",
        "redirect_uri": "https://test",
        "acr_values": "eidas1",
        "code_challenge": "36Tcgz62tUu7XvNj_g_jYu6IBi-j7BL-5ZwkW-rI9qc",
        "code_challenge_method": "S256",
        "nonce": "9CTyx0RNzP6kkywLyK6pwQ",
    }


def test_one_time_email_authenticated_session_flow_unallowed_url(client):
    """
    Test the middleware with a user that is authenticated during the
    OIDC IdP process cannot access random pages.
    """
    organization = core_factories.OrganizationFactory(with_registration_id=True)
    domain = factories.MailDomainEnabledFactory(
        organization=organization, name="example.com"
    )
    factories.MailboxEnabledFactory(domain=domain, local_part="user")

    response = client.post(
        "/api/v1.0/login/", {"email": "user@example.com", "password": "password"}
    )
    assert response.status_code == 200

    # assert the user has a session
    assert not client.session.is_empty()

    response = client.get("/api/v1.0/users/me/")
    assert response.status_code == 400

    # assert the user has no more session
    assert client.session.is_empty()


def test_one_time_email_authenticated_session_flow_allowed_url(client, authorize_data):
    """
    Test the middleware with a user that is authenticated during the
    OIDC IdP process can access the OIDC authorize page.
    """
    organization = core_factories.OrganizationFactory(with_registration_id=True)
    domain = factories.MailDomainEnabledFactory(
        organization=organization, name="example.com"
    )
    mailbox = factories.MailboxEnabledFactory(domain=domain, local_part="user")

    response = client.post(
        "/api/v1.0/login/", {"email": "user@example.com", "password": "password"}
    )
    assert response.status_code == 200

    # assert the user has a session
    assert not client.session.is_empty()

    # to properly test the /o/authorize/ we need to setup OIDC identity provider
    Application.objects.create(
        name="people-idp",
        client_id="people-idp",
        redirect_uris="https://test",
        client_type=Application.CLIENT_CONFIDENTIAL,
        authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
    )

    response = client.get(
        f"/o/authorize/?{'&'.join(f'{k}={v}' for k, v in authorize_data.items())}"
    )
    assert response.status_code == 200
    assert response.context["user"] == mailbox

    # assert the user has a session
    assert not client.session.is_empty()

    response = client.post(
        "/o/authorize/",
        authorize_data,
    )
    assert response.status_code == 302

    # assert the user has no more session
    assert client.session.is_empty()


def test_one_time_email_authenticated_session_flow_allowed_url_skip_authorization(
    client,
    authorize_data,
):
    """
    Test the middleware with a user that is authenticated during the
    OIDC IdP process can access the OIDC authorize page.
    """
    organization = core_factories.OrganizationFactory(with_registration_id=True)
    domain = factories.MailDomainEnabledFactory(
        organization=organization, name="example.com"
    )
    factories.MailboxEnabledFactory(domain=domain, local_part="user")

    response = client.post(
        "/api/v1.0/login/", {"email": "user@example.com", "password": "password"}
    )
    assert response.status_code == 200

    # assert the user has a session
    assert not client.session.is_empty()

    # to properly test the /o/authorize/ we need to setup OIDC identity provider
    Application.objects.create(
        name="people-idp",
        client_id="people-idp",
        redirect_uris="https://test",
        client_type=Application.CLIENT_CONFIDENTIAL,
        authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        skip_authorization=True,
    )

    response = client.get(
        f"/o/authorize/?{'&'.join(f'{k}={v}' for k, v in authorize_data.items())}"
    )
    assert response.status_code == 302

    # assert the user has no more session
    assert client.session.is_empty()
