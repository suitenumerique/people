"""
Test for team accesses API endpoints in People's core app : update
"""

import random
from uuid import uuid4

import pytest
from rest_framework.test import APIClient

from core import factories, models
from core.api import serializers

pytestmark = pytest.mark.django_db


def test_api_team_accesses_update_anonymous():
    """Anonymous users should not be allowed to update a team access."""
    access = factories.TeamAccessFactory()
    old_values = serializers.TeamAccessSerializer(instance=access).data

    new_values = {
        "id": uuid4(),
        "user": factories.UserFactory().id,
        "role": random.choice(models.RoleChoices.choices)[0],
    }

    for field, value in new_values.items():
        response = APIClient().put(
            f"/api/v1.0/teams/{access.team.id!s}/accesses/{access.id!s}/",
            {**old_values, field: value},
            format="json",
        )
        assert response.status_code == 401

    access.refresh_from_db()
    updated_values = serializers.TeamAccessSerializer(instance=access).data
    assert updated_values == old_values


def test_api_team_accesses_update_authenticated_unrelated():
    """
    Authenticated users should not be allowed to update a team access for a team to which
    they are not related.
    """
    user = factories.UserFactory()
    access = factories.TeamAccessFactory()
    old_values = serializers.TeamAccessSerializer(instance=access).data

    new_values = {
        "id": uuid4(),
        "user": factories.UserFactory().id,
        "role": random.choice(models.RoleChoices.choices)[0],
    }

    client = APIClient()
    client.force_login(user)
    for field, value in new_values.items():
        response = client.put(
            f"/api/v1.0/teams/{access.team.id!s}/accesses/{access.id!s}/",
            {**old_values, field: value},
            format="json",
        )
        assert response.status_code == 403

    access.refresh_from_db()
    updated_values = serializers.TeamAccessSerializer(instance=access).data
    assert updated_values == old_values


def test_api_team_accesses_update_authenticated_member():
    """Members of a team should not be allowed to update its accesses."""
    user = factories.UserFactory()
    team = factories.TeamFactory(users=[(user, "member")])
    access = factories.TeamAccessFactory(team=team)
    old_values = serializers.TeamAccessSerializer(instance=access).data

    new_values = {
        "id": uuid4(),
        "user": factories.UserFactory().id,
        "role": random.choice(models.RoleChoices.choices)[0],
    }

    client = APIClient()
    client.force_login(user)
    for field, value in new_values.items():
        response = client.put(
            f"/api/v1.0/teams/{access.team.id!s}/accesses/{access.id!s}/",
            {**old_values, field: value},
            format="json",
        )
        assert response.status_code == 403

    access.refresh_from_db()
    updated_values = serializers.TeamAccessSerializer(instance=access).data
    assert updated_values == old_values


def test_api_team_accesses_update_administrator_except_owner():
    """
    A user who is an administrator in a team should be allowed to update a user
    access for this team, as long as they don't try to set the role to owner.
    """
    user = factories.UserFactory()
    team = factories.TeamFactory(users=[(user, "administrator")])
    access = factories.TeamAccessFactory(
        team=team,
        role=random.choice(["administrator", "member"]),
    )
    old_values = serializers.TeamAccessSerializer(instance=access).data

    new_values = {
        "id": uuid4(),
        "user_id": factories.UserFactory().id,
        "role": random.choice(["administrator", "member"]),
    }

    client = APIClient()
    client.force_login(user)
    for field, value in new_values.items():
        new_data = {**old_values, field: value}
        response = client.put(
            f"/api/v1.0/teams/{team.id!s}/accesses/{access.id!s}/",
            data=new_data,
            format="json",
        )

        if (
            new_data["role"] == old_values["role"]
        ):  # we are not really updating the role
            assert response.status_code == 403
        else:
            assert response.status_code == 200

        access.refresh_from_db()
        updated_values = serializers.TeamAccessSerializer(instance=access).data
        if field == "role":
            assert updated_values == {**old_values, "role": new_values["role"]}
        else:
            assert updated_values == old_values


def test_api_team_accesses_update_administrator_from_owner():
    """
    A user who is an administrator in a team, should not be allowed to update
    the user access of an "owner" for this team.
    """
    user = factories.UserFactory()
    team = factories.TeamFactory(users=[(user, "administrator")])
    other_user = factories.UserFactory()
    access = factories.TeamAccessFactory(team=team, user=other_user, role="owner")
    old_values = serializers.TeamAccessSerializer(instance=access).data

    new_values = {
        "id": uuid4(),
        "user_id": factories.UserFactory().id,
        "role": random.choice(models.RoleChoices.choices)[0],
    }

    client = APIClient()
    client.force_login(user)
    for field, value in new_values.items():
        response = client.put(
            f"/api/v1.0/teams/{team.id!s}/accesses/{access.id!s}/",
            data={**old_values, field: value},
            format="json",
        )
        assert response.status_code == 403
        access.refresh_from_db()
        updated_values = serializers.TeamAccessSerializer(instance=access).data
        assert updated_values == old_values


