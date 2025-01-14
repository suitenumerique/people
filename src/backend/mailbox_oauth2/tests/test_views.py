"""Tests for the mailbox_oauth2.views module."""

import datetime

from django.utils import timezone

import pytest

from core import factories as core_factories

from mailbox_manager import factories

pytestmark = pytest.mark.django_db


def test_login_view_options(client):
    """Test the OPTIONS method on the login view."""
    response = client.options("/api/v1.0/login/")

    assert response.status_code == 200
    assert response.headers == {
        "Content-Type": "application/json",
        "Vary": "Accept, Authorization, origin, Accept-Language, Cookie",
        "Allow": "POST, OPTIONS",
        "Content-Length": "209",
        "X-Frame-Options": "DENY",
        "Content-Language": "en-us",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "same-origin",
        "Cross-Origin-Opener-Policy": "same-origin",
    }


def test_login_view_authorize(client):
    """Test the login view with valid data."""
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
    assert client.session.get_expiry_date() < timezone.now() + datetime.timedelta(
        minutes=1
    )

    assert response.headers == {
        "Content-Type": "application/json",
        "Vary": "Accept, Authorization, Cookie, origin, Accept-Language",
        "Allow": "POST, OPTIONS",
        "Content-Length": "36",
        "X-Frame-Options": "DENY",
        "Content-Language": "en-us",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "same-origin",
        "Cross-Origin-Opener-Policy": "same-origin",
    }


@pytest.mark.parametrize(
    "email, password, status_code, response_json",
    [
        ("", "password", 400, {"email": ["This field may not be blank."]}),
        (
            "email@test.com",
            "",
            400,
            {"password": ["This field may not be blank."]},
        ),
    ],
)
def test_login_view_invalid_data(client, email, password, status_code, response_json):
    """Test the login view with invalid data."""
    response = client.post("/api/v1.0/login/", {"email": email, "password": password})

    assert response.status_code == status_code
    assert response.json() == response_json
