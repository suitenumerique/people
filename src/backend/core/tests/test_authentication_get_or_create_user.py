"""Unit tests for the `get_or_create_user` function."""

from django.core.exceptions import SuspiciousOperation

import pytest

from core import models
from core.authentication import OIDCAuthenticationBackend
from core.factories import IdentityFactory

pytestmark = pytest.mark.django_db


def test_authentication_getter_existing_user_no_email(
    django_assert_num_queries, monkeypatch
):
    """
    If an existing user matches the user's info sub, the user should be returned.
    """

    klass = OIDCAuthenticationBackend()

    # Create a user and its identity
    identity = IdentityFactory(name=None)

    # Create multiple identities for a user
    for _ in range(5):
        IdentityFactory(user=identity.user)

    def get_userinfo_mocked(*args):
        return {"sub": identity.sub}

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked)

    with django_assert_num_queries(1):
        user = klass.get_or_create_user(
            access_token="test-token", id_token=None, payload=None
        )

    identity.refresh_from_db()
    assert user == identity.user


def test_authentication_getter_existing_user_with_email(
    django_assert_num_queries, monkeypatch
):
    """
    When the user's info contains an email and targets an existing user,
    """
    klass = OIDCAuthenticationBackend()

    identity = IdentityFactory(name="John Doe")

    # Create multiple identities for a user
    for _ in range(5):
        IdentityFactory(user=identity.user)

    assert models.User.objects.count() == 1

    def get_userinfo_mocked(*args):
        return {
            "sub": identity.sub,
            "email": identity.email,
            "first_name": "John",
            "last_name": "Doe",
        }

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked)

    # Only 1 query because email and names have not changed
    with django_assert_num_queries(1):
        user = klass.get_or_create_user(
            access_token="test-token", id_token=None, payload=None
        )

    assert models.User.objects.get() == user


@pytest.mark.parametrize(
    "first_name, last_name, email",
    [
        ("Jack", "Doe", "john.doe@example.com"),
        ("John", "Duy", "john.doe@example.com"),
        ("John", "Doe", "jack.duy@example.com"),
        ("Jack", "Duy", "jack.duy@example.com"),
    ],
)
def test_authentication_getter_existing_user_change_fields(
    first_name, last_name, email, django_assert_num_queries, monkeypatch
):
    """
    It should update the email or name fields on the identity when they change.
    The email on the user should not be changed.
    """
    klass = OIDCAuthenticationBackend()

    identity = IdentityFactory(name="John Doe", email="john.doe@example.com")
    user_email = identity.user.admin_email

    # Create multiple identities for a user
    for _ in range(5):
        IdentityFactory(user=identity.user)

    assert models.User.objects.count() == 1

    def get_userinfo_mocked(*args):
        return {
            "sub": identity.sub,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        }

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked)

    # One and only one additional update query when a field has changed
    with django_assert_num_queries(2):
        user = klass.get_or_create_user(
            access_token="test-token", id_token=None, payload=None
        )

    identity.refresh_from_db()
    assert identity.email == email
    assert identity.name == f"{first_name:s} {last_name:s}"

    assert models.User.objects.count() == 1
    assert user == identity.user
    assert user.admin_email == user_email


def test_authentication_getter_new_user_no_email(monkeypatch):
    """
    If no user matches the user's info sub, a user should be created.
    User's info doesn't contain an email, created user's email should be empty.
    """
    klass = OIDCAuthenticationBackend()

    def get_userinfo_mocked(*args):
        return {"sub": "123"}

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked)

    user = klass.get_or_create_user(
        access_token="test-token", id_token=None, payload=None
    )

    identity = user.identities.get()
    assert identity.sub == "123"
    assert identity.email is None

    assert user.admin_email is None
    assert user.password == "!"
    assert models.User.objects.count() == 1


def test_authentication_getter_new_user_with_email(monkeypatch):
    """
    If no user matches the user's info sub, a user should be created.
    User's email and name should be set on the identity.
    The "email" field on the User model should not be set as it is reserved for staff users.
    """
    klass = OIDCAuthenticationBackend()

    email = "people@example.com"

    def get_userinfo_mocked(*args):
        return {"sub": "123", "email": email, "first_name": "John", "last_name": "Doe"}

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked)

    user = klass.get_or_create_user(
        access_token="test-token", id_token=None, payload=None
    )

    identity = user.identities.get()
    assert identity.sub == "123"
    assert identity.email == email
    assert identity.name == "John Doe"

    assert user.admin_email is None
    assert models.User.objects.count() == 1


def test_models_oidc_user_getter_invalid_token(django_assert_num_queries, monkeypatch):
    """The user's info doesn't contain a sub."""
    klass = OIDCAuthenticationBackend()

    def get_userinfo_mocked(*args):
        return {
            "test": "123",
        }

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked)

    with (
        django_assert_num_queries(0),
        pytest.raises(
            SuspiciousOperation,
            match="User info contained no recognizable user identification",
        ),
    ):
        klass.get_or_create_user(access_token="test-token", id_token=None, payload=None)

    assert models.User.objects.exists() is False
