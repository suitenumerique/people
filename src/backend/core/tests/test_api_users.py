"""
Test users API endpoints in the People core app.
"""
from unittest import mock

import pytest
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_405_METHOD_NOT_ALLOWED,
)
from rest_framework.test import APIClient

from core import factories, models
from core.api import serializers
from core.api.viewsets import Pagination

pytestmark = pytest.mark.django_db


def test_api_users_list_anonymous():
    """Anonymous users should not be allowed to list users."""
    factories.UserFactory()
    client = APIClient()
    response = client.get("/api/v1.0/users/")
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert "Authentication credentials were not provided." in response.content.decode(
        "utf-8"
    )


def test_api_users_list_authenticated():
    """
    Authenticated users should be able to list all users.
    """
    identity = factories.IdentityFactory()

    client = APIClient()
    client.force_login(identity.user)

    factories.UserFactory.create_batch(2)
    response = client.get(
        "/api/v1.0/users/",
    )
    assert response.status_code == HTTP_200_OK
    assert len(response.json()["results"]) == 3


def test_api_users_authenticated_list_by_email():
    """
    Authenticated users should be able to search users with a case-insensitive and
    partial query on the email.
    """
    user = factories.UserFactory(email="tester@ministry.fr")
    factories.IdentityFactory(user=user, email=user.email)

    client = APIClient()
    client.force_login(user)

    dave = factories.IdentityFactory(email="david.bowman@work.com", is_main=True)
    nicole = factories.IdentityFactory(email="nicole_foole@work.com", is_main=True)
    frank = factories.IdentityFactory(email="frank_poole@work.com", is_main=True)
    factories.IdentityFactory(email="heywood_floyd@work.com", is_main=True)

    # Full query should work
    response = client.get(
        "/api/v1.0/users/?q=david.bowman@work.com",
    )

    assert response.status_code == HTTP_200_OK
    user_ids = [user["id"] for user in response.json()["results"]]
    assert user_ids[0] == str(dave.user.id)

    # Partial query should work
    response = client.get("/api/v1.0/users/?q=fran")

    assert response.status_code == HTTP_200_OK
    user_ids = [user["id"] for user in response.json()["results"]]
    assert user_ids[0] == str(frank.user.id)

    # Result that matches a trigram twice ranks better than result that matches once
    response = client.get("/api/v1.0/users/?q=ole")

    assert response.status_code == HTTP_200_OK
    user_ids = [user["id"] for user in response.json()["results"]]
    # "Nicole Foole" matches twice on "ole"
    assert user_ids == [str(nicole.user.id), str(frank.user.id)]

    # Even with a low similarity threshold, query should match expected emails
    response = client.get("/api/v1.0/users/?q=ool")

    assert response.status_code == HTTP_200_OK
    assert response.json()["results"] == [
        {
            "id": str(nicole.user.id),
            "email": nicole.email,
            "name": nicole.name,
            "is_device": nicole.user.is_device,
            "is_staff": nicole.user.is_staff,
            "language": nicole.user.language,
            "timezone": str(nicole.user.timezone),
        },
        {
            "id": str(frank.user.id),
            "email": frank.email,
            "name": frank.name,
            "is_device": frank.user.is_device,
            "is_staff": frank.user.is_staff,
            "language": frank.user.language,
            "timezone": str(frank.user.timezone),
        },
    ]


def test_api_users_authenticated_list_multiple_identities_single_user():
    """
    User with multiple identities should appear only once in results.
    """
    user = factories.UserFactory(email="tester@ministry.fr")
    factories.IdentityFactory(user=user, email=user.email)

    client = APIClient()
    client.force_login(user)

    dave = factories.UserFactory()
    factories.IdentityFactory(user=dave, email="david.bowman@work.com")
    factories.IdentityFactory(user=dave, email="david.bowman@fun.fr")

    # Full query should work
    response = client.get(
        "/api/v1.0/users/?q=david.bowman@work.com",
    )

    assert response.status_code == HTTP_200_OK
    # A single user is returned, despite similarity matching both emails
    assert response.json()["count"] == 1
    assert response.json()["results"][0]["id"] == str(dave.id)


