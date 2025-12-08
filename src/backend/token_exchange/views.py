"""Views for the token_exchange application."""

import logging
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.db.models import F
from django.utils import timezone
from django.utils.module_loading import import_string

from lasuite.oidc_resource_server.backend import ResourceServerBackend
from requests import HTTPError
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .authentication import ServiceProviderBasicAuthentication
from .models import (
    ActionScopeGrant,
    ExchangedToken,
    ScopeGrant,
    TokenExchangeActionPermission,
    TokenExchangeRule,
    TokenTypeChoices,
)
from .permissions import IsServiceProviderAuthenticated
from .serializers import TokenExchangeSerializer, TokenRevocationSerializer
from .token_generator import TokenGenerator

logger = logging.getLogger(__name__)


def get_resource_server_introspection_backend() -> type[ResourceServerBackend]:
    """Return the resource server backend class based on the settings."""
    return import_string(settings.OIDC_RS_BACKEND_CLASS)


class TokenExchangeView(APIView):
    """
    RFC 8693 Token Exchange endpoint.

    This endpoint allows exchanging an external SSO token
    for a new token with different audiences, scopes,
    or lifetime.

    POST /auth/token/exchange/
        Exchange a token according to RFC 8693
    """

    authentication_classes = [ServiceProviderBasicAuthentication]
    permission_classes = [IsServiceProviderAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    parser_classes = [FormParser, JSONParser]
    throttle_scope = "token_exchange"

    @staticmethod
    def generate_invalid_target_response():
        """Generate the RFC invalid_target error response."""
        return Response(
            {
                "error": "invalid_target",
                "error_description": "Invalid target audience",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def post(self, request):  # noqa: PLR0911, PLR0912, PLR0915
        """
        Handle token exchange requests.

        Validates the request, checks scopes, generates a new token,
        and returns an RFC 8693 compliant response.
        """
        # Check if feature is enabled
        if not settings.TOKEN_EXCHANGE_ENABLED:
            return Response(
                {
                    "error": "token_exchange_disabled",
                    "error_description": "Token exchange feature is not enabled",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Retrieve authenticated service provider
        service_provider = request.user

        # Validate request
        serializer = TokenExchangeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "error": "invalid_request",
                    "error_description": str(serializer.errors),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated_data = serializer.validated_data

        # Retrieve targeted service providers, by default it's the requesting one
        requested_audiences = validated_data.get(
            "audience",
            [service_provider.audience_id],  # compared to introspection result later
        )

        rules = TokenExchangeRule.objects.filter(
            source_service=service_provider,
            target_service__audience_id__in=requested_audiences,
        ).select_related("target_service")

        # Sanity check: we check each requested audience has a rule (and therefore exists)
        __known_audiences = {rule.target_service.audience_id for rule in rules}

        if not __known_audiences:
            logger.error(
                "Only unknown audiences requested: %s",
                ", ".join(requested_audiences),
            )
            return self.generate_invalid_target_response()

        if __unknown_services := (set(requested_audiences) - __known_audiences):
            logger.warning(
                "Unknown audiences requested: %s",
                ", ".join(__unknown_services),
            )
            return self.generate_invalid_target_response()

        if any(not rule.is_active for rule in rules):
            logger.warning(
                "Some rules are inactive: %s",
                ", ".join(str(rule.pk) for rule in rules if not rule.is_active),
            )
            return self.generate_invalid_target_response()

        # Retrieve the user from subject_token, the only token type
        # accepted for now is the access token -> needs introspection
        subject_token = validated_data["subject_token"]

        # XXX : manage the user impersonation case ???? another view ?
        try:
            introspection_backend = get_resource_server_introspection_backend()()
            introspection_backend._scopes = [  # noqa: SLF001
                "openid"
            ]  # Prevent backend from enforcing scopes: MUST improve code here
            user_info = introspection_backend.get_user_info_with_introspection(
                subject_token
            )
            if (
                introspection_backend.token_origin_audience
                != service_provider.audience_id
            ):
                logger.error(
                    "Introspected token origin is different from requesting service: %s, %s",
                    introspection_backend.token_origin_audience,
                    service_provider.audience_id,
                )
                raise SuspiciousOperation()
        except HTTPError as exc:
            logger.exception("Failed to introspect subject token: %s", exc)
            raise

        # Check the user audience is the same as the requesting service
        if (
            user_info.get(settings.OIDC_RS_AUDIENCE_CLAIM)
            != service_provider.audience_id
        ):
            logger.error(
                "Introspected token audience is different from requesting service: %s, %s",
                user_info.get(settings.OIDC_RS_AUDIENCE_CLAIM),
                service_provider.audience_id,
            )
            raise SuspiciousOperation()

        # Extract subject token scope
        subject_token_scope = user_info.get("scope", "")
        subject_token_jti = user_info.get("jti", "unknown")

        # Extract identity (sub or email)
        subject_sub = user_info.get("sub")
        subject_email = user_info.get("email")

        if not subject_sub and not subject_email:
            # We need at least one identity
            logger.warning("Introspection response missing both 'sub' and 'email'")
            return Response(
                {
                    "error": "invalid_token",
                    "error_description": "Subject token introspection failed to provide identity (sub or email)",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parse subject token scopes
        subject_scopes = (
            set(subject_token_scope.split()) if subject_token_scope else set()
        )

        # Parse requested scopes
        # If not scope specifically required, we switch to "best-effort" mode by returning
        # the same scopes as the subject token and ignoring the ones not allowed.
        _missing_requested_scope_fails = True
        requested_scopes_and_actions = set(validated_data.get("scope", []))
        if not requested_scopes_and_actions:
            requested_actions = None
            requested_scopes = subject_scopes
            _missing_requested_scope_fails = False
        else:
            requested_actions = {
                s for s in requested_scopes_and_actions if s.startswith("action:")
            }
            requested_scopes = requested_scopes_and_actions - requested_actions

        # Dev note: requested_actions is a list with at most one element to prevent
        # action with different throttling to interfere. The serializer is currently
        # doing the job to limit this, yet we add another check here.
        if requested_actions:
            if len(requested_actions) > 1:
                logger.warning("Multiple actions requested: %s", requested_actions)
                return self.generate_invalid_target_response()
            if requested_scopes:
                # TODO: allow distinct scope (ie not contained in action) to be requested.
                logger.warning(
                    "Action requested along common scopes: %s, %s",
                    requested_actions,
                    requested_scopes,
                )
                return self.generate_invalid_target_response()

        # Build the global request matrix
        requested_accesses = set()
        for audience_id in requested_audiences:
            for requested_scope in requested_scopes:
                requested_accesses.add(f"{audience_id}:{requested_scope}")

        # Get the global access rules:
        existing_access = {}
        for scope_grant in ScopeGrant.objects.filter(
            rule__in=rules, source_scope__in=subject_scopes
        ).annotate(
            audience_id=F("rule__target_service__audience_id"),
        ):
            existing_access[
                f"{scope_grant.audience_id}:{scope_grant.granted_scope}"
            ] = scope_grant

        if _missing_requested_scope_fails and not requested_accesses.issubset(
            set(existing_access.keys())
        ):
            return self.generate_invalid_target_response()

        # Compute granted scopes and grants list
        granted_scopes = set()
        granted_actions = set()
        grants_dict = {}

        # Process scope grants
        for requested_access in requested_accesses:
            try:
                scope_grant = existing_access[requested_access]
            except KeyError:
                if _missing_requested_scope_fails:
                    raise
                continue

            if scope_grant.source_scope not in subject_scopes:
                logger.info("Missing user scope: %s", scope_grant.source_scope)
                if _missing_requested_scope_fails:
                    return self.generate_invalid_target_response()
            granted_scopes.add(scope_grant.granted_scope)
            audience_id = scope_grant.audience_id
            grants_dict.setdefault(audience_id, []).append(
                {
                    "scope": scope_grant.granted_scope,
                    "throttle": (
                        {"rate": scope_grant.throttle_rate}
                        if scope_grant.throttle_rate
                        else {}
                    ),
                }
            )

        # Process action scopes
        action_permissions = TokenExchangeActionPermission.objects.filter(
            rule__in=rules
        ).select_related("action")

        for action_perm in action_permissions:
            # Check if user has required source scope for this action
            if action_perm.required_source_scope:
                if action_perm.required_source_scope not in subject_scopes:
                    continue  # User doesn't have required scope, skip this action

            # Check if action is requested (action scopes are prefixed with "action:")
            if requested_scopes and action_perm.action.name not in requested_scopes:
                continue  # Action not requested, skip

            # Grant all scopes associated with this action on the target service
            action_grants = ActionScopeGrant.objects.filter(
                action=action_perm.action,
                target_service__audience_id__in=requested_audiences,
            )
            if action_grants:
                granted_actions.add(action_perm.action.name)
            for ag in action_grants:
                granted_scopes.add(ag.granted_scope)
                audience_id = ag.target_service.audience_id
                grants_dict.setdefault(audience_id, []).append(
                    {
                        "scope": ag.granted_scope,
                        "throttle": (
                            {"rate": ag.throttle_rate} if ag.throttle_rate else {}
                        ),
                    }
                )

        # If scopes were requested, validate they're all granted
        if (
            requested_scopes
            and not requested_scopes.issubset(granted_scopes)
            and _missing_requested_scope_fails
        ):
            missing_scopes = requested_scopes - granted_scopes
            logger.error(
                "Requested scopes cannot be granted. Missing scopes: %s",
                ", ".join(missing_scopes),
            )
            return self.generate_invalid_target_response()

        if requested_actions and not requested_actions.issubset(granted_actions):
            missing_actions = requested_actions - granted_actions
            logger.error(
                "Requested actions cannot be granted. Missing actions: %s",
                ", ".join(missing_actions),
            )
            return self.generate_invalid_target_response()

        if not granted_scopes:
            logger.warning("No scopes granted: %s", requested_scopes_and_actions)
            return self.generate_invalid_target_response()

        # Convert granted scopes to string
        final_scope = " ".join(sorted(granted_scopes)) if granted_scopes else ""

        # Determine token type and format
        token_type = (
            validated_data.get("requested_token_type") or TokenTypeChoices.ACCESS_TOKEN
        )

        # Determine expires_in from rule or default
        expires_in = (
            validated_data.get("expires_in")
            # XXX or int(rule.exchanged_token_duration.total_seconds())
            or settings.TOKEN_EXCHANGE_DEFAULT_EXPIRES_IN
        )

        # Determine token audiences
        if settings.TOKEN_EXCHANGE_MULTI_AUDIENCES_ALLOWED:
            audiences = requested_audiences
        else:
            audiences = [requested_audiences[0]]

        # Generate token
        if token_type == TokenTypeChoices.JWT:
            kid = settings.TOKEN_EXCHANGE_JWT_CURRENT_KID
            if not kid:
                return Response(
                    {
                        "error": "server_error",
                        "error_description": "JWT signing key not configured",
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            try:
                token_value = TokenGenerator.generate_jwt_token(
                    sub=subject_sub,
                    email=subject_email,
                    audiences=audiences,
                    scope=final_scope,
                    expires_in=expires_in,
                    actor_token=validated_data.get("actor_token"),
                    may_act=None,  # TODO: Parse from actor_token if needed
                    subject_token_jti=subject_token_jti,
                    kid=kid,
                    grants=grants_dict if grants_dict else None,
                )
            except ValueError as exc:
                return Response(
                    {"error": "server_error", "error_description": str(exc)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            token_value = TokenGenerator.generate_opaque_token()
            kid = None

        # Create ExchangedToken record
        expires_at = timezone.now() + timedelta(seconds=expires_in)
        _exchanged_token = ExchangedToken.objects.create(
            token=token_value,
            token_type=token_type,
            jwt_kid=kid,
            subject_sub=subject_sub,
            subject_email=subject_email,
            audiences=audiences,
            scope=final_scope,
            grants=grants_dict if grants_dict else None,
            expires_at=expires_at,
            actor_token=validated_data.get("actor_token"),
            may_act=None,  # TODO: Parse from actor_token if needed
            subject_token_jti=subject_token_jti,
            subject_token_scope=subject_token_scope,
        )

        # Log the exchange
        logger.info(
            "Token exchanged: sub=%s, email=%s, audiences=%s, token_type=%s, "
            "expires_in=%s, subject_jti=%s, kid=%s, scopes_granted=%s, grants=%s",
            subject_sub,
            subject_email,
            audiences,
            token_type,
            expires_in,
            subject_token_jti,
            kid,
            final_scope,
            len(grants_dict),
        )

        # Return RFC 8693 response
        response_data = {
            "access_token": token_value,
            "issued_token_type": f"urn:ietf:params:oauth:token-type:{token_type}",
            "token_type": "Bearer",
            "expires_in": expires_in,
        }

        if final_scope:
            response_data["scope"] = final_scope

        if grants_dict:
            response_data["grants"] = grants_dict

        return Response(response_data, status=status.HTTP_200_OK)


class TokenIntrospectionView(APIView):
    """
    RFC 7662 Token Introspection endpoint.

    This endpoint allows validating exchanged tokens and retrieving
    their metadata.

    POST /auth/token/introspect/
        Introspect a token according to RFC 7662
    """

    authentication_classes = [ServiceProviderBasicAuthentication]
    permission_classes = [IsServiceProviderAuthenticated]

    def post(self, request):
        """
        Handle token introspection requests.

        Accepts a token and returns its validity and metadata.
        """
        # Get token from request (form-encoded or JSON)
        token = request.data.get("token")
        if not token:
            return Response(
                {"active": False},
                status=status.HTTP_200_OK,
            )

        # Look up the token
        try:
            exchanged_token = ExchangedToken.objects.get(token=token)
        except ExchangedToken.DoesNotExist:
            logger.info("Token introspected: token not found, active=False")
            return Response({"active": False}, status=status.HTTP_200_OK)

        # Check if valid
        if not exchanged_token.is_valid():
            logger.info(
                "Token introspected: token_jti=%s, active=False, format=%s",
                exchanged_token.subject_token_jti,
                exchanged_token.token_type,
            )
            return Response({"active": False}, status=status.HTTP_200_OK)

        # For JWT tokens, verify signature
        if exchanged_token.token_type == TokenTypeChoices.JWT:
            try:
                TokenGenerator.verify_jwt_token(token)
            except ValueError as exc:
                logger.warning(
                    "Token introspected: JWT signature verification failed: %s",
                    str(exc),
                )
                return Response({"active": False}, status=status.HTTP_200_OK)

        # Return introspection response
        response_data = exchanged_token.to_introspection_response()

        logger.info(
            "Token introspected: token_jti=%s, active=%s, format=%s, kid=%s",
            exchanged_token.subject_token_jti,
            response_data["active"],
            exchanged_token.token_type,
            exchanged_token.jwt_kid or "N/A",
        )

        return Response(response_data, status=status.HTTP_200_OK)


class TokenRevocationView(APIView):
    """
    RFC 7009 Token Revocation endpoint.

    This endpoint allows revoking exchanged tokens before their
    natural expiration.

    POST /auth/token/revoke/
        Revoke a token according to RFC 7009
    """

    authentication_classes = [ServiceProviderBasicAuthentication]
    permission_classes = [IsServiceProviderAuthenticated]

    def post(self, request):
        """
        Handle token revocation requests.

        Accepts a token and revokes it.
        """
        # Validate request
        serializer = TokenRevocationSerializer(data=request.data)
        if not serializer.is_valid():
            # RFC 7009: Return 200 even for invalid requests
            return Response(status=status.HTTP_200_OK)

        token = serializer.validated_data["token"]

        # Look up the token
        try:
            exchanged_token = ExchangedToken.objects.get(
                token=token,
            )
        except ExchangedToken.DoesNotExist:
            # RFC 7009: Silent success even if token doesn't exist
            logger.info("Token revocation attempted: token not found")
            return Response(status=status.HTTP_200_OK)

        # Revoke the token
        exchanged_token.revoke()

        logger.info(
            "Token revoked: token_jti=%s, sub=%s, email=%s, type=%s, audiences=%s",
            exchanged_token.subject_token_jti,
            exchanged_token.subject_sub,
            exchanged_token.subject_email,
            exchanged_token.token_type,
            exchanged_token.audiences,
        )

        return Response(status=status.HTTP_200_OK)
