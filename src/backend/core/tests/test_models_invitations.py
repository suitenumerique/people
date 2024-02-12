"""
Unit tests for the Invitation model
"""

import time

from django.contrib.auth.models import AnonymousUser
from django.core import exceptions

import pytest

from core import factories

pytestmark = pytest.mark.django_db


def test_models_invitations_readonly_after_create():
    """Existing invitations should be readonly."""
    invitation = factories.InvitationFactory()
    with pytest.raises(exceptions.PermissionDenied):
        invitation.save()


def test_models_invitations_email_no_empty_mail():
    """The "email" field should not be empty."""
    with pytest.raises(exceptions.ValidationError, match="This field cannot be blank"):
        factories.InvitationFactory(email="")


def test_models_invitations_email_no_null_mail():
    """The "email" field is required."""
    with pytest.raises(exceptions.ValidationError, match="This field cannot be null"):
        factories.InvitationFactory(email=None)


def test_models_invitations_team_required():
    """The "team" field is required."""
    with pytest.raises(exceptions.ValidationError, match="This field cannot be null"):
        factories.InvitationFactory(team=None)


def test_models_invitations_team_should_be_team_instance():
    """The "team" field should be a team instance."""
    with pytest.raises(ValueError, match='Invitation.team" must be a "Team" instance'):
        factories.InvitationFactory(team="ee")


def test_models_invitations_role_required():
    """The "role" field is required."""
    with pytest.raises(exceptions.ValidationError, match="This field cannot be blank"):
        factories.InvitationFactory(role="")


def test_models_invitations_role_among_choices():
    """The "role" field should be a valid choice."""
    with pytest.raises(
        exceptions.ValidationError, match="Value 'boss' is not a valid choice"
    ):
        factories.InvitationFactory(role="boss")


def test_models_invitations__is_expired(settings):
    """
    The 'is_expired' property should return False until validity duration
    is exceeded and True afterwards.
    """
    expired_invitation = factories.InvitationFactory()
    assert expired_invitation.is_expired is False

    settings.INVITATION_VALIDITY_DURATION = 1
    time.sleep(1)

    assert expired_invitation.is_expired is True


# get_abilities


def test_models_team_invitations_get_abilities_anonymous():
    """Check abilities returned for an anonymous user."""
    access = factories.InvitationFactory()
    abilities = access.get_abilities(AnonymousUser())
    assert abilities == {
        "delete": False,
        "get": False,
        "patch": False,
        "put": False,
    }


def test_models_team_invitations_get_abilities_authenticated():
    """Check abilities returned for an authenticated user."""
    access = factories.InvitationFactory()
    user = factories.UserFactory()
    abilities = access.get_abilities(user)
    assert abilities == {
        "delete": False,
        "get": False,
        "patch": False,
        "put": False,
    }


@pytest.mark.parametrize("role", ["administrator", "owner"])
def test_models_team_invitations_get_abilities_privileged_member(role):
    """Check abilities for a team member with a privileged role."""

    pivileged_access = factories.TeamAccessFactory(role=role)
    team = pivileged_access.team

    factories.TeamAccessFactory(team=team)  # another one

    invitation = factories.InvitationFactory(team=team)
    abilities = invitation.get_abilities(pivileged_access.user)

    assert abilities == {
        "delete": True,
        "get": True,
        "patch": False,
        "put": False,
    }


def test_models_team_invitations_get_abilities_member():
    """Check abilities for a team member with 'member' role."""

    member_access = factories.TeamAccessFactory(role="member")
    team = member_access.team

    factories.TeamAccessFactory(team=team)  # another one

    invitation = factories.InvitationFactory(team=team)
    abilities = invitation.get_abilities(member_access.user)

    assert abilities == {
        "delete": False,
        "get": True,
        "patch": False,
        "put": False,
    }
