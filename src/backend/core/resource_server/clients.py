"""Resource Server Clients classes"""

from django.core.exceptions import ImproperlyConfigured

import requests
from joserfc.jwk import KeySet


class AuthorizationServerClient:
    """Client for interacting with an OAuth 2.0 authorization server.

    An authorization server issues access tokens to client applications after authenticating
    and obtaining authorization from the resource owner. It also provides endpoints for token
    introspection and JSON Web Key Sets (JWKS) to validate and decode tokens.

    This client facilitates communication with the authorization server, including:
    - Fetching token introspection responses.
    - Fetching JSON Web Key Sets (JWKS) for token validation.
    - Setting appropriate headers for secure communication as recommended by RFC drafts.
    """

    # ruff: noqa: PLR0913
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        url,
        url_jwks,
        url_introspection,
        verify_ssl,
        timeout,
        proxy,
    ):
        if not url or not url_jwks or not url_introspection:
            raise ImproperlyConfigured(
                "Could not instantiate AuthorizationServerClient, some parameters are missing."
            )

        self.url = url
        self._url_introspection = url_introspection
        self._url_jwks = url_jwks
        self._verify_ssl = verify_ssl
        self._timeout = timeout
        self._proxy = proxy

    @property
    def _introspection_headers(self):
        """Get HTTP header for the introspection request.

        Notify the authorization server that we expect a signed and encrypted response
        by setting the appropriate 'Accept' header.

        This follows the recommendation from the draft RFC:
        https://datatracker.ietf.org/doc/html/draft-ietf-oauth-jwt-introspection-response-12.
        """
        return {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/token-introspection+jwt",
        }

    def get_introspection(self, client_id, client_secret, token):
        """Retrieve introspection response about a token."""
        response = requests.post(
            self._url_introspection,
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "token": token,
            },
            headers=self._introspection_headers,
            verify=self._verify_ssl,
            timeout=self._timeout,
            proxies=self._proxy,
        )
        response.raise_for_status()
        return response.text

    def get_jwks(self):
        """Retrieve Authorization Server JWKS."""
        response = requests.get(
            self._url_jwks,
            verify=self._verify_ssl,
            timeout=self._timeout,
            proxies=self._proxy,
        )
        response.raise_for_status()
        return response.json()

    def import_public_keys(self):
        """Retrieve and import Authorization Server JWKS."""

        jwks = self.get_jwks()
        public_keys = KeySet.import_key_set(jwks)

        return public_keys
