"""
Test users API endpoints in the People core app: focus on "create" action
"""

import pytest
from rest_framework.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_405_METHOD_NOT_ALLOWED,
)
from rest_framework.test import APIClient

from core import factories, models

pytestmark = pytest.mark.django_db


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
