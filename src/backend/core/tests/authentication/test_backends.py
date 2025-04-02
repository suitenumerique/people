"""Unit tests for the Authentication Backends."""

from django.contrib.auth import get_user_model
from django.core.exceptions import SuspiciousOperation
from django.test import RequestFactory, override_settings

import pytest
from rest_framework.exceptions import AuthenticationFailed

from core import factories, models
from core.authentication.backends import (
    AccountServiceAuthentication,
    OIDCAuthenticationBackend,
)

pytestmark = pytest.mark.django_db
User = get_user_model()


def test_authentication_getter_existing_user_no_email(
    django_assert_num_queries, monkeypatch
):
    """
    If an existing user matches the user's info sub, the user should be returned.
    """

    klass = OIDCAuthenticationBackend()
    user = factories.UserFactory()

    def get_userinfo_mocked(*args):
        return {"sub": user.sub}

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked)

    with django_assert_num_queries(1):
        authenticated_user = klass.get_or_create_user(
            access_token="test-token", id_token=None, payload=None
        )

    assert user == authenticated_user


def test_authentication_getter_existing_user_with_email(
    django_assert_num_queries, monkeypatch
):
    """
    When the user's info contains an email and targets an existing user,
    """
    klass = OIDCAuthenticationBackend()

    user = factories.UserFactory(name="John Doe", with_organization=True)

    def get_userinfo_mocked(*args):
        return {
            "sub": user.sub,
            "email": user.email,
            "first_name": "John",
            "last_name": "Doe",
        }

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked)

    # Only 1 query because email and names have not changed
    with django_assert_num_queries(1):
        authenticated_user = klass.get_or_create_user(
            access_token="test-token", id_token=None, payload=None
        )

    assert user == authenticated_user


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
    It should update the email or name fields on the user when they change.
    """
    klass = OIDCAuthenticationBackend()
    user = factories.UserFactory(
        name="John Doe", email="john.doe@example.com", with_organization=True
    )

    def get_userinfo_mocked(*args):
        return {
            "sub": user.sub,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        }

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked)

    # One and only one additional update query when a field has changed
    with django_assert_num_queries(2):
        authenticated_user = klass.get_or_create_user(
            access_token="test-token", id_token=None, payload=None
        )

    assert user == authenticated_user
    user.refresh_from_db()
    assert user.email == email
    assert user.name == f"{first_name:s} {last_name:s}"


def test_authentication_getter_existing_user_keep_fields(
    django_assert_num_queries, monkeypatch
):
    """
    Falsy values in claim should not update the user's fields.
    """
    klass = OIDCAuthenticationBackend()
    user = factories.UserFactory(
        name="John Doe", email="john.doe@example.com", with_organization=True
    )

    def get_userinfo_mocked(*args):
        return {
            "sub": user.sub,
            "email": None,
            "first_name": "",
            "last_name": "",
        }

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked)

    # No field changed no more query
    with django_assert_num_queries(1):
        authenticated_user = klass.get_or_create_user(
            access_token="test-token", id_token=None, payload=None
        )

    assert user == authenticated_user
    user.refresh_from_db()
    assert user.email == "john.doe@example.com"
    assert user.name == "John Doe"


def test_authentication_getter_existing_user_via_email(
    django_assert_num_queries, monkeypatch
):
    """
    If an existing user doesn't match the sub but matches the email,
    the user should be returned.
    """

    klass = OIDCAuthenticationBackend()
    db_user = factories.UserFactory(with_organization=True)

    def get_userinfo_mocked(*args):
        return {"sub": "123", "email": db_user.email}

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked)

    with django_assert_num_queries(3):  # user by email + user by sub + update sub
        user = klass.get_or_create_user(
            access_token="test-token", id_token=None, payload=None
        )

    assert user == db_user


def test_authentication_getter_existing_user_no_fallback_to_email(
    settings, monkeypatch
):
    """
    When the "OIDC_FALLBACK_TO_EMAIL_FOR_IDENTIFICATION" setting is set to False,
    the system should not match users by email, even if the email matches.
    """

    klass = OIDCAuthenticationBackend()
    db_user = factories.UserFactory()

    # Set the setting to False
    settings.OIDC_FALLBACK_TO_EMAIL_FOR_IDENTIFICATION = False

    def get_userinfo_mocked(*args):
        return {"sub": "123", "email": db_user.email}

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked)

    user = klass.get_or_create_user(
        access_token="test-token", id_token=None, payload=None
    )

    # Since the sub doesn't match, it should create a new user
    assert models.User.objects.count() == 2
    assert user != db_user
    assert user.sub == "123"


def test_authentication_getter_new_user_no_email(monkeypatch):
    """
    If no user matches the user's info sub, a user should not be created without email
    nor organization registration ID.
    """
    klass = OIDCAuthenticationBackend()

    def get_userinfo_mocked(*args):
        return {"sub": "123"}  # No email, no organization registration ID

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked)

    with (
        pytest.raises(
            SuspiciousOperation,
            match="Claims contained no recognizable organization identification",
        ),
    ):
        klass.get_or_create_user(access_token="test-token", id_token=None, payload=None)


def test_authentication_getter_new_user_with_email(monkeypatch):
    """
    If no user matches the user's info sub, a user should be created.
    User's email and name should be set on the user.
    """
    klass = OIDCAuthenticationBackend()
    email = "people@example.com"

    def get_userinfo_mocked(*args):
        return {"sub": "123", "email": email, "first_name": "John", "last_name": "Doe"}

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked)

    user = klass.get_or_create_user(
        access_token="test-token", id_token=None, payload=None
    )

    assert user.sub == "123"
    assert user.email == email
    assert user.name == "John Doe"
    assert user.has_usable_password() is False
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


def test_authentication_getter_existing_disabled_user_via_sub(
    django_assert_num_queries, monkeypatch
):
    """
    If an existing user matches the sub but is disabled,
    an error should be raised and a user should not be created.
    """

    klass = OIDCAuthenticationBackend()
    db_user = factories.UserFactory(name="John Doe", is_active=False)

    def get_userinfo_mocked(*args):
        return {
            "sub": db_user.sub,
            "email": db_user.email,
            "first_name": "John",
            "last_name": "Doe",
        }

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked)

    with (
        django_assert_num_queries(1),
        pytest.raises(SuspiciousOperation, match="User account is disabled"),
    ):
        klass.get_or_create_user(access_token="test-token", id_token=None, payload=None)

    assert models.User.objects.count() == 1


def test_authentication_getter_existing_disabled_user_via_email(
    django_assert_num_queries, monkeypatch
):
    """
    If an existing user does not matches the sub but match the email and is disabled,
    an error should be raised and a user should not be created.
    """

    klass = OIDCAuthenticationBackend()
    db_user = factories.UserFactory(name="John Doe", is_active=False)

    def get_userinfo_mocked(*args):
        return {
            "sub": "random",
            "email": db_user.email,
            "first_name": "John",
            "last_name": "Doe",
        }

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked)

    with (
        django_assert_num_queries(2),
        pytest.raises(SuspiciousOperation, match="User account is disabled"),
    ):
        klass.get_or_create_user(access_token="test-token", id_token=None, payload=None)

    assert models.User.objects.count() == 1


def test_authentication_getter_new_user_with_email_new_organization(monkeypatch):
    """
    If no user matches the user's info sub, a user should be created.
    If the corresponding organization doesn't exist, it should be created.
    """
    klass = OIDCAuthenticationBackend()
    email = "people@example.com"

    def get_userinfo_mocked(*args):
        return {"sub": "123", "email": email, "first_name": "John", "last_name": "Doe"}

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked)

    user = klass.get_or_create_user(
        access_token="test-token", id_token=None, payload=None
    )

    assert user.organization is not None
    assert user.organization.domain_list == ["example.com"]
    assert user.organization.registration_id_list == []


@pytest.mark.parametrize(
    "registration_id_setting,expected_registration_id_list,expected_domain_list",
    [
        (None, [], ["example.com"]),
        ("missing-claim", [], ["example.com"]),
        ("registration_number", ["12345678901234"], []),
    ],
)
def test_authentication_getter_new_user_with_registration_id_new_organization(
    monkeypatch,
    settings,
    registration_id_setting,
    expected_registration_id_list,
    expected_domain_list,
):
    """
    If no user matches the user's info sub, a user should be created.
    If the corresponding organization doesn't exist, it should be created.
    """
    settings.OIDC_ORGANIZATION_REGISTRATION_ID_FIELD = registration_id_setting

    klass = OIDCAuthenticationBackend()
    email = "people@example.com"

    def get_userinfo_mocked(*args):
        return {
            "sub": "123",
            "email": email,
            "first_name": "John",
            "last_name": "Doe",
            "registration_number": "12345678901234",
        }

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked)

    user = klass.get_or_create_user(
        access_token="test-token", id_token=None, payload=None
    )

    assert user.organization is not None
    assert user.organization.domain_list == expected_domain_list
    assert user.organization.registration_id_list == expected_registration_id_list


def test_authentication_getter_existing_user_via_email_update_organization(
    django_assert_num_queries, monkeypatch
):
    """
    If an existing user already exists without organization, the organization must be updated.
    """

    klass = OIDCAuthenticationBackend()
    db_user = factories.UserFactory(name="John Doe", email="toto@my-domain.com")

    def get_userinfo_mocked(*args):
        return {
            "sub": db_user.sub,
            "email": db_user.email,
            "first_name": "John",
            "last_name": "Doe",
        }

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked)

    with django_assert_num_queries(9):
        user = klass.get_or_create_user(
            access_token="test-token", id_token=None, payload=None
        )

    assert user == db_user
    assert user.organization is not None
    assert user.organization.domain_list == ["my-domain.com"]


def test_authentication_getter_existing_user_with_registration_id(
    monkeypatch,
    settings,
):
    """
    Authenticate a user who already exists with an organization registration ID.

    This asserts the "update_user_if_needed" does not fail when the claim
    contains the organization registration ID (or any value not present in the
    User model).
    """
    settings.OIDC_ORGANIZATION_REGISTRATION_ID_FIELD = "registration_number"

    klass = OIDCAuthenticationBackend()
    _existing_user = factories.UserFactory(
        sub="123",
        name="John Doe",
        email="people@example.com",
    )

    def get_userinfo_mocked(*args):
        return {
            "sub": "123",
            "email": "people@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "registration_number": "12345678901234",
        }

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", get_userinfo_mocked)

    user = klass.get_or_create_user(
        access_token="test-token", id_token=None, payload=None
    )

    assert user.organization is not None
    assert user.organization.registration_id_list == ["12345678901234"]


@override_settings(ACCOUNT_SERVICE_SCOPES=["la-suite-list-organizations-siret"])
def test_account_service_authenticate_valid_api_key():
    """Test the authenticate method with a valid API key."""
    request = RequestFactory().get("/")
    account_service = factories.AccountServiceFactory(
        name="test_service",
        api_key="test_api_key_123",
        scopes=["la-suite-list-organizations-siret"],
    )
    request.headers = {"Authorization": f"ApiKey {account_service.api_key}"}

    result = AccountServiceAuthentication().authenticate(request)

    assert result is not None
    assert result[0] == account_service
    assert result[1] == account_service.api_key


def test_account_service_authenticate_missing_api_key():
    """Test the authenticate method with a missing API key."""
    request = RequestFactory().get("/")
    request.headers = {}

    result = AccountServiceAuthentication().authenticate(request)

    assert result is None


def test_account_service_authenticate_invalid_api_key():
    """Test the authenticate method with an invalid API key."""
    request = RequestFactory().get("/")
    request.headers = {"Authorization": "ApiKey invalid_key"}

    with pytest.raises(AuthenticationFailed):
        AccountServiceAuthentication().authenticate(request)


@override_settings(ACCOUNT_SERVICE_SCOPES=["la-suite-list-organizations-siret"])
def test_account_service_authenticate_invalid_header():
    """Test the authenticate method with an invalid header."""
    request = RequestFactory().get("/")
    account_service = factories.AccountServiceFactory(
        name="test_service",
        api_key="test_api_key_123",
        scopes=["la-suite-list-organizations-siret"],
    )
    request.headers = {"Authorization": f"Bearer {account_service.api_key}"}

    with pytest.raises(AuthenticationFailed):
        AccountServiceAuthentication().authenticate(request)

    request.headers = {"Authorization": account_service.api_key}

    with pytest.raises(AuthenticationFailed):
        AccountServiceAuthentication().authenticate(request)
