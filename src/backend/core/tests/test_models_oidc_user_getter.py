"""Unit tests for the `oidc_user_getter` function."""
import pytest
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import AccessToken

from core import factories, models

pytestmark = pytest.mark.django_db


def test_models_oidc_user_getter_existing_user_no_email(django_assert_num_queries):
    """
    When a valid token is passed, an existing user matching the token's sub should be returned.
    """
    identity = factories.IdentityFactory()
    factories.IdentityFactory(user=identity.user)  # another identity for the user
    token = AccessToken()
    token["sub"] = str(identity.sub)

    with django_assert_num_queries(1):
        user = models.oidc_user_getter(token)

    identity.refresh_from_db()
    assert user == identity.user


def test_models_oidc_user_getter_existing_user_with_email(django_assert_num_queries):
    """
    When the valid token passed contains an email and targets an existing user,
    it should update the email on the identity but not on the user.
    """
    identity = factories.IdentityFactory()
    factories.IdentityFactory(user=identity.user)  # another identity for the user
    user_email = identity.user.email
    assert models.User.objects.count() == 1

    token = AccessToken()
    token["sub"] = str(identity.sub)

    # Only 1 query if the email has not changed
    token["email"] = identity.email
    with django_assert_num_queries(1):
        user = models.oidc_user_getter(token)

    # Additional update query if the email has changed
    new_email = "people@example.com"
    token["email"] = new_email
    with django_assert_num_queries(2):
        user = models.oidc_user_getter(token)

    identity.refresh_from_db()
    assert identity.email == new_email

    assert models.User.objects.count() == 1
    assert user == identity.user
    assert user.email == user_email


def test_models_oidc_user_getter_new_user_no_email():
    """
    When a valid token is passed, a user should be created if the sub
    does not match any existing user.
    """
    token = AccessToken()
    token["sub"] = "123"

    user = models.oidc_user_getter(token)

    identity = user.identities.get()
    assert identity.sub == "123"
    assert identity.email is None

    assert user.email is None
    assert user.password == "!"
    assert models.User.objects.count() == 1


def test_models_oidc_user_getter_new_user_with_email():
    """
    When the valid token passed contains an email and a new user is created,
    the email should be set on the user and on the identity.
    """
    email = "people@example.com"
    token = AccessToken()
    token["sub"] = "123"
    token["email"] = email

    user = models.oidc_user_getter(token)

    identity = user.identities.get()
    assert identity.sub == "123"
    assert identity.email == email

    assert user.email == email
    assert models.User.objects.count() == 1


def test_models_oidc_user_getter_invalid_token(django_assert_num_queries):
    """The token passed in argument should contain the configured user id claim."""
    token = AccessToken()

    with django_assert_num_queries(0), pytest.raises(
        InvalidToken, match="Token contained no recognizable user identification"
    ):
        models.oidc_user_getter(token)

    assert models.User.objects.exists() is False
