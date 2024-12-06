"""
Test contacts API endpoints in People's core app.
"""

import pytest
from rest_framework.test import APIClient

from core import factories, models

pytestmark = pytest.mark.django_db


def test_api_contacts_delete_list_anonymous():
    """Anonymous users should not be allowed to delete a list of contacts."""
    factories.ContactFactory.create_batch(2)

    response = APIClient().delete("/api/v1.0/contacts/")

    assert response.status_code == 401
    assert models.Contact.objects.count() == 2


def test_api_contacts_delete_list_authenticated():
    """Authenticated users should not be allowed to delete a list of contacts."""
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    factories.ContactFactory.create_batch(2)

    response = client.delete("/api/v1.0/contacts/")

    assert response.status_code == 405
    assert models.Contact.objects.count() == 2


def test_api_contacts_delete_anonymous():
    """Anonymous users should not be allowed to delete a contact."""
    contact = factories.ContactFactory()

    client = APIClient()
    response = client.delete(f"/api/v1.0/contacts/{contact.id!s}/")

    assert response.status_code == 401
    assert models.Contact.objects.count() == 1


def test_api_contacts_delete_authenticated_public():
    """
    Authenticated users should not be allowed to delete a public contact.
    """
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    contact = factories.BaseContactFactory()

    response = client.delete(
        f"/api/v1.0/contacts/{contact.id!s}/",
    )

    assert response.status_code == 403
    assert models.Contact.objects.count() == 1


def test_api_contacts_delete_authenticated_owner():
    """
    Authenticated users should be allowed to delete a contact they own.
    """
    user = factories.UserFactory()
    contact = factories.ContactFactory(owner=user)

    client = APIClient()
    client.force_login(user)

    response = client.delete(
        f"/api/v1.0/contacts/{contact.id!s}/",
    )

    assert response.status_code == 204
    assert models.Contact.objects.count() == 0
    assert models.Contact.objects.filter(id=contact.id).exists() is False


def test_api_contacts_delete_authenticated_profile():
    """
    Authenticated users should not be allowed to delete their profile contact.
    """
    user = factories.UserFactory()
    contact = factories.ProfileContactFactory(user=user)

    client = APIClient()
    client.force_login(user)

    response = client.delete(
        f"/api/v1.0/contacts/{contact.id!s}/",
    )

    assert response.status_code == 403
    assert models.Contact.objects.exists() is True


def test_api_contacts_delete_authenticated_other():
    """
    Authenticated users should not be allowed to delete a contact they don't own.
    """
    user = factories.UserFactory()
    contact = factories.ContactFactory()

    client = APIClient()
    client.force_login(user)

    response = client.delete(
        f"/api/v1.0/contacts/{contact.id!s}/",
    )

    assert response.status_code == 403
    assert models.Contact.objects.count() == 1
