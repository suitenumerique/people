"""
Test users API endpoints in the People core app: focus on "delete" action
"""

import pytest
from rest_framework.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_405_METHOD_NOT_ALLOWED,
)
from rest_framework.test import APIClient

from core import factories, models

pytestmark = pytest.mark.django_db


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
