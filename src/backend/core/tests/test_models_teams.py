"""
Unit tests for the Team model
"""

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError

import pytest

from core import factories, models

pytestmark = pytest.mark.django_db


def test_models_teams_str():
    """The str representation should be the name of the team."""
    team = factories.TeamFactory(name="admins")
    assert str(team) == "admins"


def test_models_teams_id_unique():
    """The "id" field should be unique."""
    team = factories.TeamFactory()
    with pytest.raises(ValidationError, match="Team with this Id already exists."):
        factories.TeamFactory(id=team.id)


def test_models_teams_name_null():
    """The "name" field should not be null."""
    with pytest.raises(ValidationError, match="This field cannot be null."):
        models.Team.objects.create(name=None)


def test_models_teams_name_empty():
    """The "name" field should not be empty."""
    with pytest.raises(ValidationError, match="This field cannot be blank."):
        models.Team.objects.create(name="")


def test_models_teams_name_max_length():
    """The "name" field should be 100 characters maximum."""
    factories.TeamFactory(name="a " * 50)
    with pytest.raises(
        ValidationError,
        match=r"Ensure this value has at most 100 characters \(it has 102\)\.",
    ):
        factories.TeamFactory(name="a " * 51)


# get_abilities


def test_models_teams_get_abilities_anonymous():
    """Check abilities returned for an anonymous user."""
    team = factories.TeamFactory()
    abilities = team.get_abilities(AnonymousUser())
    assert abilities == {
        "delete": False,
        "get": False,
        "patch": False,
        "put": False,
        "manage_accesses": False,
    }


def test_models_teams_get_abilities_authenticated():
    """Check abilities returned for an authenticated user."""
    team = factories.TeamFactory()
    abilities = team.get_abilities(factories.UserFactory())
    assert abilities == {
        "delete": False,
        "get": False,
        "patch": False,
        "put": False,
        "manage_accesses": False,
    }


def test_models_teams_get_abilities_owner():
    """Check abilities returned for the owner of a team."""
    user = factories.UserFactory()
    access = factories.TeamAccessFactory(role="owner", user=user)
    abilities = access.team.get_abilities(access.user)
    assert abilities == {
        "delete": True,
        "get": True,
        "patch": True,
        "put": True,
        "manage_accesses": True,
    }


def test_models_teams_get_abilities_administrator():
    """Check abilities returned for the administrator of a team."""
    access = factories.TeamAccessFactory(role="administrator")
    abilities = access.team.get_abilities(access.user)
    assert abilities == {
        "delete": False,
        "get": True,
        "patch": True,
        "put": True,
        "manage_accesses": True,
    }


def test_models_teams_get_abilities_member_user(django_assert_num_queries):
    """Check abilities returned for the member of a team."""
    access = factories.TeamAccessFactory(role="member")

    with django_assert_num_queries(1):
        abilities = access.team.get_abilities(access.user)

    assert abilities == {
        "delete": False,
        "get": True,
        "patch": False,
        "put": False,
        "manage_accesses": False,
    }


def test_models_teams_get_abilities_preset_role(django_assert_num_queries):
    """No query is done if the role is preset e.g. with query annotation."""
    access = factories.TeamAccessFactory(role="member")
    access.team.user_role = "member"

    with django_assert_num_queries(0):
        abilities = access.team.get_abilities(access.user)

    assert abilities == {
        "delete": False,
        "get": True,
        "patch": False,
        "put": False,
        "manage_accesses": False,
    }


# test trees


def test_models_teams_create_root_team():
    """Create a root team."""
    team = models.Team.add_root(name="Root Team")
    assert team.is_root()
    assert team.name == "Root Team"


def test_models_teams_create_child_team():
    """Create a child team."""
    root_team = models.Team.add_root(name="Root Team")
    child_team = root_team.add_child(name="Child Team")
    assert child_team.is_child_of(root_team)
    assert child_team.name == "Child Team"
    assert child_team.get_parent() == root_team


def test_models_teams_create_grandchild_team():
    """Create a grandchild team."""
    root_team = models.Team.add_root(name="Root Team")
    child_team = root_team.add_child(name="Child Team")
    grandchild_team = child_team.add_child(name="Grandchild Team")
    assert grandchild_team.is_child_of(child_team)
    assert grandchild_team.name == "Grandchild Team"
    assert grandchild_team.get_parent() == child_team


def test_models_teams_move_team():
    """Move a team to another parent."""
    root_team = models.Team.add_root(name="Root Team")
    child_team = root_team.add_child(name="Child Team")
    new_root_team = models.Team.add_root(name="New Root Team")
    child_team.move(new_root_team, pos="first-child")
    child_team.refresh_from_db()
    assert child_team.get_parent(update=True) == new_root_team


def test_models_teams_delete_team():
    """
    Delete a parent team also deletes children.

    This might not be what we want, but it's the default behavior of treebeard.
    """
    root_team = models.Team.add_root(name="Root Team")
    root_team.add_child(name="Child Team")

    assert models.Team.objects.all().count() == 2
    root_team.delete()

    assert models.Team.objects.all().count() == 0


def test_models_teams_manager_create():
    """Create a team using the manager."""
    team = models.Team.objects.create(name="Team")
    assert team.is_root()
    assert team.name == "Team"

    child_team = models.Team.objects.create(name="Child Team", parent_id=team.pk)
    assert child_team.is_child_of(team)
    assert child_team.name == "Child Team"


def test_models_teams_tree_alphabet():
    """Test the creation of teams with treebeard methods."""
    organization = factories.OrganizationFactory(with_registration_id=True)
    models.Team.load_bulk(
        [
            {
                "data": {
                    "name": f"team-{i}",
                    "organization_id": organization.pk,
                }
            }
            for i in range(len(models.Team.alphabet) * 2)
        ]
    )

    assert models.Team.objects.count() == len(models.Team.alphabet) * 2
