"""
Test users API endpoints in the People core app: focus on "retrieve" action
"""

import pytest
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_405_METHOD_NOT_ALLOWED,
)
from rest_framework.test import APIClient

from core import factories, models
from core.factories import TeamAccessFactory

from mailbox_manager.factories import MailDomainAccessFactory

pytestmark = pytest.mark.django_db


def test_api_users_retrieve_me_anonymous():
    """Anonymous users should not be allowed to list users."""
    factories.UserFactory.create_batch(2)
    client = APIClient()
    response = client.get("/api/v1.0/users/me/")
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_users_retrieve_me_authenticated():
    """Authenticated users should be able to retrieve their own user via the "/users/me" path."""
    user = factories.UserFactory(with_organization=True)

    client = APIClient()
    client.force_login(user)

    # Define profile contact
    factories.ContactFactory(owner=user, user=user)

    factories.UserFactory.create_batch(2)
    response = client.get(
        "/api/v1.0/users/me/",
    )

    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "id": str(user.id),
        "name": str(user.name),
        "email": str(user.email),
        "language": user.language,
        "timezone": str(user.timezone),
        "is_device": False,
        "is_staff": False,
        "abilities": {
            "contacts": {"can_create": True, "can_view": True},
            "mailboxes": {"can_create": False, "can_view": False},
            "teams": {"can_create": True, "can_view": True},
        },
        "organization": {
            "id": str(user.organization.pk),
            "name": user.organization.name,
            "registration_id_list": user.organization.registration_id_list,
        },
    }


def test_api_users_retrieve_me_authenticated_abilities(settings):
    """
    Authenticated users should be able to retrieve their own user via the "/users/me" path
    with the proper abilities.
    """
    settings.FEATURES = {
        "TEAMS_DISPLAY": False,
        "TEAMS_CREATE": True,
        "CONTACTS_DISPLAY": True,
        "CONTACTS_CREATE": True,
        "MAILBOXES_CREATE": True,
    }
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    # Define profile contact
    factories.ContactFactory(owner=user, user=user)

    factories.UserFactory.create_batch(2)

    # Test the mailboxes abilities
    mail_domain_access = MailDomainAccessFactory(user=user)

    response = client.get("/api/v1.0/users/me/")

    assert response.status_code == HTTP_200_OK
    assert response.json()["abilities"] == {
        "contacts": {"can_create": True, "can_view": True},
        "mailboxes": {"can_create": True, "can_view": True},
        "teams": {"can_create": False, "can_view": False},
    }

    # Test the teams abilities - user is not an admin/owner
    team_access = TeamAccessFactory(user=user, role=models.RoleChoices.MEMBER)
    response = client.get("/api/v1.0/users/me/")

    assert response.status_code == HTTP_200_OK
    assert response.json()["abilities"] == {
        "contacts": {"can_create": True, "can_view": True},
        "mailboxes": {"can_create": True, "can_view": True},
        "teams": {"can_create": False, "can_view": False},
    }

    # Test the teams abilities - user is an admin/owner
    team_access.role = models.RoleChoices.ADMIN
    team_access.save()

    response = client.get("/api/v1.0/users/me/")

    assert response.status_code == HTTP_200_OK
    assert response.json()["abilities"] == {
        "contacts": {"can_create": True, "can_view": True},
        "mailboxes": {"can_create": True, "can_view": True},
        "teams": {"can_create": True, "can_view": True},
    }

    # Test the mailboxes abilities - user has no mail domain access anymore
    mail_domain_access.delete()

    response = client.get("/api/v1.0/users/me/")

    assert response.status_code == HTTP_200_OK
    assert response.json()["abilities"] == {
        "contacts": {"can_create": True, "can_view": True},
        "mailboxes": {"can_create": False, "can_view": False},
        "teams": {"can_create": True, "can_view": True},
    }


def test_api_users_retrieve_anonymous():
    """Anonymous users should not be allowed to retrieve a user."""
    client = APIClient()
    user = factories.UserFactory()
    response = client.get(f"/api/v1.0/users/{user.id!s}/")

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_users_retrieve_authenticated_self():
    """
    Authenticated users should be allowed to retrieve their own user.
    The returned object should not contain the password.
    """
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    response = client.get(
        f"/api/v1.0/users/{user.id!s}/",
    )
    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
    assert response.json() == {"detail": 'Method "GET" not allowed.'}


def test_api_users_retrieve_authenticated_other():
    """
    Authenticated users should be able to retrieve another user's detail view with
    limited information.
    """
    user, other_user = factories.UserFactory.create_batch(2)

    client = APIClient()
    client.force_login(user)

    response = client.get(
        f"/api/v1.0/users/{other_user.id!s}/",
    )
    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
    assert response.json() == {"detail": 'Method "GET" not allowed.'}
