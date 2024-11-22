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
from core.api.client import serializers
from core.api.client.viewsets import Pagination
from core.factories import TeamAccessFactory

from mailbox_manager.factories import MailDomainAccessFactory

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
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    factories.UserFactory.create_batch(2)
    response = client.get(
        "/api/v1.0/users/",
    )
    assert response.status_code == HTTP_200_OK
    assert len(response.json()["results"]) == 3


def test_api_users_list_authenticated_response_content(
    client, django_assert_num_queries
):
    """
    Authenticated users should be able to list all users with the expected output.
    """
    user_organization = factories.OrganizationFactory(
        with_registration_id=True, name="HAL 9000"
    )
    user = factories.UserFactory(
        organization=user_organization,
        email="kylefields@example.net",
        name="Mr. Christopher Curtis",
        language="en-us",
    )

    client.force_login(user)

    other_user_organization = factories.OrganizationFactory(
        with_registration_id=True, name="Corp. Inc."
    )
    other_user = factories.UserFactory(
        organization=other_user_organization,
        email="sara83@example.com",
        name="Christopher Thompson",
        language="fr-fr",
    )

    with django_assert_num_queries(3):  # get User, Count, Users
        response = client.get("/api/v1.0/users/")

    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "count": 2,
        "next": None,
        "previous": None,
        "results": [
            {
                "email": "sara83@example.com",
                "id": str(other_user.pk),
                "is_device": False,
                "is_staff": False,
                "language": "fr-fr",
                "name": "Christopher Thompson",
                "organization": {
                    "id": str(other_user.organization.pk),
                    "name": "Corp. Inc.",
                },
                "timezone": "UTC",
            },
            {
                "email": "kylefields@example.net",
                "id": str(user.pk),
                "is_device": False,
                "is_staff": False,
                "language": "en-us",
                "name": "Mr. Christopher Curtis",
                "organization": {
                    "id": str(user.organization.pk),
                    "name": "HAL 9000",
                },
                "timezone": "UTC",
            },
        ],
    }


def test_api_users_authenticated_list_by_email():
    """
    Authenticated users should be able to search users with a case-insensitive and
    partial query on the email.
    """
    user = factories.UserFactory(email="tester@ministry.fr", name="john doe")
    dave = factories.UserFactory(email="david.bowman@work.com", name=None)
    nicole = factories.UserFactory(
        email="nicole_foole@work.com", name=None, with_organization=True
    )
    frank = factories.UserFactory(
        email="frank_poole@work.com", name=None, with_organization=True
    )
    factories.UserFactory(email="heywood_floyd@work.com", name=None)

    client = APIClient()
    client.force_login(user)

    # Full query should work
    response = client.get(
        "/api/v1.0/users/?q=david.bowman@work.com",
    )

    assert response.status_code == HTTP_200_OK
    user_ids = [user["id"] for user in response.json()["results"]]
    assert user_ids[0] == str(dave.id)

    # Partial query should work
    response = client.get("/api/v1.0/users/?q=fran")

    assert response.status_code == HTTP_200_OK
    user_ids = [user["id"] for user in response.json()["results"]]
    assert user_ids[0] == str(frank.id)

    response = client.get("/api/v1.0/users/?q=ole")

    assert response.status_code == HTTP_200_OK
    user_ids = [user["id"] for user in response.json()["results"]]
    assert user_ids == [str(frank.id), str(nicole.id)]

    response = client.get("/api/v1.0/users/?q=ool")

    assert response.status_code == HTTP_200_OK
    assert response.json()["results"] == [
        {
            "id": str(frank.id),
            "email": frank.email,
            "name": frank.name,
            "is_device": frank.is_device,
            "is_staff": frank.is_staff,
            "language": frank.language,
            "timezone": str(frank.timezone),
            "organization": {
                "id": str(frank.organization.pk),
                "name": frank.organization.name,
            },
        },
        {
            "id": str(nicole.id),
            "email": nicole.email,
            "name": nicole.name,
            "is_device": nicole.is_device,
            "is_staff": nicole.is_staff,
            "language": nicole.language,
            "timezone": str(nicole.timezone),
            "organization": {
                "id": str(nicole.organization.pk),
                "name": nicole.organization.name,
            },
        },
    ]


