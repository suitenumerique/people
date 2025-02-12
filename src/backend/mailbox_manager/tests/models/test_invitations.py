"""
Unit tests for the Domain Invitation model
"""

import smtplib
import time
import uuid
from logging import Logger
from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.core import exceptions, mail
from django.conf import settings

import pytest
from faker import Faker
from freezegun import freeze_time

from core import factories as core_factories
from mailbox_manager import factories, models

pytestmark = pytest.mark.django_db


fake = Faker()


def test_models_domain_invitations_readonly_after_create():
    """Existing invitations should be readonly."""
    invitation = factories.DomainInvitationFactory()
    with pytest.raises(exceptions.PermissionDenied):
        invitation.save()



def test_models_domain_invitations__is_expired(settings):
    """
    The 'is_expired' property should return False until validity duration
    is exceeded and True afterwards.
    """
    expired_invitation = factories.DomainInvitationFactory()
    assert expired_invitation.is_expired is False

    settings.INVITATION_VALIDITY_DURATION = 1
    time.sleep(1)

    assert expired_invitation.is_expired is True


def test_models_domain_invitation__invitation_should_be_converted_to_accesses_upon_joining():
    """
    Upon creating a new user, invitations linked to that email
    should be converted to accesses and then deleted.
    """
    # Two invitations to the same mail but to different domains
    invitation_to_domain1 = factories.DomainInvitationFactory()
    invitation_to_domain2 = factories.DomainInvitationFactory(email=invitation_to_domain1.email)

    other_invitation = factories.DomainInvitationFactory(
        domain=invitation_to_domain2.domain
    )  # another person invited to domain2

    # an expired invitation that should not be converted
    settings.INVITATION_VALIDITY_DURATION = 1
    expired_invitation = factories.DomainInvitationFactory(email=invitation_to_domain1.email)
    time.sleep(1)

    new_user = core_factories.UserFactory(email=invitation_to_domain1.email)

    import pdb; pdb.set_trace()
    assert models.MailDomainAccess.objects.filter(
        domain=invitation_to_domain1.domain, user=new_user
    ).exists()
    assert models.MailDomainAccess.objects.filter(
        domain=invitation_to_domain2.domain, user=new_user
    ).exists()
    assert not models.Invitation.objects.filter(
        domain=invitation_to_domain1.domain, email=invitation_to_domain1.email
    ).exists()  # invitation "consumed"
    assert not models.Invitation.objects.filter(
        domain=invitation_to_domain2.domain, email=invitation_to_domain2.email
    ).exists()  # invitation "consumed"
    assert models.Invitation.objects.filter(
        domain=invitation_to_domain2.domain, email=other_invitation.email
    ).exists()  # the other invitation remains
    assert models.Invitation.objects.filter(
        domain=expired_invitation.domain, email=other_invitation.email
    ).exists()  # expired invitation remains

