import logging
from typing import Tuple

from django.utils.translation import gettext_lazy as _

from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from . import models

logger = logging.getLogger(__name__)


class OrganizationOneTimeTokenAuthentication(TokenAuthentication):
    """
    Simple token based authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "OrganizationToken ".  For example:

        Authorization: OrganizationToken 401f7ac837da42b97f613d789819ff93537bee6a
    """

    keyword = 'OrganizationToken'
    model = models.OrganizationOneTimeToken

    def authenticate_credentials(self, key) -> Tuple[models.Organization, models.OrganizationOneTimeToken]:
        model = self.get_model()
        try:
            token = model.objects.select_related('organization').get(key=key)
        except model.DoesNotExist:
            logger.warning("Invalid token: %s", key)
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if token.used_at or not token.enabled:
            logger.warning("Token is disabled: %s", key)
            raise exceptions.AuthenticationFailed(_('Token is disabled.'))

        if not self.organization_can_authenticate(token.organization):
            logger.warning("Token cannot authenticate organization: %s", token.organization)
            raise exceptions.AuthenticationFailed(_('Token cannot be used for authentication.'))

        logger.info('OrganizationOneTimeToken authenticated: %s', token.organization)
        return (token.organization, token)

    @staticmethod
    def organization_can_authenticate(organization) -> bool:
        """Check if the organization can authenticate.

        We only allow authentication for the first user of the organization.

        Parameters:
        - organization (Organization): The organization object.

        Returns:
        - bool: True if the user can authenticate, otherwise False.
        """
        return not organization.users.exists()
