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


def test_models_contacts_base_self():
    """A contact should not override itself."""
    contact = factories.ContactFactory()
    contact.override = contact

    with pytest.raises(ValidationError) as excinfo:
        contact.save()

    error_message = (
        "{'__all__': ['A contact cannot override a contact that itself overrides a contact.',"
        " 'A contact cannot override itself.']}"
    )
    assert str(excinfo.value) == error_message


def test_models_contacts_base_to_base():
    """A contact should not override a contact that is itself overrides contact."""
    contact = factories.OverrideContactFactory()

    with pytest.raises(ValidationError) as excinfo:
        factories.OverrideContactFactory(override=contact)

    error_message = (
        "{'__all__': ['A contact cannot override a contact that "
        "itself overrides a contact.']}"
    )
    assert str(excinfo.value) == error_message


def test_models_contacts_owner_base_unique():
    """There should be only one contact overriding a contact for a given owner."""
    contact = factories.OverrideContactFactory()

    with pytest.raises(ValidationError) as excinfo:
        factories.OverrideContactFactory(override=contact.override, owner=contact.owner)

    assert (
        str(excinfo.value)
        == "{'__all__': ['Contact with this Owner and Override already exists.']}"
    )


def test_models_contacts_base_not_owned():
    """A contact cannot override a contact without being owned."""
    with pytest.raises(ValidationError) as excinfo:
        factories.OverrideContactFactory(owner=None)

    assert (
        str(excinfo.value)
        == "{'__all__': ['A contact overriding a base contact must be owned.']}"
    )


def test_models_contacts_profile_not_owned():
    """A contact cannot be defined as profile for a user if is not owned."""
    with pytest.raises(ValidationError) as excinfo:
        factories.ContactFactory(owner=None, user=factories.UserFactory())

    assert (
        str(excinfo.value)
        == "{'__all__': ['Users can only declare as profile a contact they own.']}"
    )


def test_models_contacts_profile_owned_by_other():
    """A contact cannot be defined as profile for a user if is owned by another user."""
    contact = factories.ContactFactory()

    with pytest.raises(ValidationError) as excinfo:
        contact.user = factories.UserFactory()
        contact.save()

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


def test_generate_vcard():
    """Test the vCard generation from contact data."""
    contact = factories.ContactFactory(
        full_name="John Doe",
        short_name="Johnny",
        data={
            "emails": [
                {"type": "Work", "value": "john.doe@work.com"},
                {"type": "Home", "value": "john.doe@home.com"},
            ],
            "phones": [
                {"type": "Mobile", "value": "(123) 456-7890"},
                {"type": "Home", "value": "(987) 654-3210"},
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
                {"type": "Website", "value": "http://workwebsite.com"},
                {"type": "LinkedIn", "value": "https://www.linkedin.com/in/johndoe"},
            ],
            "organizations": [
                {
                    "name": "ACME Corporation",
                    "department": "IT",
                    "jobTitle": "Software Engineer",
                }
            ],
        }
    )

    vcard = contact.generate_vcard()

    assert vcard.split("\n") == ['BEGIN:VCARD\r',
        'VERSION:3.0\r',
        'ADR;TYPE=Home:;;123 Main St;Cityville;CA;12345;USA\r',
        'EMAIL;TYPE=Work:john.doe@work.com\r',
        'EMAIL;TYPE=Home:john.doe@home.com\r',
        'FN:John Doe\r',
        'NICKNAME:Johnny\r',
        'ORG:ACME Corporation;IT\r',
        'TEL;TYPE=Mobile:(123) 456-7890\r',
        'TEL;TYPE=Home:(987) 654-3210\r',
        'TITLE:Software Engineer\r',
        'URL;TYPE=Website:http://workwebsite.com\r',
        'URL;TYPE=LinkedIn:https://www.linkedin.com/in/johndoe\r',
        'END:VCARD\r',
        '',
    ]
