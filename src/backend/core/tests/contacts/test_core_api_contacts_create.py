"""
Test contacts API endpoints in People's core app.
"""

from django.test.utils import override_settings

import pytest
from rest_framework.test import APIClient

from core import factories, models

pytestmark = pytest.mark.django_db


CONTACT_DATA = {
    "emails": [
        {"type": "Work", "value": "john.doe@work.com"},
        {"type": "Home", "value": "john.doe@home.com"},
    ],
    "phones": [
        {"type": "Work", "value": "(123) 456-7890"},
        {"type": "Other", "value": "(987) 654-3210"},
    ],
    "addresses": [
        {
            "type": "Home",
            "street": "123 Main St",
            "city": "Cityville",
            "state": "CA",
            "zip": "12345",
            "country": "USA",
        }
    ],
    "links": [
        {"type": "Blog", "value": "http://personalwebsite.com"},
        {"type": "Website", "value": "http://workwebsite.com"},
    ],
    "customFields": {"custom_field_1": "value1", "custom_field_2": "value2"},
    "organizations": [
        {
            "name": "ACME Corporation",
            "department": "IT",
            "jobTitle": "Software Engineer",
        },
        {
            "name": "XYZ Ltd",
            "department": "Marketing",
            "jobTitle": "Marketing Specialist",
        },
    ],
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
