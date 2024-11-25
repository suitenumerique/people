"""
Test contacts API endpoints in People's core app.
"""

from django.test.utils import override_settings

import pytest
from rest_framework.test import APIClient

from core import factories, models
from core.api.client import serializers

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


def test_api_contacts_list_anonymous():
    """Anonymous users should not be allowed to list contacts."""
    factories.ContactFactory.create_batch(2)

    response = APIClient().get("/api/v1.0/contacts/")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_contacts_list_authenticated_no_query():
    """
    Authenticated users should be able to list contacts without applying a query.
    Profile and base contacts should be excluded.
    """
    user = factories.UserFactory()
    contact = factories.ContactFactory(owner=user)
    user.profile_contact = contact
    user.save()

    # Let's have 5 contacts in database:
    assert user.profile_contact is not None  # Excluded because profile contact
    base_contact = factories.BaseContactFactory()  # Excluded because overridden
    factories.ContactFactory(
        base=base_contact
    )  # Excluded because belongs to other user
    contact2 = factories.ContactFactory(
        base=base_contact, owner=user, full_name="Bernard"
    )  # Included

    client = APIClient()
    client.force_login(user)

    response = client.get("/api/v1.0/contacts/")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(contact2.id),
            "base": str(base_contact.id),
            "owner": str(contact2.owner.id),
            "data": contact2.data,
            "full_name": contact2.full_name,
            "short_name": contact2.short_name,
        },
    ]


def test_api_contacts_list_authenticated_by_full_name():
    """
    Authenticated users should be able to search users with a case insensitive and
    partial query on the full name.
    """
    user = factories.UserFactory()

    dave = factories.BaseContactFactory(full_name="David Bowman")
    nicole = factories.BaseContactFactory(full_name="Nicole Foole")
    frank = factories.BaseContactFactory(full_name="Frank Poole")
    factories.BaseContactFactory(full_name="Heywood Floyd")

    # Full query should work
    client = APIClient()
    client.force_login(user)

    response = client.get("/api/v1.0/contacts/?q=David%20Bowman")

    assert response.status_code == 200
    contact_ids = [contact["id"] for contact in response.json()]
    assert contact_ids == [str(dave.id)]

    # Partial query should work
    response = client.get("/api/v1.0/contacts/?q=ank")

    assert response.status_code == 200
    contact_ids = [contact["id"] for contact in response.json()]
    assert contact_ids == [str(frank.id)]

    response = client.get("/api/v1.0/contacts/?q=ole")

    assert response.status_code == 200
    contact_ids = [contact["id"] for contact in response.json()]
    assert contact_ids == [str(frank.id), str(nicole.id)]

    response = client.get("/api/v1.0/contacts/?q=ool")

    assert response.status_code == 200
    contact_ids = [contact["id"] for contact in response.json()]
    assert contact_ids == [str(frank.id), str(nicole.id)]


def test_api_contacts_list_authenticated_uppercase_content():
    """Upper case content should be found by lower case query."""
    user = factories.UserFactory()

    dave = factories.BaseContactFactory(full_name="EEE", short_name="AAA")

    # Unaccented full name
    client = APIClient()
    client.force_login(user)

    response = client.get("/api/v1.0/contacts/?q=eee")

    assert response.status_code == 200
    contact_ids = [contact["id"] for contact in response.json()]
    assert contact_ids == [str(dave.id)]

    # Unaccented short name
    response = client.get("/api/v1.0/contacts/?q=aaa")

    assert response.status_code == 200
    contact_ids = [contact["id"] for contact in response.json()]
    assert contact_ids == [str(dave.id)]


def test_api_contacts_list_authenticated_capital_query():
    """Upper case query should find lower case content."""
    user = factories.UserFactory()

    dave = factories.BaseContactFactory(full_name="eee", short_name="aaa")

    client = APIClient()
    client.force_login(user)

    # Unaccented full name
    response = client.get("/api/v1.0/contacts/?q=EEE")

    assert response.status_code == 200
    contact_ids = [contact["id"] for contact in response.json()]
    assert contact_ids == [str(dave.id)]

    # Unaccented short name
    response = client.get("/api/v1.0/contacts/?q=AAA")

    assert response.status_code == 200
    contact_ids = [contact["id"] for contact in response.json()]
    assert contact_ids == [str(dave.id)]


def test_api_contacts_list_authenticated_accented_content():
    """Accented content should be found by unaccented query."""
    user = factories.UserFactory()

    dave = factories.BaseContactFactory(full_name="ééé", short_name="ààà")

    client = APIClient()
    client.force_login(user)

    # Unaccented full name
    response = client.get("/api/v1.0/contacts/?q=eee")

    assert response.status_code == 200
    contact_ids = [contact["id"] for contact in response.json()]
    assert contact_ids == [str(dave.id)]

    # Unaccented short name
    response = client.get("/api/v1.0/contacts/?q=aaa")

    assert response.status_code == 200
    contact_ids = [contact["id"] for contact in response.json()]
    assert contact_ids == [str(dave.id)]