def test_api_users_authenticated_list_by_name():
    """
    Authenticated users should be able to search users with a case-insensitive and
    partial query on the name.
    """
    user = factories.UserFactory(email="tester@ministry.fr", name="john doe")
    dave = factories.UserFactory(name="Dave bowman", email=None)
    nicole = factories.UserFactory(
        name="nicole foole", email=None, with_organization=True
    )
    frank = factories.UserFactory(
        name="frank poolé", email=None, with_organization=True
    )
    factories.UserFactory(name="heywood floyd", email=None)

    client = APIClient()
    client.force_login(user)

    # Full query should work
    response = client.get(
        "/api/v1.0/users/?q=dave",
    )

    assert response.status_code == HTTP_200_OK
    user_ids = [user["id"] for user in response.json()["results"]]
    assert user_ids[0] == str(dave.id)

    # Partial query should work
    response = client.get("/api/v1.0/users/?q=fran")

    assert response.status_code == HTTP_200_OK
    user_ids = [user["id"] for user in response.json()["results"]]
    assert user_ids[0] == str(frank.id)

    response = client.get("/api/v1.0/users/?q=ole")

    assert response.status_code == HTTP_200_OK
    user_ids = [user["id"] for user in response.json()["results"]]
    assert user_ids == [str(frank.id), str(nicole.id)]

    response = client.get("/api/v1.0/users/?q=oole")

    assert response.status_code == HTTP_200_OK
    assert response.json()["results"] == [
        {
            "id": str(frank.id),
            "email": frank.email,
            "name": frank.name,
            "is_device": frank.is_device,
            "is_staff": frank.is_staff,
            "language": frank.language,
            "timezone": str(frank.timezone),
            "organization": {
                "id": str(frank.organization.pk),
                "name": frank.organization.name,
            },
        },
        {
            "id": str(nicole.id),
            "email": nicole.email,
            "name": nicole.name,
            "is_device": nicole.is_device,
            "is_staff": nicole.is_staff,
            "language": nicole.language,
            "timezone": str(nicole.timezone),
            "organization": {
                "id": str(nicole.organization.pk),
                "name": nicole.organization.name,
            },
        },
    ]


def test_api_users_authenticated_list_by_name_and_email():
    """
    Authenticated users should be able to search users with a case-insensitive and
    partial query on the name and email.
    """

    user = factories.UserFactory(email="tester@ministry.fr", name="john doe")
    nicole = factories.UserFactory(email="nicole_foole@work.com", name="nicole foole")
    oleg = factories.UserFactory(email="oleg_poole@work.com", name=None)
    david = factories.UserFactory(email=None, name="david role")

    client = APIClient()
    client.force_login(user)

    response = client.get("/api/v1.0/users/?q=ole")

    assert response.status_code == HTTP_200_OK
    user_ids = [user["id"] for user in response.json()["results"]]

    assert user_ids == [str(david.id), str(oleg.id), str(nicole.id)]


def test_api_users_authenticated_list_exclude_users_already_in_team(
    django_assert_num_queries,
):
    """
    Authenticated users should be able to search users
    but the result should exclude all users already in the given team.
    """
    user = factories.UserFactory(email="tester@ministry.fr", name="john doe")
    dave = factories.UserFactory(name="dave bowman", email=None)
    nicole = factories.UserFactory(name="nicole foole", email=None)
    frank = factories.UserFactory(name="frank poole", email=None)
    mary = factories.UserFactory(name="mary poole", email=None)
    factories.UserFactory(name="heywood floyd", email=None)
    factories.UserFactory(name="Andrei Smyslov", email=None)
    factories.TeamFactory.create_batch(10)

    client = APIClient()
    client.force_login(user)

    # Add Dave and Frank in the same team
    team = factories.TeamFactory(
        users=[
            (dave, models.RoleChoices.MEMBER),
            (frank, models.RoleChoices.MEMBER),
        ]
    )
    factories.TeamFactory(users=[(nicole, models.RoleChoices.MEMBER)])

    # Search user to add him/her to a team, we give a team id to the request
    # to exclude all users already in the team

    # We can't find David Bowman because he is already a member of the given team
    # 2 queries are needed here:
    # - user authenticated
    # - search user query
    with django_assert_num_queries(2):
        response = client.get(
            f"/api/v1.0/users/?q=bowman&team_id={team.id}",
        )
    assert response.status_code == HTTP_200_OK
    assert response.json()["results"] == []

    # We can only find Nicole and Mary because Frank is already a member of the given team
    # 4 queries are needed here:
    # - user authenticated
    # - search user query
    # - User
    with django_assert_num_queries(3):
        response = client.get(
            f"/api/v1.0/users/?q=ool&team_id={team.id}",
        )
    assert response.status_code == HTTP_200_OK
    user_ids = sorted([user["id"] for user in response.json()["results"]])
    assert user_ids == sorted([str(mary.id), str(nicole.id)])


