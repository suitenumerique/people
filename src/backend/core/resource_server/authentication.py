"""Resource Server Authentication"""

import base64
import binascii
import logging
from functools import lru_cache

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from mozilla_django_oidc.contrib.drf import OIDCAuthentication

from .backend import ResourceServerImproperlyConfiguredBackend
from .clients import AuthorizationServerClient

logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def get_resource_server_backend():
    """Return the resource server backend class based on the settings."""
    return import_string(settings.OIDC_RS_BACKEND_CLASS)


class ResourceServerAuthentication(OIDCAuthentication):
    """Authenticate clients using the token received from the authorization server."""

    def __init__(self):
        """Require authentication to be configured in order to instantiate."""
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
            self.backend = get_resource_server_backend()(authorization_server_client)

        except ImproperlyConfigured as err:
            message = "Resource Server authentication is disabled"
            logger.debug("%s. Exception: %s", message, err)
            self.backend = ResourceServerImproperlyConfiguredBackend()

    def get_access_token(self, request):
        """Retrieve and decode the access token from the request.

        This method overrides the 'get_access_token' method from the parent class,
        to support service providers that would base64 encode the bearer token.
        """

        access_token = super().get_access_token(request)

        try:
            access_token = base64.b64decode(access_token).decode("utf-8")
        except (binascii.Error, TypeError):
            pass

        return access_token

    def authenticate(self, request):
        """
        Authenticate the request and return a tuple of (user, token) or None.

        We override the 'authenticate' method from the parent class to store
        the introspected token audience inside the request.
        """
        result = super().authenticate(request)  # Might raise AuthenticationFailed

        if result is None:  # Case when there is no access token
            return None

        # Note: at this stage, the request is a "drf_request" object
        request.resource_server_token_audience = self.backend.token_origin_audience

        return result