def test_api_contacts_list_authenticated_accented_query():
    """Accented query should find unaccented content."""
    user = factories.UserFactory()

    dave = factories.BaseContactFactory(full_name="eee", short_name="aaa")

    client = APIClient()
    client.force_login(user)

    # Unaccented full name
    response = client.get("/api/v1.0/contacts/?q=ééé")

    assert response.status_code == 200
    contact_ids = [contact["id"] for contact in response.json()]
    assert contact_ids == [str(dave.id)]

    # Unaccented short name
    response = client.get("/api/v1.0/contacts/?q=ààà")

    assert response.status_code == 200
    contact_ids = [contact["id"] for contact in response.json()]
    assert contact_ids == [str(dave.id)]


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
        "base": str(contact.base.id),
        "owner": str(contact.owner.id),
        "data": contact.data,
        "full_name": contact.full_name,
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
        "base": None,
        "owner": None,
        "data": contact.data,
        "full_name": contact.full_name,
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
    """Anonymous users should be able to create users."""
    user = factories.UserFactory(profile_contact=None)

    client = APIClient()
    client.force_login(user)

    response = client.post(
        "/api/v1.0/contacts/",
        {
            "full_name": "David Bowman",
            "short_name": "Dave",
        },
        format="json",
    )
    assert response.status_code == 400
    assert models.Contact.objects.exists() is False

    assert response.json() == {"base": ["This field is required."]}


def test_api_contacts_create_authenticated_successful():
    """Authenticated users should be able to create contacts."""
    user = factories.UserFactory(profile_contact=None)
    base_contact = factories.BaseContactFactory()

    client = APIClient()
    client.force_login(user)

    # Existing override for another user should not interfere
    factories.ContactFactory(base=base_contact)

    response = client.post(
        "/api/v1.0/contacts/",
        {
            "base": str(base_contact.id),
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
        "base": str(base_contact.id),
        "data": CONTACT_DATA,
        "full_name": "David Bowman",
        "owner": str(user.id),
        "short_name": "Dave",
    }

    assert contact.full_name == "David Bowman"
    assert contact.short_name == "Dave"
    assert contact.data == CONTACT_DATA
    assert contact.base == base_contact
    assert contact.owner == user


@override_settings(ALLOW_API_USER_CREATE=True)
def test_api_contacts_create_authenticated_existing_override():
    """
    Trying to create a contact for base contact that is already overridden by the user
    should receive a 400 error.
    """
    user = factories.UserFactory(profile_contact=None)
    base_contact = factories.BaseContactFactory()
    factories.ContactFactory(base=base_contact, owner=user)

    client = APIClient()
    client.force_login(user)

    response = client.post(
        "/api/v1.0/contacts/",
        {
            "base": str(base_contact.id),
            "full_name": "David Bowman",
            "short_name": "Dave",
            "data": CONTACT_DATA,
        },
        format="json",
    )

    assert response.status_code == 400
    assert models.Contact.objects.count() == 2

    assert response.json() == {
        "__all__": ["Contact with this Owner and Base already exists."]
    }


def test_api_contacts_update_anonymous():
    """Anonymous users should not be allowed to update a contact."""
    contact = factories.ContactFactory()
    old_contact_values = serializers.ContactSerializer(instance=contact).data

    new_contact_values = serializers.ContactSerializer(
        instance=factories.ContactFactory()
    ).data
    new_contact_values["base"] = str(factories.ContactFactory().id)
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
    user = factories.UserFactory(profile_contact=None)

    client = APIClient()
    client.force_login(user)

    contact = factories.ContactFactory(owner=user)  # Owned by the logged-in user
    old_contact_values = serializers.ContactSerializer(instance=contact).data

    new_contact_values = serializers.ContactSerializer(
        instance=factories.ContactFactory()
    ).data
    new_contact_values["base"] = str(factories.ContactFactory().id)

    response = client.put(
        f"/api/v1.0/contacts/{contact.id!s}/",
        new_contact_values,
        format="json",
    )

    assert response.status_code == 200

    contact.refresh_from_db()
    contact_values = serializers.ContactSerializer(instance=contact).data
    for key, value in contact_values.items():
        if key in ["base", "owner", "id"]:
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

    contact = factories.ContactFactory(owner=user)
    user.profile_contact = contact
    user.save()

    old_contact_values = serializers.ContactSerializer(instance=contact).data
    new_contact_values = serializers.ContactSerializer(
        instance=factories.ContactFactory()
    ).data
    new_contact_values["base"] = str(factories.ContactFactory().id)

    response = client.put(
        f"/api/v1.0/contacts/{contact.id!s}/",
        new_contact_values,
        format="json",
    )

    assert response.status_code == 200
    contact.refresh_from_db()
    contact_values = serializers.ContactSerializer(instance=contact).data
    for key, value in contact_values.items():
        if key in ["base", "owner", "id"]:
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
    new_contact_values["base"] = str(factories.ContactFactory().id)

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
    assert models.Contact.objects.count() == 4


def test_api_contacts_delete_list_authenticated():
    """Authenticated users should not be allowed to delete a list of contacts."""
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    factories.ContactFactory.create_batch(2)

    response = client.delete("/api/v1.0/contacts/")

    assert response.status_code == 405
    assert models.Contact.objects.count() == 4


def test_api_contacts_delete_anonymous():
    """Anonymous users should not be allowed to delete a contact."""
    contact = factories.ContactFactory()

    client = APIClient()
    response = client.delete(f"/api/v1.0/contacts/{contact.id!s}/")

    assert response.status_code == 401
    assert models.Contact.objects.count() == 2


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
    assert models.Contact.objects.count() == 1
    assert models.Contact.objects.filter(id=contact.id).exists() is False


def test_api_contacts_delete_authenticated_profile():
    """
    Authenticated users should be allowed to delete their profile contact.
    """
    user = factories.UserFactory()
    contact = factories.ContactFactory(owner=user, base=None)
    user.profile_contact = contact
    user.save()

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
    assert models.Contact.objects.count() == 2