def test_api_users_authenticated_list_uppercase_content():
    """Upper case content should be found by lower case query."""
    user = factories.UserFactory(email="tester@ministry.fr", name="eva karl")
    dave = factories.UserFactory(
        email="DAVID.BOWMAN@INTENSEWORK.COM", name="DAVID BOWMAN"
    )

    client = APIClient()
    client.force_login(user)

    # Unaccented full address
    response = client.get(
        "/api/v1.0/users/?q=david.bowman@intensework.com",
    )

    assert response.status_code == HTTP_200_OK
    user_ids = [user["id"] for user in response.json()["results"]]
    assert user_ids == [str(dave.id)]

    # Partial query
    response = client.get(
        "/api/v1.0/users/?q=david",
    )

    assert response.status_code == HTTP_200_OK
    user_ids = [user["id"] for user in response.json()["results"]]
    assert user_ids == [str(dave.id)]


def test_api_users_list_authenticated_capital_query():
    """Upper case query should find lower case content."""
    user = factories.UserFactory(email="tester@ministry.fr", name="eva karl")
    dave = factories.UserFactory(email="david.bowman@work.com", name="david bowman")

    client = APIClient()
    client.force_login(user)

    # Full uppercase query
    response = client.get(
        "/api/v1.0/users/?q=DAVID.BOWMAN@WORK.COM",
    )

    assert response.status_code == HTTP_200_OK
    user_ids = [user["id"] for user in response.json()["results"]]
    assert user_ids == [str(dave.id)]

    # Partial uppercase email
    response = client.get(
        "/api/v1.0/users/?q=DAVID",
    )

    assert response.status_code == HTTP_200_OK
    user_ids = [user["id"] for user in response.json()["results"]]
    assert user_ids == [str(dave.id)]


def test_api_contacts_list_authenticated_accented_query():
    """Accented content should be found by unaccented query."""
    user = factories.UserFactory(email="tester@ministry.fr", name="john doe")
    helene = factories.UserFactory(email="helene.bowman@work.com", name="helene bowman")

    client = APIClient()
    client.force_login(user)

    # Accented full query
    response = client.get(
        "/api/v1.0/users/?q=hélène.bowman@work.com",
    )

    assert response.status_code == HTTP_200_OK
    user_ids = [user["id"] for user in response.json()["results"]]
    assert user_ids == [str(helene.id)]

    # Unaccented partial email
    response = client.get(
        "/api/v1.0/users/?q=hélène",
    )

    assert response.status_code == HTTP_200_OK
    user_ids = [user["id"] for user in response.json()["results"]]
    assert user_ids == [str(helene.id)]


@mock.patch.object(Pagination, "get_page_size", return_value=3)
def test_api_users_list_pagination(
    _mock_page_size,
):
    """Pagination should work as expected."""
    user = factories.UserFactory()

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


@pytest.mark.parametrize("page_size", [1, 10, 99, 100])
def test_api_users_list_pagination_page_size(
    page_size,
):
    """Page's size on pagination should work as expected."""
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    for i in range(page_size):
        factories.UserFactory.create(email=f"user-{i}@people.com")

    response = client.get(
        f"/api/v1.0/users/?page_size={page_size}",
    )

    assert response.status_code == HTTP_200_OK
    content = response.json()

    assert content["count"] == page_size + 1
    assert len(content["results"]) == page_size