def test_api_users_authenticated_list_multiple_identities_multiple_users():
    """
    User with multiple identities should be ranked
    on their best matching identity.
    """
    user = factories.UserFactory(email="tester@ministry.fr")
    factories.IdentityFactory(user=user, email=user.email)

    client = APIClient()
    client.force_login(user)

    dave = factories.UserFactory()
    dave_identity = factories.IdentityFactory(
        user=dave, email="david.bowman@work.com", is_main=True
    )
    factories.IdentityFactory(user=dave, email="babibou@ehehe.com")
    davina_identity = factories.IdentityFactory(
        user=factories.UserFactory(), email="davina.bowan@work.com"
    )
    prue_identity = factories.IdentityFactory(
        user=factories.UserFactory(), email="prudence.crandall@work.com"
    )

    # Full query should work
    response = client.get(
        "/api/v1.0/users/?q=david.bowman@work.com",
    )

    assert response.status_code == HTTP_200_OK
    assert response.json()["count"] == 3
    assert response.json()["results"] == [
        {
            "id": str(dave.id),
            "email": dave_identity.email,
            "name": dave_identity.name,
            "is_device": dave_identity.user.is_device,
            "is_staff": dave_identity.user.is_staff,
            "language": dave_identity.user.language,
            "timezone": str(dave_identity.user.timezone),
        },
        {
            "id": str(davina_identity.user.id),
            "email": davina_identity.email,
            "name": davina_identity.name,
            "is_device": davina_identity.user.is_device,
            "is_staff": davina_identity.user.is_staff,
            "language": davina_identity.user.language,
            "timezone": str(davina_identity.user.timezone),
        },
        {
            "id": str(prue_identity.user.id),
            "email": prue_identity.email,
            "name": prue_identity.name,
            "is_device": prue_identity.user.is_device,
            "is_staff": prue_identity.user.is_staff,
            "language": prue_identity.user.language,
            "timezone": str(prue_identity.user.timezone),
        },
    ]


def test_api_users_authenticated_list_uppercase_content():
    """Upper case content should be found by lower case query."""
    user = factories.UserFactory(email="tester@ministry.fr")
    factories.IdentityFactory(user=user, email=user.email)

    client = APIClient()
    client.force_login(user)

    dave = factories.IdentityFactory(email="DAVID.BOWMAN@INTENSEWORK.COM")

    # Unaccented full address
    response = client.get(
        "/api/v1.0/users/?q=david.bowman@intensework.com",
    )

    assert response.status_code == HTTP_200_OK
    user_ids = [user["id"] for user in response.json()["results"]]
    assert user_ids == [str(dave.user.id)]

    # Partial query
    response = client.get(
        "/api/v1.0/users/?q=david",
    )

    assert response.status_code == HTTP_200_OK
    user_ids = [user["id"] for user in response.json()["results"]]
    assert user_ids == [str(dave.user.id)]


def test_api_users_list_authenticated_capital_query():
    """Upper case query should find lower case content."""
    user = factories.UserFactory(email="tester@ministry.fr")
    factories.IdentityFactory(user=user, email=user.email)

    client = APIClient()
    client.force_login(user)

    dave = factories.IdentityFactory(email="david.bowman@work.com")

    # Full uppercase query
    response = client.get(
        "/api/v1.0/users/?q=DAVID.BOWMAN@WORK.COM",
    )

    assert response.status_code == HTTP_200_OK
    user_ids = [user["id"] for user in response.json()["results"]]
    assert user_ids == [str(dave.user.id)]

    # Partial uppercase email
    response = client.get(
        "/api/v1.0/users/?q=DAVID",
    )

    assert response.status_code == HTTP_200_OK
    user_ids = [user["id"] for user in response.json()["results"]]
    assert user_ids == [str(dave.user.id)]


def test_api_contacts_list_authenticated_accented_query():
    """Accented content should be found by unaccented query."""
    user = factories.UserFactory(email="tester@ministry.fr")
    factories.IdentityFactory(user=user, email=user.email)

    client = APIClient()
    client.force_login(user)

    helene = factories.IdentityFactory(email="helene.bowman@work.com")

    # Accented full query
    response = client.get(
        "/api/v1.0/users/?q=hélène.bowman@work.com",
    )

    assert response.status_code == HTTP_200_OK
    user_ids = [user["id"] for user in response.json()["results"]]
    assert user_ids == [str(helene.user.id)]

    # Unaccented partial email
    response = client.get(
        "/api/v1.0/users/?q=hélène",
    )

    assert response.status_code == HTTP_200_OK
    user_ids = [user["id"] for user in response.json()["results"]]
    assert user_ids == [str(helene.user.id)]


@mock.patch.object(Pagination, "get_page_size", return_value=3)
def test_api_users_list_pagination(
    _mock_page_size,
):
    """Pagination should work as expected."""
    identity = factories.IdentityFactory()
    user = identity.user

    client = APIClient()
    client.force_login(user)

    factories.UserFactory.create_batch(4)

    # Get page 1
    response = client.get(
        "/api/v1.0/users/",
    )

    assert response.status_code == HTTP_200_OK
    content = response.json()

    assert content["count"] == 5
    assert len(content["results"]) == 3
    assert content["next"] == "http://testserver/api/v1.0/users/?page=2"
    assert content["previous"] is None

    # Get page 2
    response = client.get(
        "/api/v1.0/users/?page=2",
    )

    assert response.status_code == HTTP_200_OK
    content = response.json()

    assert content["count"] == 5
    assert content["next"] is None
    assert content["previous"] == "http://testserver/api/v1.0/users/"

    assert len(content["results"]) == 2


