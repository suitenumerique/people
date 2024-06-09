"""
Tests for Teams API endpoint in People's core app: create
"""

import pytest
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
)
from rest_framework.test import APIClient

from core.factories import TeamFactory, UserFactory
from core.models import Team

pytestmark = pytest.mark.django_db


def test_api_teams_create_anonymous():
    """Anonymous users should not be allowed to create teams."""
    response = APIClient().post(
        "/api/v1.0/teams/",
        {
            "name": "my team",
        },
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert not Team.objects.exists()


def test_api_teams_create_authenticated():
    """
    Authenticated users should be able to create teams and should automatically be declared
    as the owner of the newly created team.
    """
    user = UserFactory()

    client = APIClient()
    client.force_login(user)

    response = client.post(
        "/api/v1.0/teams/",
        {
            "name": "my team",
        },
        format="json",
    )

    assert response.status_code == HTTP_201_CREATED
    team = Team.objects.get()
    assert team.name == "my team"
    assert team.accesses.filter(role="owner", user=user).exists()


def test_api_teams_create_authenticated_slugify_name():
    """
    Creating teams should automatically generate a slug.
    """
    user = UserFactory()
    client = APIClient()
    client.force_login(user)

    response = client.post(
        "/api/v1.0/teams/",
        {"name": "my team"},
    )

    assert response.status_code == HTTP_201_CREATED
    team = Team.objects.get()
    assert team.name == "my team"
    assert team.slug == "my-team"


@pytest.mark.parametrize(
    "param",
    [
        ("my team", "my-team"),
        ("my     team", "my-team"),
        ("MY TEAM TOO", "my-team-too"),
        ("mon équipe", "mon-equipe"),
        ("front devs & UX", "front-devs-ux"),
    ],
)
def test_api_teams_create_authenticated_expected_slug(param):
    """
    Creating teams should automatically create unaccented, no unicode, lower-case slug.
    """
    user = UserFactory()

    client = APIClient()
    client.force_login(user)

    response = client.post(
        "/api/v1.0/teams/",
        {
            "name": param[0],
        },
    )

    assert response.status_code == HTTP_201_CREATED
    team = Team.objects.get()
    assert team.name == param[0]
    assert team.slug == param[1]


def test_api_teams_create_authenticated_unique_slugs():
    """
    Creating teams should raise an error if already existing slug.
    """
    TeamFactory(name="existing team")
    user = UserFactory()

    client = APIClient()
    client.force_login(user)

    response = client.post(
        "/api/v1.0/teams/",
        {
            "name": "èxisting team",
        },
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["slug"] == ["Team with this Slug already exists."]
