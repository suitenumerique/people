"""
Test contacts API endpoints in People's core app.
"""

from django.test.utils import override_settings

import pytest
from rest_framework.test import APIClient

from core import factories, models
from core.api.client import serializers

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


def test_api_contacts_create_anonymous_forbidden():
    """Anonymous users should not be able to create contacts via the API."""
    response = APIClient().post(
        "/api/v1.0/contacts/",
        {
            "full_name": "David",
            "short_name": "Bowman",
        },
    )
    assert response.status_code == 401
    assert not models.Contact.objects.exists()


def test_api_contacts_create_authenticated_missing_base():
    """Authenticated user should be able to create contact without override."""
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    response = client.post(
        "/api/v1.0/contacts/",
        {
            "full_name": "David Bowman",
            "short_name": "Dave",
            "data": {},
        },
        format="json",
    )
    assert response.status_code == 201

    new_contact = models.Contact.objects.get(owner=user)

    assert response.json() == {
        "override": None,
        "data": {},
        "full_name": "David Bowman",
        "id": str(new_contact.pk),
        "notes": "",
        "owner": str(user.pk),
        "short_name": "Dave",
    }


def test_api_contacts_create_authenticated_successful():
    """Authenticated users should be able to create contacts."""
    user = factories.UserFactory()
    base_contact = factories.BaseContactFactory()

    client = APIClient()
    client.force_login(user)

    # Existing override for another user should not interfere
    factories.ContactFactory(override=base_contact)

    response = client.post(
        "/api/v1.0/contacts/",
        {
            "override": str(base_contact.id),
            "full_name": "David Bowman",
            "short_name": "Dave",
            "data": CONTACT_DATA,
        },
        format="json",
    )

    assert response.status_code == 201
    assert models.Contact.objects.count() == 3

    contact = models.Contact.objects.get(owner=user)
    assert response.json() == {
        "id": str(contact.id),
        "override": str(base_contact.id),
        "data": CONTACT_DATA,
        "full_name": "David Bowman",
        "notes": "",
        "owner": str(user.id),
        "short_name": "Dave",
    }

    assert contact.full_name == "David Bowman"
    assert contact.short_name == "Dave"
    assert contact.data == CONTACT_DATA
    assert contact.override == base_contact
    assert contact.owner == user


@override_settings(ALLOW_API_USER_CREATE=True)
def test_api_contacts_create_authenticated_existing_override():
    """
    Trying to create a contact overriding a contact that is already overridden by the user
    should receive a 400 error.
    """
    user = factories.UserFactory()
    base_contact = factories.BaseContactFactory()
    factories.ContactFactory(override=base_contact, owner=user)

    client = APIClient()
    client.force_login(user)

    response = client.post(
        "/api/v1.0/contacts/",
        {
            "override": str(base_contact.id),
            "full_name": "David Bowman",
            "notes": "",
            "short_name": "Dave",
            "data": CONTACT_DATA,
        },
        format="json",
    )

    assert response.status_code == 400
    assert models.Contact.objects.count() == 2

    assert response.json() == {
        "__all__": ["Contact with this Owner and Override already exists."]
    }


def test_api_contacts_create_authenticated_successful_with_notes():
    """Authenticated users should be able to create contacts with notes."""
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    response = client.post(
        "/api/v1.0/contacts/",
        {
            "full_name": "David Bowman",
            "short_name": "Dave",
            "data": CONTACT_DATA,
            "notes": "This is a note",
        },
        format="json",
    )

    assert response.status_code == 201
    assert models.Contact.objects.count() == 1

    contact = models.Contact.objects.get(owner=user)
    assert response.json() == {
        "id": str(contact.id),
        "override": None,
        "data": CONTACT_DATA,
        "full_name": "David Bowman",
        "notes": "This is a note",
        "owner": str(user.id),
        "short_name": "Dave",
    }

    assert contact.full_name == "David Bowman"
    assert contact.short_name == "Dave"
    assert contact.data == CONTACT_DATA
    assert contact.owner == user
    assert contact.notes == "This is a note"


def test_api_contacts_update_anonymous():
    """Anonymous users should not be allowed to update a contact."""
    contact = factories.ContactFactory()
    old_contact_values = serializers.ContactSerializer(instance=contact).data

    new_contact_values = serializers.ContactSerializer(
        instance=factories.ContactFactory()
    ).data
    new_contact_values["override"] = str(factories.ContactFactory().id)
    response = APIClient().put(
        f"/api/v1.0/contacts/{contact.id!s}/",
        new_contact_values,
        format="json",
    )
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }

    contact.refresh_from_db()
    contact_values = serializers.ContactSerializer(instance=contact).data
    assert contact_values == old_contact_values


def test_api_contacts_update_authenticated_owned():
    """
    Authenticated users should be allowed to update their own contacts.
    """
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    contact = factories.ContactFactory(owner=user)  # Owned by the logged-in user
    old_contact_values = serializers.ContactSerializer(instance=contact).data

    new_contact_values = serializers.ContactSerializer(
        instance=factories.ContactFactory()
    ).data
    new_contact_values["override"] = str(factories.ContactFactory().id)

    response = client.put(
        f"/api/v1.0/contacts/{contact.id!s}/",
        new_contact_values,
        format="json",
    )

    assert response.status_code == 200

    contact.refresh_from_db()
    contact_values = serializers.ContactSerializer(instance=contact).data
    for key, value in contact_values.items():
        if key in ["override", "owner", "id"]:
            assert value == old_contact_values[key]
        else:
            assert value == new_contact_values[key]


def test_api_contacts_update_authenticated_profile():
    """
    Authenticated users should be allowed to update their profile contact.
    """
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    contact = factories.ContactFactory(owner=user, user=user)

    old_contact_values = serializers.ContactSerializer(instance=contact).data
    new_contact_values = serializers.ContactSerializer(
        instance=factories.ContactFactory()
    ).data
    new_contact_values["override"] = str(factories.ContactFactory().id)

    response = client.put(
        f"/api/v1.0/contacts/{contact.id!s}/",
        new_contact_values,
        format="json",
    )

    assert response.status_code == 200
    contact.refresh_from_db()
    contact_values = serializers.ContactSerializer(instance=contact).data
    for key, value in contact_values.items():
        if key in ["override", "owner", "id"]:
            assert value == old_contact_values[key]
        else:
            assert value == new_contact_values[key]


def test_api_contacts_update_authenticated_other():
    """
    Authenticated users should not be allowed to update contacts owned by other users.
    """
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    contact = factories.ContactFactory()  # owned by another user
    old_contact_values = serializers.ContactSerializer(instance=contact).data

    new_contact_values = serializers.ContactSerializer(
        instance=factories.ContactFactory()
    ).data
    new_contact_values["override"] = str(factories.ContactFactory().id)

    response = client.put(
        f"/api/v1.0/contacts/{contact.id!s}/",
        new_contact_values,
        format="json",
    )

    assert response.status_code == 403

    contact.refresh_from_db()
    contact_values = serializers.ContactSerializer(instance=contact).data
    assert contact_values == old_contact_values


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
    Authenticated users should be allowed to delete their profile contact.
    """
    user = factories.UserFactory()
    contact = factories.ContactFactory(owner=user, user=user)

    client = APIClient()
    client.force_login(user)

    response = client.delete(
        f"/api/v1.0/contacts/{contact.id!s}/",
    )

    assert response.status_code == 204
    assert models.Contact.objects.exists() is False


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
 