def test_api_users_retrieve_me_anonymous():
    """Anonymous users should not be allowed to list users."""
    factories.UserFactory.create_batch(2)
    client = APIClient()
    response = client.get("/api/v1.0/users/me/")
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_users_retrieve_me_authenticated():
    """Authenticated users should be able to retrieve their own user via the "/users/me" path."""
    identity = factories.IdentityFactory(is_main=True)
    user = identity.user

    client = APIClient()
    client.force_login(user)

    # Define profile contact
    contact = factories.ContactFactory(owner=user)
    user.profile_contact = contact
    user.save()

    factories.UserFactory.create_batch(2)
    response = client.get(
        "/api/v1.0/users/me/",
    )

    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "id": str(user.id),
        "name": str(identity.name),
        "email": str(identity.email),
        "language": user.language,
        "timezone": str(user.timezone),
        "is_device": False,
        "is_staff": False,
    }


def test_api_users_retrieve_anonymous():
    """Anonymous users should not be allowed to retrieve a user."""
    client = APIClient()
    user = factories.UserFactory()
    response = client.get(f"/api/v1.0/users/{user.id!s}/")

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }


def test_api_users_retrieve_authenticated_self():
    """
    Authenticated users should be allowed to retrieve their own user.
    The returned object should not contain the password.
    """
    identity = factories.IdentityFactory()
    user = identity.user

    client = APIClient()
    client.force_login(user)

    response = client.get(
        f"/api/v1.0/users/{user.id!s}/",
    )
    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
    assert response.json() == {"detail": 'Method "GET" not allowed.'}


def test_api_users_retrieve_authenticated_other():
    """
    Authenticated users should be able to retrieve another user's detail view with
    limited information.
    """
    identity = factories.IdentityFactory()

    client = APIClient()
    client.force_login(identity.user)

    other_user = factories.UserFactory()

    response = client.get(
        f"/api/v1.0/users/{other_user.id!s}/",
    )
    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
    assert response.json() == {"detail": 'Method "GET" not allowed.'}


