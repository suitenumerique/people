"""Resource Server Authentication"""

import base64
import binascii
import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from mozilla_django_oidc.contrib.drf import OIDCAuthentication

from .backend import ResourceServerBackend, ResourceServerImproperlyConfiguredBackend
from .clients import AuthorizationServerClient

logger = logging.getLogger(__name__)


class ResourceServerAuthentication(OIDCAuthentication):
    """Authenticate clients using the token received from the authorization server."""

    def __init__(self):
        super().__init__()

        try:
            authorization_server_client = AuthorizationServerClient(
                url=settings.OIDC_OP_URL,
                verify_ssl=settings.OIDC_VERIFY_SSL,
                timeout=settings.OIDC_TIMEOUT,
                proxy=settings.OIDC_PROXY,
                url_jwks=settings.OIDC_OP_JWKS_ENDPOINT,
                url_introspection=settings.OIDC_OP_INTROSPECTION_ENDPOINT,
            )
            self.backend = ResourceServerBackend(authorization_server_client)

        except ImproperlyConfigured as err:
            message = "Resource Server authentication is disabled"
            logger.debug("%s. Exception: %s", message, err)
            self.backend = ResourceServerImproperlyConfiguredBackend()

    def get_access_token(self, request):
        """Retrieve and decode the access token from the request.

        This method overcharges the 'get_access_token' method from the parent class,
        to support service providers that would base64 encode the bearer token.
        """

        access_token = super().get_access_token(request)

        try:
            access_token = base64.b64decode(access_token).decode("utf-8")
        except (binascii.Error, TypeError):
            pass

        return access_token
