"""Token generator for RFC 8693 token exchange."""

import secrets
import uuid
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone

from joserfc import jwt
from joserfc.jwk import RSAKey


class TokenGenerator:
    """Generator for exchanged tokens (opaque or JWT)."""

    @staticmethod
    def generate_opaque_token():
        """
        Generate a secure opaque token.

        Returns:
            str: A URL-safe random token
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_jwt_token(  # noqa: PLR0913
        sub,
        email,
        audiences,
        scope,
        expires_in,
        actor_token=None,
        may_act=None,
        subject_token_jti=None,
        kid=None,
        grants=None,
    ):
        """
        Generate a signed JWT token according to RFC 8693.

        Args:
            sub: Subject identifier
            email: Subject email
            audiences: List of audience strings
            scope: Space-separated scopes or list of scopes
            expires_in: Token lifetime in seconds
            actor_token: Optional actor token for delegation
            may_act: Optional may_act claim for delegation
            subject_token_jti: JTI of the original SSO token
            kid: Key ID for signing
            grants: Optional list of grant dicts with throttle info

        Returns:
            str: A signed JWT token

        Raises:
            ValueError: If kid is not provided or not found in signing keys
        """
        if not kid:
            raise ValueError("kid is required for JWT token generation")

        signing_keys = settings.TOKEN_EXCHANGE_JWT_SIGNING_KEYS
        if kid not in signing_keys:
            raise ValueError(
                f"Key ID '{kid}' not found in TOKEN_EXCHANGE_JWT_SIGNING_KEYS"
            )

        # Prepare scope as list if it's a string
        if isinstance(scope, str):
            scope_list = scope.split() if scope else []
        else:
            scope_list = scope or []

        # Prepare claims
        now = timezone.now()
        claims = {
            "sub": sub,
            "aud": audiences,
            "scope": scope_list,
            "exp": int((now + timedelta(seconds=expires_in)).timestamp()),
            "iat": int(now.timestamp()),
            "jti": str(uuid.uuid4()),
        }

        # Add email if provided
        if email:
            claims["email"] = email

        # Add grants if provided
        if grants:
            claims["grants"] = grants

        # Add optional RFC 8693 claims
        if actor_token:
            # Extract subject from actor_token if possible, or use a placeholder
            claims["act"] = {"sub": "actor"}  # Simplified for now

        if may_act:
            claims["may_act"] = may_act

        # Prepare header with kid
        header = {
            "kid": kid,
            "alg": settings.TOKEN_EXCHANGE_JWT_ALGORITHM,
        }

        # Load the private key
        private_key_pem = signing_keys[kid]
        key = RSAKey.import_key(private_key_pem)

        # Sign the JWT
        token = jwt.encode(header, claims, key)
        return token.decode("utf-8") if isinstance(token, bytes) else token

    @staticmethod
    def verify_jwt_token(token):
        """
        Verify a JWT token signature supporting multiple keys (rotation).

        Args:
            token: The JWT token string to verify

        Returns:
            dict: The decoded claims if valid

        Raises:
            ValueError: If token is invalid or signature verification fails
        """
        # Decode header to get kid
        try:
            # Decode without verification first to get the kid
            unverified = jwt.decode(token, None)
            kid = unverified.header.get("kid")

            if not kid:
                raise ValueError("JWT token missing 'kid' in header")

            signing_keys = settings.TOKEN_EXCHANGE_JWT_SIGNING_KEYS
            if kid not in signing_keys:
                raise ValueError(
                    f"Key ID '{kid}' not found in TOKEN_EXCHANGE_JWT_SIGNING_KEYS"
                )

            # Load the public key and verify
            private_key_pem = signing_keys[kid]
            key = RSAKey.import_key(private_key_pem)

            # Verify and decode
            claims = jwt.decode(token, key)
            return claims

        except Exception as exc:
            raise ValueError(f"Invalid JWT token: {exc}") from exc