def test_api_users_create_anonymous():
    """Anonymous users should not be able to create users via the API."""
    response = APIClient().post(
        "/api/v1.0/users/",
        {
            "language": "fr-fr",
            "password": "mypassword",
        },
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert "Authentication credentials were not provided." in response.content.decode(
        "utf-8"
    )
    assert models.User.objects.exists() is False


def test_api_users_create_authenticated():
    """Authenticated users should not be able to create users via the API."""
    identity = factories.IdentityFactory()
    user = identity.user

    client = APIClient()
    client.force_login(user)

    response = client.post(
        "/api/v1.0/users/",
        {
            "language": "fr-fr",
            "password": "mypassword",
        },
        format="json",
    )
    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
    assert response.json() == {"detail": 'Method "POST" not allowed.'}
    assert models.User.objects.exclude(id=user.id).exists() is False


def test_api_users_update_anonymous():
    """Anonymous users should not be able to update users via the API."""
    user = factories.UserFactory()

    old_user_values = dict(serializers.UserSerializer(instance=user).data)
    new_user_values = serializers.UserSerializer(instance=factories.UserFactory()).data

    response = APIClient().put(
        f"/api/v1.0/users/{user.id!s}/",
        new_user_values,
        format="json",
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }

    user.refresh_from_db()
    user_values = dict(serializers.UserSerializer(instance=user).data)
    for key, value in user_values.items():
        assert value == old_user_values[key]


def test_api_users_update_authenticated_self():
    """
    Authenticated users should be able to update their own user but only "language"
    and "timezone" fields.
    """
    identity = factories.IdentityFactory()
    user = identity.user

    client = APIClient()
    client.force_login(user)

    old_user_values = dict(serializers.UserSerializer(instance=user).data)
    new_user_values = dict(
        serializers.UserSerializer(instance=factories.UserFactory()).data
    )

    response = client.put(
        f"/api/v1.0/users/{user.id!s}/",
        new_user_values,
        format="json",
    )

    assert response.status_code == HTTP_200_OK
    user.refresh_from_db()
    user_values = dict(serializers.UserSerializer(instance=user).data)
    for key, value in user_values.items():
        if key in ["language", "timezone"]:
            assert value == new_user_values[key]
        else:
            assert value == old_user_values[key]


def test_api_users_update_authenticated_other():
    """Authenticated users should not be allowed to update other users."""
    identity = factories.IdentityFactory()

    client = APIClient()
    client.force_login(identity.user)

    user = factories.UserFactory()
    old_user_values = dict(serializers.UserSerializer(instance=user).data)
    new_user_values = serializers.UserSerializer(instance=factories.UserFactory()).data

    response = client.put(
        f"/api/v1.0/users/{user.id!s}/",
        new_user_values,
        format="json",
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    user.refresh_from_db()
    user_values = dict(serializers.UserSerializer(instance=user).data)
    for key, value in user_values.items():
        assert value == old_user_values[key]


def test_api_users_patch_anonymous():
    """Anonymous users should not be able to patch users via the API."""
    user = factories.UserFactory()

    old_user_values = dict(serializers.UserSerializer(instance=user).data)
    new_user_values = dict(
        serializers.UserSerializer(instance=factories.UserFactory()).data
    )

    for key, new_value in new_user_values.items():
        response = APIClient().patch(
            f"/api/v1.0/users/{user.id!s}/",
            {key: new_value},
            format="json",
        )
        assert response.status_code == HTTP_401_UNAUTHORIZED
        assert response.json() == {
            "detail": "Authentication credentials were not provided."
        }

    user.refresh_from_db()
    user_values = dict(serializers.UserSerializer(instance=user).data)
    for key, value in user_values.items():
        assert value == old_user_values[key]


def test_api_users_patch_authenticated_self():
    """
    Authenticated users should be able to patch their own user but only "language"
    and "timezone" fields.
    """
    identity = factories.IdentityFactory()
    user = identity.user

    client = APIClient()
    client.force_login(user)

    old_user_values = dict(serializers.UserSerializer(instance=user).data)
    new_user_values = dict(
        serializers.UserSerializer(instance=factories.UserFactory()).data
    )

    for key, new_value in new_user_values.items():
        response = client.patch(
            f"/api/v1.0/users/{user.id!s}/",
            {key: new_value},
            format="json",
        )
        assert response.status_code == HTTP_200_OK

    user.refresh_from_db()
    user_values = dict(serializers.UserSerializer(instance=user).data)
    for key, value in user_values.items():
        if key in ["language", "timezone"]:
            assert value == new_user_values[key]
        else:
            assert value == old_user_values[key]


def test_api_users_patch_authenticated_other():
    """Authenticated users should not be allowed to patch other users."""
    identity = factories.IdentityFactory()

    client = APIClient()
    client.force_login(identity.user)

    user = factories.UserFactory()
    old_user_values = dict(serializers.UserSerializer(instance=user).data)
    new_user_values = dict(
        serializers.UserSerializer(instance=factories.UserFactory()).data
    )

    for key, new_value in new_user_values.items():
        response = client.put(
            f"/api/v1.0/users/{user.id!s}/",
            {key: new_value},
            format="json",
        )
        assert response.status_code == HTTP_403_FORBIDDEN

    user.refresh_from_db()
    user_values = dict(serializers.UserSerializer(instance=user).data)
    for key, value in user_values.items():
        assert value == old_user_values[key]


def test_api_users_delete_list_anonymous():
    """Anonymous users should not be allowed to delete a list of users."""
    factories.UserFactory.create_batch(2)

    client = APIClient()
    response = client.delete("/api/v1.0/users/")

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert models.User.objects.count() == 2


def test_api_users_delete_list_authenticated():
    """Authenticated users should not be allowed to delete a list of users."""
    factories.UserFactory.create_batch(2)
    identity = factories.IdentityFactory()

    client = APIClient()
    client.force_login(identity.user)

    response = client.delete(
        "/api/v1.0/users/",
    )

    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
    assert models.User.objects.count() == 3


def test_api_users_delete_anonymous():
    """Anonymous users should not be allowed to delete a user."""
    user = factories.UserFactory()

    response = APIClient().delete(f"/api/v1.0/users/{user.id!s}/")

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert models.User.objects.count() == 1


def test_api_users_delete_authenticated():
    """
    Authenticated users should not be allowed to delete a user other than themselves.
    """
    identity = factories.IdentityFactory()
    other_user = factories.UserFactory()

    client = APIClient()
    client.force_login(identity.user)

    response = client.delete(f"/api/v1.0/users/{other_user.id!s}/")

    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
    assert models.User.objects.count() == 2


def test_api_users_delete_self():
    """Authenticated users should not be able to delete their own user."""
    identity = factories.IdentityFactory()

    client = APIClient()
    client.force_login(identity.user)

    response = client.delete(
        f"/api/v1.0/users/{identity.user.id!s}/",
    )

    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
    assert models.User.objects.count() == 1
