"""Resource Server Backend"""

import logging

from django.conf import settings
from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation

from joserfc import jwe as jose_jwe
from joserfc import jwt as jose_jwt
from joserfc.errors import InvalidClaimError, InvalidTokenError
from requests.exceptions import HTTPError
from rest_framework.exceptions import AuthenticationFailed

from . import utils

logger = logging.getLogger(__name__)


class ResourceServerBackend:
    """Backend of an OAuth 2.0 resource server.

    This backend is designed to authenticate resource owners to our API using the access token
    they received from the authorization server.

    In the context of OAuth 2.0, a resource server is a server that hosts protected resources and
    is capable of accepting and responding to protected resource requests using access tokens.
    The resource server verifies the validity of the access tokens issued by the authorization
    server to ensure secure access to the resources.

    For more information, visit: https://www.oauth.com/oauth2-servers/the-resource-server/
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, authorization_server_client):
        # pylint: disable=invalid-name
        self.UserModel = auth.get_user_model()

        self._client_id = settings.OIDC_RS_CLIENT_ID
        self._client_secret = settings.OIDC_RS_CLIENT_SECRET
        self._encryption_encoding = settings.OIDC_RS_ENCRYPTION_ENCODING
        self._encryption_algorithm = settings.OIDC_RS_ENCRYPTION_ALGO
        self._signing_algorithm = settings.OIDC_RS_SIGNING_ALGO
        self._scopes = settings.OIDC_RS_SCOPES

        if (
            not self._client_id
            or not self._client_secret
            or not authorization_server_client
        ):
            raise ImproperlyConfigured(
                "Could not instantiate ResourceServerBackend, some parameters are missing."
            )

        self._authorization_server_client = authorization_server_client

        self._claims_registry = jose_jwt.JWTClaimsRegistry(
            iss={"essential": True, "value": self._authorization_server_client.url},
            aud={"essential": True, "value": self._client_id},
            token_introspection={"essential": True},
        )

    # pylint: disable=unused-argument
    def get_or_create_user(self, access_token, id_token, payload):
        """Maintain API compatibility with OIDCAuthentication class from mozilla-django-oidc

        Params 'id_token', 'payload' won't be used, and our implementation will only
        support 'get_user', not 'get_or_create_user'.
        """

        return self.get_user(access_token)

    def get_user(self, access_token):
        """Get user from an access token emitted by the authorization server.

        This method will submit the access token to the authorization server for
        introspection, to ensure its validity and obtain the associated metadata.

        It follows the specifications outlined in RFC7662 https://www.rfc-editor.org/info/rfc7662,
        https://datatracker.ietf.org/doc/html/draft-ietf-oauth-jwt-introspection-response-12.

        In our eGovernment applications, the standard RFC 7662 doesn't provide sufficient security.
        Its introspection response is a plain JSON object. Therefore, we use the draft RFC
        that extends RFC 7662 by returning a signed and encrypted JWT for stronger assurance that
        the authorization server issued the token introspection response.
        """
        jwt = self._introspect(access_token)
        claims = self._verify_claims(jwt)
        user_info = self._verify_user_info(claims["token_introspection"])

        sub = user_info.get("sub")
        if sub is None:
            message = "User info contained no recognizable user identification"
            logger.debug(message)
            raise SuspiciousOperation(message)
        try:
            user = self.UserModel.objects.get(sub=sub)
        except self.UserModel.DoesNotExist:
            logger.debug("Login failed: No user with %s found", sub)
            return None

        return user

    def _verify_user_info(self, introspection_response):
        """Verify the 'introspection_response' to get valid and relevant user info.

        The 'introspection_response' should be still active, and while authenticating
        the resource owner should have requested relevant scope to access her data in
        our resource server.

        Scope should be configured to match between the AS and the RS. The AS will filter
        all the scopes the resource owner requested to expose only the relevant ones to
        our resource server.
        """

        active = introspection_response.get("active", None)

        if not active:
            message = "Introspection response is not active."
            logger.debug(message)
            raise SuspiciousOperation(message)

        requested_scopes = introspection_response.get("scope", None).split(" ")
        if set(self._scopes).isdisjoint(set(requested_scopes)):
            message = "Introspection response contains any required scopes."
            logger.debug(message)
            raise SuspiciousOperation(message)

        return introspection_response

    def _introspect(self, token):
        """Introspect an access token to the authorization server."""
        try:
            jwe = self._authorization_server_client.get_introspection(
                self._client_id,
                self._client_secret,
                token,
            )
        except HTTPError as err:
            message = "Could not fetch introspection"
            logger.debug("%s. Exception:", message, exc_info=True)
            raise SuspiciousOperation(message) from err

        private_key = utils.import_private_key_from_settings()
        jws = self._decrypt(jwe, private_key=private_key)

        try:
            public_key_set = self._authorization_server_client.import_public_keys()
        except (TypeError, ValueError, AttributeError, HTTPError) as err:
            message = "Could get authorization server JWKS"
            logger.debug("%s. Exception:", message, exc_info=True)
            raise SuspiciousOperation(message) from err

        jwt = self._decode(jws, public_key_set)

        return jwt

    def _decrypt(self, encrypted_token, private_key):
        """Decrypt the token encrypted by the Authorization Server (AS).

        Resource Server (RS)'s public key is used for encryption, and its private
        key is used for decryption. The RS's public key is exposed to the AS via a JWKS endpoint.
        Encryption Algorithm and Encoding should be configured to match between the AS
        and the RS.
        """

        try:
            decrypted_token = jose_jwe.decrypt_compact(
                encrypted_token,
                private_key,
                algorithms=[self._encryption_algorithm, self._encryption_encoding],
            )
        except Exception as err:
            message = "Token decryption failed"
            logger.debug("%s. Exception:", message, exc_info=True)
            raise SuspiciousOperation(message) from err

        return decrypted_token

    def _decode(self, encoded_token, public_key_set):
        """Decode the token signed by the Authorization Server (AS).

        AS's private key is used for signing, and its public key is used for decoding.
        The AS public key is exposed via a JWK endpoint.
        Signing Algorithm should be configured to match between the AS and the RS.
        """
        try:
            token = jose_jwt.decode(
                encoded_token.plaintext,
                public_key_set,
                algorithms=[self._signing_algorithm],
            )
        except ValueError as err:
            message = "Token decoding failed"
            logger.debug("%s. Exception:", message, exc_info=True)
            raise SuspiciousOperation(message) from err

        return token

    def _verify_claims(self, token):
        """Verify the claims of the token to ensure authentication security.

        By verifying these claims, we ensure that the token was issued by a
        trusted authorization server and is intended for this specific
        resource server. This prevents various types of attacks, such as
        token substitution or misuse of tokens issued for different clients.
        """
        try:
            self._claims_registry.validate(token.claims)
        except (InvalidClaimError, InvalidTokenError) as err:
            message = "Failed to validate token's claims"
            logger.debug("%s. Exception:", message, exc_info=True)
            raise SuspiciousOperation(message) from err

        return token.claims


class ResourceServerImproperlyConfiguredBackend:
    """Fallback backend for improperly configured Resource Servers."""

    def get_or_create_user(self, access_token, id_token, payload):
        """Indicate that the Resource Server is improperly configured."""
        raise AuthenticationFailed("Resource Server is improperly configured")
