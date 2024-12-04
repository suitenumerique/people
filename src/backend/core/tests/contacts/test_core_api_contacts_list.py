"""
Test contacts API endpoints in People's core app.
"""

import pytest
from rest_framework.test import APIClient

from core import factories

pytestmark = pytest.mark.django_db


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
    Profile and overridden contacts should be excluded.
    """
    organization = factories.OrganizationFactory(with_registration_id=True)
    user = factories.UserFactory(organization=organization)

    # The user's profile contact should be listed (why not)
    user_profile_contact = factories.ContactFactory(
        owner=user, user=user, full_name="Dave Bowman"
    )

    # A contact that belongs to another user should not be listed
    factories.ContactFactory()
    # even if from the same organization
    factories.ContactFactory(owner__organization=organization)

    # A profile contact should not be listed if from another organization
    factories.ProfileContactFactory()

    # A profile contact for someone in the same organization should be listed
    profile_contact = factories.ProfileContactFactory(
        user__organization=organization, full_name="Frank Poole"
    )

    # An overridden contact should not be listed, but the override must be
    overriden_contact = factories.ProfileContactFactory(user__organization=organization)
    override_contact = factories.ContactFactory(
        owner=user, override=overriden_contact, full_name="Nicole Foole"
    )

    client = APIClient()
    client.force_login(user)

    response = client.get("/api/v1.0/contacts/")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(user_profile_contact.pk),
            "override": None,
            "owner": str(user.pk),
            "data": user_profile_contact.data,
            "full_name": user_profile_contact.full_name,
            "notes": "",
            "short_name": user_profile_contact.short_name,
        },
        {
            "id": str(profile_contact.pk),
            "override": None,
            "owner": str(profile_contact.user.pk),
            "data": profile_contact.data,
            "full_name": profile_contact.full_name,
            "notes": "",
            "short_name": profile_contact.short_name,
        },
        {
            "id": str(override_contact.pk),
            "override": str(overriden_contact.pk),
            "owner": str(user.pk),
            "data": override_contact.data,
            "full_name": override_contact.full_name,
            "notes": "",
            "short_name": override_contact.short_name,
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
