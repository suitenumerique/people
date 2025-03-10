"""
Unit tests for the Invitation model
"""

import smtplib
import time
import uuid
from logging import Logger
from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.core import exceptions, mail

import pytest
from faker import Faker
from freezegun import freeze_time

from core import factories, models

pytestmark = pytest.mark.django_db


fake = Faker()


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


def test_models_invitation__new_user__convert_invitations_to_accesses():
    """
    Upon creating a new user, invitations linked to that email
    should be converted to accesses and then deleted.
    """
    # Two invitations to the same mail but to different teams
    invitation_to_team1 = factories.InvitationFactory()
    invitation_to_team2 = factories.InvitationFactory(email=invitation_to_team1.email)

    other_invitation = factories.InvitationFactory(
        team=invitation_to_team2.team
    )  # another person invited to team2

    new_user = factories.UserFactory(email=invitation_to_team1.email)

    # The invitation regarding
    assert models.TeamAccess.objects.filter(
        team=invitation_to_team1.team, user=new_user
    ).exists()
    assert models.TeamAccess.objects.filter(
        team=invitation_to_team2.team, user=new_user
    ).exists()
    assert not models.Invitation.objects.filter(
        team=invitation_to_team1.team, email=invitation_to_team1.email
    ).exists()  # invitation "consumed"
    assert not models.Invitation.objects.filter(
        team=invitation_to_team2.team, email=invitation_to_team2.email
    ).exists()  # invitation "consumed"
    assert models.Invitation.objects.filter(
        team=invitation_to_team2.team, email=other_invitation.email
    ).exists()  # the other invitation remains


def test_models_invitation__new_user__filter_expired_invitations():
    """
    Upon creating a new user, valid invitations should be converted into accesses
    and expired invitations should remain unchanged.
    """
    with freeze_time("2020-01-01"):
        expired_invitation = factories.InvitationFactory()
    user_email = expired_invitation.email
    valid_invitation = factories.InvitationFactory(email=user_email)

    new_user = factories.UserFactory(email=user_email)

    # valid invitation should have granted access to the related team
    assert models.TeamAccess.objects.filter(
        team=valid_invitation.team, user=new_user
    ).exists()
    assert not models.Invitation.objects.filter(
        team=valid_invitation.team, email=user_email
    ).exists()

    # expired invitation should not have been consumed
    assert not models.TeamAccess.objects.filter(
        team=expired_invitation.team, user=new_user
    ).exists()
    assert models.Invitation.objects.filter(
        team=expired_invitation.team, email=user_email
    ).exists()


@pytest.mark.parametrize("num_invitations, num_queries", [(0, 5), (1, 8), (20, 8)])
def test_models_invitation__new_user__user_creation_constant_num_queries(
    django_assert_num_queries, num_invitations, num_queries
):
    """
    The number of queries executed during user creation should not be proportional
    to the number of invitations being processed.
    """
    user_email = fake.email()

    if num_invitations != 0:
        for _ in range(0, num_invitations):
            factories.InvitationFactory(email=user_email, team=factories.TeamFactory())

    factories.UserFactory()

    # with no invitation, we skip an "if", resulting in 8 requests
    # otherwise, we should have 11 queries with any number of invitations
    with django_assert_num_queries(num_queries):
        models.User.objects.create(
            email=user_email,
            password="!",
            name="Prudence C.",
            sub=uuid.uuid4(),
        )


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


def test_models_team_invitations_email():
    """Check email invitation during invitation creation."""

    member_access = factories.TeamAccessFactory(role="member")
    team = member_access.team

    # pylint: disable-next=no-member
    assert len(mail.outbox) == 0

    factories.TeamAccessFactory(team=team)
    invitation = factories.InvitationFactory(
        team=team, email="john@people.com", issuer__language="fr-fr"
    )

    # pylint: disable-next=no-member
    assert len(mail.outbox) == 1

    # pylint: disable-next=no-member
    email = mail.outbox[0]

    assert email.to == [invitation.email]
    assert email.subject == "Invitation à rejoindre La Régie !"

    email_content = " ".join(email.body.split())
    assert "Nous sommes ravis de vous accueillir" in email_content
    assert "[//example.com]" in email_content


@mock.patch(
    "django.core.mail.send_mail",
    side_effect=smtplib.SMTPException("Error SMTPException"),
)
@mock.patch.object(Logger, "error")
def test_models_team_invitations_email_failed(mock_logger, _mock_send_mail):
    """Check invitation behavior when an SMTP error occurs during invitation creation."""

    member_access = factories.TeamAccessFactory(role="member")
    team = member_access.team

    # pylint: disable-next=no-member
    assert len(mail.outbox) == 0

    factories.TeamAccessFactory(team=team)

    # No error should be raised
    invitation = factories.InvitationFactory(team=team, email="john@people.com")

    # No email has been sent
    # pylint: disable-next=no-member
    assert len(mail.outbox) == 0

    # Logger should be called
    mock_logger.assert_called_once()

    (
        _,
        email,
        exception,
    ) = mock_logger.call_args.args

    assert email == invitation.email
    assert isinstance(exception, smtplib.SMTPException)
