"""
Unit tests for the User model
"""

from unittest import mock

from django.core.exceptions import ValidationError

import pytest

from core import factories, models

pytestmark = pytest.mark.django_db


def test_models_users_str():
    """
    user str representation should return name or email when avalaible.
    Otherwise, it should return the sub.
    """
    user = factories.UserFactory()
    assert str(user) == user.name

    no_name_user = factories.UserFactory(name=None)
    assert str(no_name_user) == no_name_user.email

    no_name_no_email_user = factories.UserFactory(name=None, email=None)
    assert str(no_name_no_email_user) == f"User {no_name_no_email_user.sub}"


def test_models_users_id_unique():
    """The "id" field should be unique."""
    user = factories.UserFactory()
    with pytest.raises(ValidationError, match="User with this Id already exists."):
        factories.UserFactory(id=user.id)


def test_models_users_sub_null():
    """The 'sub' field should not be null."""
    with pytest.raises(ValidationError, match="This field cannot be null.") as excinfo:
        models.User.objects.create(sub=None, password="password")

    assert str(excinfo.value) == "{'sub': ['This field cannot be null.']}"


def test_models_users_sub_blank():
    """The 'sub' field should not be blank."""
    with pytest.raises(ValidationError, match="This field cannot be blank.") as excinfo:
        models.User.objects.create(sub="", password="password")

    assert str(excinfo.value) == "{'sub': ['This field cannot be blank.']}"


def test_models_users_sub_unique():
    """The 'sub' field should be unique."""
    user = factories.UserFactory()
    with pytest.raises(ValidationError, match="User with this Sub already exists."):
        models.User.objects.create(sub=user.sub, password="password")


def test_models_users_sub_max_length():
    """The 'sub' field should be 255 characters maximum."""
    factories.UserFactory(sub="a" * 255)
    with pytest.raises(ValidationError) as excinfo:
        factories.UserFactory(sub="a" * 256)

    assert (
        str(excinfo.value)
        == "{'sub': ['Ensure this value has at most 255 characters (it has 256).']}"
    )


def test_models_users_sub_special_characters():
    """The 'sub' field should accept periods, dashes, +, @ and underscores."""
    user = factories.UserFactory(sub="dave.bowman-1+2@hal_9000")
    assert user.sub == "dave.bowman-1+2@hal_9000"


def test_models_users_sub_spaces():
    """The 'sub' field should not accept spaces."""
    with pytest.raises(ValidationError) as excinfo:
        factories.UserFactory(sub="a b")

    assert str(excinfo.value) == (
        "{'sub': ['Enter a valid sub. This value may contain only letters, numbers, "
        "and @/./+/-/_ characters.']}"
    )


def test_models_users_sub_upper_case():
    """The 'sub' field should accept upper case characters."""
    user = factories.UserFactory(sub="John")
    assert user.sub == "John"


def test_models_users_sub_ascii():
    """The 'sub' field should accept non ASCII letters."""
    user = factories.UserFactory(sub="rené")
    assert user.sub == "rené"


def test_models_users_email_not_required():
    """The 'email' field can be blank."""
    user = factories.UserFactory(email=None)
    assert user.email is None


def test_models_users_email_normalization():
    """The 'email' field should be automatically normalized upon saving."""
    user = factories.UserFactory()
    user.email = "Thomas.Jefferson@Example.com"
    user.save()

    assert user.email == "Thomas.Jefferson@example.com"


def test_models_users_email_several_null():
    """Several users with a null value for the "email" field can co-exist."""
    factories.UserFactory(email=None)
    models.User.objects.create(email=None, sub="123", password="foo.")

    assert models.User.objects.filter(email__isnull=True).count() == 2


def test_models_users_email_not_unique():
    """The 'email' field should not necessarily be unique among users."""
    user = factories.UserFactory()
    other_user = factories.UserFactory(email=user.email)

    assert user.email == other_user.email


def test_models_users_profile_not_owned():
    """A user cannot declare as profile a contact that not is owned."""
    user = factories.UserFactory()
    contact = factories.ContactFactory(override=None, owner=None)

    user.profile_contact = contact
    with pytest.raises(ValidationError) as excinfo:
        user.save()

    assert (
        str(excinfo.value)
        == "{'__all__': ['Users can only declare as profile a contact they own.']}"
    )


def test_models_users_profile_owned_by_other():
    """A user cannot declare as profile a contact that is owned by another user."""
    user = factories.UserFactory()
    contact = factories.ContactFactory()

    user.profile_contact = contact
    with pytest.raises(ValidationError) as excinfo:
        user.save()

    assert (
        str(excinfo.value)
        == "{'__all__': ['Users can only declare as profile a contact they own.']}"
    )


def test_models_users_send_mail_main_existing():
    """The 'email_user' method should send mail to the user's email address."""
    user = factories.UserFactory(email="dave@example.com")
    factories.UserFactory.create_batch(2)

    with mock.patch("django.core.mail.send_mail") as mock_send:
        user.email_user("my subject", "my message")

    mock_send.assert_called_once_with(
        "my subject", "my message", None, ["dave@example.com"]
    )


def test_models_users_send_mail_main_admin():
    """
    The 'email_user' method should send mail to the user's email address.
    """
    user = factories.UserFactory()

    with mock.patch("django.core.mail.send_mail") as mock_send:
        user.email_user("my subject", "my message")

    mock_send.assert_called_once_with("my subject", "my message", None, [user.email])


def test_models_users_send_mail_main_missing():
    """The 'email_user' method should fail if the user has no email address."""
    user = factories.UserFactory(email=None)

    with pytest.raises(ValueError) as excinfo:
        user.email_user("my subject", "my message")

    assert str(excinfo.value) == "You must first set an email for the user."
