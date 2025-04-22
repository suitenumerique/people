"""
Test contacts API endpoints in People's core app.
"""

import pytest
from rest_framework.test import APIClient

from core import factories
from core.api.client import serializers

pytestmark = pytest.mark.django_db


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


def test_api_contacts_update_authenticated_owned(django_assert_num_queries):
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

    with django_assert_num_queries(14):
        # user, 2x contact, user, 3x check, update contact, 3x savepoint/release
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
