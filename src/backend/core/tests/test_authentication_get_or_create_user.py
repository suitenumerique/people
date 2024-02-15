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
    identity = IdentityFactory()

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
    it should update the email on the identity but not on the user.
    """
    klass = OIDCAuthenticationBackend()

    identity = IdentityFactory()

    # Create multiple identities for a user
    for _ in range(5):
        IdentityFactory(user=identity.user)

    user_email = identity.user.email
    assert models.User.objects.count() == 1

    def get_userinfo_mocked(*args):
        return {"sub": identity.sub, "email": identity.email}

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked)

    # Only 1 query if the email has not changed
    with django_assert_num_queries(1):
        user = klass.get_or_create_user(
            access_token="test-token", id_token=None, payload=None
        )

    new_email = "test@fooo.com"

    def get_userinfo_mocked_new_email(*args):
        return {"sub": identity.sub, "email": new_email}

    monkeypatch.setattr(
        OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked_new_email
    )

    # Additional update query if the email has changed
    with django_assert_num_queries(2):
        user = klass.get_or_create_user(
            access_token="test-token", id_token=None, payload=None
        )

    identity.refresh_from_db()
    assert identity.email == new_email

    assert models.User.objects.count() == 1
    assert user == identity.user
    assert user.email == user_email


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

    assert user.email is None
    assert user.password == "!"
    assert models.User.objects.count() == 1


def test_authentication_getter_new_user_with_email(monkeypatch):
    """
    If no user matches the user's info sub, a user should be created.
    User's info contains an email, created user's email should be set.
    """
    klass = OIDCAuthenticationBackend()

    email = "people@example.com"

    def get_userinfo_mocked(*args):
        return {"sub": "123", "email": email}

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked)

    user = klass.get_or_create_user(
        access_token="test-token", id_token=None, payload=None
    )

    identity = user.identities.get()
    assert identity.sub == "123"
    assert identity.email == email

    assert user.email == email
    assert models.User.objects.count() == 1


def test_models_oidc_user_getter_invalid_token(django_assert_num_queries, monkeypatch):
    """The user's info doesn't contain a sub."""
    klass = OIDCAuthenticationBackend()

    def get_userinfo_mocked(*args):
        return {
            "test": "123",
        }

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked)

    with django_assert_num_queries(0), pytest.raises(
        SuspiciousOperation,
        match="User info contained no recognizable user identification",
    ):
        klass.get_or_create_user(access_token="test-token", id_token=None, payload=None)

    assert models.User.objects.exists() is False
