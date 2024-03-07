"""
Unit tests for the Invitation model
"""

from django.core.exceptions import ValidationError

import pytest

from core import factories

pytestmark = pytest.mark.django_db


def test_models_invitations_email_no_empty_mail():
    """The "email" field should not be empty."""
    with pytest.raises(ValidationError, match="This field cannot be blank"):
        factories.InvitationFactory(email="")


def test_models_invitations_email_no_null_mail():
    """The "email" field is required."""
    with pytest.raises(ValidationError, match="This field cannot be null"):
        factories.InvitationFactory(email=None)


def test_models_invitations_team_required():
    """The "team" field is required."""
    with pytest.raises(ValidationError, match="This field cannot be null"):
        factories.InvitationFactory(team=None)


def test_models_invitations_team_should_be_team_instance():
    """The "team" field should be a team instance."""
    with pytest.raises(ValueError, match='Invitation.team" must be a "Team" instance'):
        factories.InvitationFactory(team="ee")


def test_models_invitations_role_required():
    """The "role" field is required."""
    with pytest.raises(ValidationError, match="This field cannot be blank"):
        factories.InvitationFactory(role="")


def test_models_invitations_role_among_choices():
    """The "role" field should be a valid choice."""
    with pytest.raises(ValidationError, match="Value 'boss' is not a valid choice"):
        factories.InvitationFactory(role="boss")
