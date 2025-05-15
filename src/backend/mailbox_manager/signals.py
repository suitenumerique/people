"""
Signals module for the mailbox_manager app.
"""

import logging
from datetime import timedelta

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from core.models import User

from mailbox_manager.models import MailDomainAccess, MailDomainInvitation

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def convert_domain_invitations(sender, created, instance, **kwargs):  # pylint: disable=unused-argument
    """
    Convert valid domain invitations to domain accesses for a given user.
    Expired invitations are ignored.
    """
    logger.info("Convert domain invitations for user %s", instance)
    if created:
        valid_domain_invitations = MailDomainInvitation.objects.filter(
            email=instance.email,
            created_at__gte=(
                timezone.now()
                - timedelta(seconds=settings.INVITATION_VALIDITY_DURATION)
            ),
        )

        if not valid_domain_invitations.exists():
            return

        MailDomainAccess.objects.bulk_create(
            [
                MailDomainAccess(
                    user=instance, domain=invitation.domain, role=invitation.role
                )
                for invitation in valid_domain_invitations
            ]
        )

        valid_domain_invitations.delete()
        logger.info("Invitations converted to domain accesses for user %s", instance)