@pytest.mark.parametrize("page_size", [101, 200])
def test_api_users_list_pagination_wrong_page_size(
    page_size,
):
    """Page's size on pagination should be limited to "max_page_size"."""
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    for i in range(page_size):
        factories.UserFactory.create(email=f"user-{i}@people.com")

    response = client.get(
        f"/api/v1.0/users/?page_size={page_size}",
    )

    assert response.status_code == HTTP_200_OK
    content = response.json()

    assert content["count"] == page_size + 1

    # Length should not exceed "max_page_size" default value
    assert len(content["results"]) == 100


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
    user = factories.UserFactory(with_organization=True)

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
        "name": str(user.name),
        "email": str(user.email),
        "language": user.language,
        "timezone": str(user.timezone),
        "is_device": False,
        "is_staff": False,
        "abilities": {
            "contacts": {"can_create": True, "can_view": True},
            "mailboxes": {"can_create": False, "can_view": False},
            "teams": {"can_create": False, "can_view": False},
        },
        "organization": {
            "id": str(user.organization.pk),
            "name": user.organization.name,
        },
    }


def test_api_users_retrieve_me_authenticated_abilities():
    """
    Authenticated users should be able to retrieve their own user via the "/users/me" path
    with the proper abilities.
    """
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    # Define profile contact
    contact = factories.ContactFactory(owner=user)
    user.profile_contact = contact
    user.save()

    factories.UserFactory.create_batch(2)

    # Test the mailboxes abilities
    mail_domain_access = MailDomainAccessFactory(user=user)

    response = client.get("/api/v1.0/users/me/")

    assert response.status_code == HTTP_200_OK
    assert response.json()["abilities"] == {
        "contacts": {"can_create": True, "can_view": True},
        "mailboxes": {"can_create": True, "can_view": True},
        "teams": {"can_create": False, "can_view": False},
    }

    # Test the teams abilities - user is not an admin/owner
    team_access = TeamAccessFactory(user=user, role=models.RoleChoices.MEMBER)
    response = client.get("/api/v1.0/users/me/")

    assert response.status_code == HTTP_200_OK
    assert response.json()["abilities"] == {
        "contacts": {"can_create": True, "can_view": True},
        "mailboxes": {"can_create": True, "can_view": True},
        "teams": {"can_create": False, "can_view": False},
    }

    # Test the teams abilities - user is an admin/owner
    team_access.role = models.RoleChoices.ADMIN
    team_access.save()

    response = client.get("/api/v1.0/users/me/")

    assert response.status_code == HTTP_200_OK
    assert response.json()["abilities"] == {
        "contacts": {"can_create": True, "can_view": True},
        "mailboxes": {"can_create": True, "can_view": True},
        "teams": {"can_create": True, "can_view": True},
    }

    # Test the mailboxes abilities - user has no mail domain access anymore
    mail_domain_access.delete()

    response = client.get("/api/v1.0/users/me/")

    assert response.status_code == HTTP_200_OK
    assert response.json()["abilities"] == {
        "contacts": {"can_create": True, "can_view": True},
        "mailboxes": {"can_create": False, "can_view": False},
        "teams": {"can_create": True, "can_view": True},
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
    user = factories.UserFactory()

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
    user, other_user = factories.UserFactory.create_batch(2)

    client = APIClient()
    client.force_login(user)

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
    user = factories.UserFactory()

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
    user = factories.UserFactory()

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
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

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
    user = factories.UserFactory()

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
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    other_user = factories.UserFactory()
    old_user_values = dict(serializers.UserSerializer(instance=other_user).data)
    new_user_values = dict(
        serializers.UserSerializer(instance=factories.UserFactory()).data
    )

    for key, new_value in new_user_values.items():
        response = client.put(
            f"/api/v1.0/users/{other_user.id!s}/",
            {key: new_value},
            format="json",
        )
        assert response.status_code == HTTP_403_FORBIDDEN

    other_user.refresh_from_db()
    user_values = dict(serializers.UserSerializer(instance=other_user).data)
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
    user = factories.UserFactory()
    factories.UserFactory.create_batch(2)

    client = APIClient()
    client.force_login(user)

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
    user, other_user = factories.UserFactory.create_batch(2)

    client = APIClient()
    client.force_login(user)

    response = client.delete(f"/api/v1.0/users/{other_user.id!s}/")

    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
    assert models.User.objects.count() == 2


def test_api_users_delete_self():
    """Authenticated users should not be able to delete their own user."""
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    response = client.delete(
        f"/api/v1.0/users/{user.id!s}/",
    )

    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
    assert models.User.objects.count() == 1
