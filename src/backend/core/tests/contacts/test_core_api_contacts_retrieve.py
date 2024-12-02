"""
Test contacts API endpoints in People's core app.
"""

import pytest
from rest_framework.test import APIClient

from core import factories

pytestmark = pytest.mark.django_db


def test_api_contacts_retrieve_anonymous():
    """Anonymous users should not be allowed to retrieve a user."""
    client = APIClient()
    contact = factories.ContactFactory()
    response = client.get(f"/api/v1.0/contacts/{contact.id!s}/")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_contacts_retrieve_authenticated_owned():
    """
    Authenticated users should be allowed to retrieve a contact they own.
    """
    user = factories.UserFactory()
    contact = factories.ContactFactory(owner=user)

    client = APIClient()
    client.force_login(user)

    response = client.get(f"/api/v1.0/contacts/{contact.id!s}/")

    assert response.status_code == 200
    assert response.json() == {
        "id": str(contact.id),
        "override": None,
        "owner": str(contact.owner.id),
        "data": contact.data,
        "full_name": contact.full_name,
        "notes": "",
        "short_name": contact.short_name,
    }


def test_api_contacts_retrieve_authenticated_public():
    """
    Authenticated users should be able to retrieve public contacts.
    """
    user = factories.UserFactory()
    contact = factories.BaseContactFactory()

    client = APIClient()
    client.force_login(user)

    response = client.get(f"/api/v1.0/contacts/{contact.id!s}/")
    assert response.status_code == 200
    assert response.json() == {
        "id": str(contact.id),
        "override": None,
        "owner": None,
        "data": contact.data,
        "full_name": contact.full_name,
        "notes": "",
        "short_name": contact.short_name,
    }


def test_api_contacts_retrieve_authenticated_other():
    """
    Authenticated users should not be allowed to retrieve another user's contacts.
    """
    user = factories.UserFactory()
    contact = factories.ContactFactory()

    client = APIClient()
    client.force_login(user)

    response = client.get(f"/api/v1.0/contacts/{contact.id!s}/")
    assert response.status_code == 403
    assert response.json() == {
        "detail": "You do not have permission to perform this action."
    }
