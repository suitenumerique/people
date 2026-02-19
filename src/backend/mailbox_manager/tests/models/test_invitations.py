"""
Unit tests for the Mail Domain Invitation model
"""

import time

from django.conf import settings
from django.core import exceptions

import pytest
from freezegun import freeze_time

from core import factories as core_factories

from mailbox_manager import enums, factories, models

pytestmark = pytest.mark.django_db


def test_models_domain_invitations_readonly_after_create():
    """Existing invitations should be readonly."""
    invitation = factories.MailDomainInvitationFactory()
    with pytest.raises(exceptions.PermissionDenied):
        invitation.save()


def test_models_domain_invitations__is_expired():
    """
    The 'is_expired' property should return False until validity duration
    is exceeded and True afterwards.
    """
    expired_invitation = factories.MailDomainInvitationFactory()
    assert expired_invitation.is_expired is False

    settings.INVITATION_VALIDITY_DURATION = 1
    time.sleep(1)

    assert expired_invitation.is_expired is True


def test_models_domain_invitation__should_convert_invitations_to_accesses_upon_joining(
    caplog,
):
    """
    Upon creating a new user, domain invitations linked to that email
    should be converted to accesses and then deleted.
    """
    caplog.set_level("INFO")

    # Two invitations to the same mail but to different domains
    email = "future_admin@example.com"
    invitation_domain1 = factories.MailDomainInvitationFactory(
        email=email, role=enums.MailDomainRoleChoices.OWNER
    )
    invitation_domain2 = factories.MailDomainInvitationFactory(email=email)

    # an expired invitation that should not be converted
    with freeze_time("1985-10-30"):
        expired_invitation = factories.MailDomainInvitationFactory(email=email)

    # another person invited to domain2
    other_invitation = factories.MailDomainInvitationFactory(
        domain=invitation_domain2.domain
    )

    # convert
    new_user = core_factories.UserFactory(email=email)

    invitations = models.MailDomainInvitation.objects.all()
    accesses = models.MailDomainAccess.objects.all()

    # invitations 1 and 2 successfully converted
    access1 = accesses.get(domain=invitation_domain1.domain, user=new_user)
    assert access1.role == invitation_domain1.role
    assert not invitations.filter(
        domain=invitation_domain1.domain, email=email
    ).exists()

    access2 = accesses.get(domain=invitation_domain2.domain, user=new_user)
    assert access2.role == invitation_domain2.role
    assert not invitations.filter(
        domain=invitation_domain2.domain, email=email
    ).exists()

    # expired invitation remains
    assert invitations.filter(domain=expired_invitation.domain, email=email).exists()

    # the other invitation remains
    assert invitations.filter(
        domain=invitation_domain2.domain, email=other_invitation.email
    ).exists()

    log_messages = [msg.message for msg in caplog.records]
    assert (
        f"Converting 2 domain invitations for new user {str(new_user)}" in log_messages
    )
