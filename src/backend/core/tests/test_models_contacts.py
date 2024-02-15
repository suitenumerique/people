"""
Unit tests for the Contact model
"""
from django.core.exceptions import ValidationError

import pytest

from core import factories

pytestmark = pytest.mark.django_db


def test_models_contacts_str_full_name():
    """The str representation should be the contact's full name."""
    contact = factories.ContactFactory(full_name="David Bowman")
    assert str(contact) == "David Bowman"


def test_models_contacts_str_short_name():
    """The str representation should be the contact's short name if full name is not set."""
    contact = factories.ContactFactory(full_name=None, short_name="Dave")
    assert str(contact) == "Dave"


def test_models_contacts_base_self():
    """A contact should not point to itself as a base contact."""
    contact = factories.ContactFactory()
    contact.base = contact

    with pytest.raises(ValidationError) as excinfo:
        contact.save()

    error_message = (
        "{'__all__': ['A contact cannot point to a base contact that itself points to a "
        "base contact.', 'A contact cannot be based on itself.']}"
    )
    assert str(excinfo.value) == error_message


def test_models_contacts_base_to_base():
    """A contact should not point to a base contact that is itself derived from a base contact."""
    contact = factories.ContactFactory()

    with pytest.raises(ValidationError) as excinfo:
        factories.ContactFactory(base=contact)

    error_message = (
        "{'__all__': ['A contact cannot point to a base contact that itself points to a "
        "base contact.']}"
    )
    assert str(excinfo.value) == error_message


def test_models_contacts_owner_base_unique():
    """There should be only one contact deriving from a given base contact for a given owner."""
    contact = factories.ContactFactory()

    with pytest.raises(ValidationError) as excinfo:
        factories.ContactFactory(base=contact.base, owner=contact.owner)

    assert (
        str(excinfo.value)
        == "{'__all__': ['Contact with this Owner and Base already exists.']}"
    )


def test_models_contacts_base_not_owned():
    """A contact cannot have a base and not be owned."""
    with pytest.raises(ValidationError) as excinfo:
        factories.ContactFactory(owner=None)

    assert (
        str(excinfo.value)
        == "{'__all__': ['A contact overriding a base contact must be owned.']}"
    )


def test_models_contacts_profile_not_owned():
    """A contact cannot be defined as profile for a user if is not owned."""
    base_contact = factories.ContactFactory(owner=None, base=None)

    with pytest.raises(ValidationError) as excinfo:
        factories.UserFactory(profile_contact=base_contact)

    assert (
        str(excinfo.value)
        == "{'__all__': ['Users can only declare as profile a contact they own.']}"
    )


def test_models_contacts_profile_owned_by_other():
    """A contact cannot be defined as profile for a user if is owned by another user."""
    contact = factories.ContactFactory()

    with pytest.raises(ValidationError) as excinfo:
        factories.UserFactory(profile_contact=contact)

    assert (
        str(excinfo.value)
        == "{'__all__': ['Users can only declare as profile a contact they own.']}"
    )


def test_models_contacts_data_valid():
    """Contact information matching the jsonschema definition should be valid"""
    factories.ContactFactory(
        data={
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
                {"type": "LinkedIn", "value": "https://www.linkedin.com/in/johndoe"},
                {"type": "Facebook", "value": "https://www.facebook.com/in/johndoe"},
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
    )


def test_models_contacts_data_invalid():
    """Invalid contact information should be rejected with a clear error message."""
    with pytest.raises(ValidationError) as excinfo:
        factories.ContactFactory(
            data={
                "emails": [
                    {"type": "invalid type", "value": "john.doe@work.com"},
                ],
            }
        )

    assert str(excinfo.value) == (
        "{'data': [\"Validation error in 'emails.0.type': 'invalid type' is not one of ['Work', "
        "'Home', 'Other']\"]}"
    )