def test_api_team_accesses_update_administrator_to_owner():
    """
    A user who is an administrator in a team, should not be allowed to update
    the user access of another user to grant team ownership.
    """
    user = factories.UserFactory()
    team = factories.TeamFactory(users=[(user, "administrator")])
    other_user = factories.UserFactory()
    access = factories.TeamAccessFactory(
        team=team,
        user=other_user,
        role=random.choice(["administrator", "member"]),
    )
    old_values = serializers.TeamAccessSerializer(instance=access).data

    new_values = {
        "id": uuid4(),
        "user_id": factories.UserFactory().id,
        "role": "owner",
    }

    client = APIClient()
    client.force_login(user)
    for field, value in new_values.items():
        new_data = {**old_values, field: value}
        response = client.put(
            f"/api/v1.0/teams/{team.id!s}/accesses/{access.id!s}/",
            data=new_data,
            format="json",
        )
        # We are not allowed or not really updating the role
        if field == "role" or new_data["role"] == old_values["role"]:
            assert response.status_code == 403
        else:
            assert response.status_code == 200

        access.refresh_from_db()
        updated_values = serializers.TeamAccessSerializer(instance=access).data
        assert updated_values == old_values


def test_api_team_accesses_update_owner_except_owner():
    """
    A user who is an owner in a team should be allowed to update
    a user access for this team except for existing "owner" accesses.
    """
    user = factories.UserFactory()
    team = factories.TeamFactory(users=[(user, "owner")])
    factories.UserFactory()
    access = factories.TeamAccessFactory(
        team=team,
        role=random.choice(["administrator", "member"]),
    )
    old_values = serializers.TeamAccessSerializer(instance=access).data

    new_values = {
        "id": uuid4(),
        "user_id": factories.UserFactory().id,
        "role": random.choice(models.RoleChoices.choices)[0],
    }

    client = APIClient()
    client.force_login(user)
    for field, value in new_values.items():
        new_data = {**old_values, field: value}
        response = client.put(
            f"/api/v1.0/teams/{team.id!s}/accesses/{access.id!s}/",
            data=new_data,
            format="json",
        )

        if (
            new_data["role"] == old_values["role"]
        ):  # we are not really updating the role
            assert response.status_code == 403
        else:
            assert response.status_code == 200

        access.refresh_from_db()
        updated_values = serializers.TeamAccessSerializer(instance=access).data

        if field == "role":
            assert updated_values == {**old_values, "role": new_values["role"]}
        else:
            assert updated_values == old_values


def test_api_team_accesses_update_owner_for_owners():
    """
    A user who is "owner" of a team should not be allowed to update
    an existing owner access for this team.
    """
    user = factories.UserFactory()
    team = factories.TeamFactory(users=[(user, "owner")])
    access = factories.TeamAccessFactory(team=team, role="owner")
    old_values = serializers.TeamAccessSerializer(instance=access).data

    new_values = {
        "id": uuid4(),
        "user_id": factories.UserFactory().id,
        "role": random.choice(models.RoleChoices.choices)[0],
    }

    client = APIClient()
    client.force_login(user)
    for field, value in new_values.items():
        response = client.put(
            f"/api/v1.0/teams/{team.id!s}/accesses/{access.id!s}/",
            data={**old_values, field: value},
            content_type="application/json",
        )
        assert response.status_code == 403
        access.refresh_from_db()
        updated_values = serializers.TeamAccessSerializer(instance=access).data
        assert updated_values == old_values


def test_api_team_accesses_update_owner_self():
    """
    A user who is owner of a team should be allowed to update
    their own user access provided there are other owners in the team.
    """
    user = factories.UserFactory()
    team = factories.TeamFactory()
    access = factories.TeamAccessFactory(team=team, user=user, role="owner")
    old_values = serializers.TeamAccessSerializer(instance=access).data
    new_role = random.choice(["administrator", "member"])

    client = APIClient()
    client.force_login(user)
    response = client.put(
        f"/api/v1.0/teams/{team.id!s}/accesses/{access.id!s}/",
        data={**old_values, "role": new_role},
        format="json",
    )

    assert response.status_code == 403
    access.refresh_from_db()
    assert access.role == "owner"

    # Add another owner and it should now work
    factories.TeamAccessFactory(team=team, role="owner")

    response = client.put(
        f"/api/v1.0/teams/{team.id!s}/accesses/{access.id!s}/",
        data={**old_values, "role": new_role},
        format="json",
    )

    assert response.status_code == 200
    access.refresh_from_db()
    assert access.role == new_role
