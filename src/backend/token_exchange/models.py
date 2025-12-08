"""Models for the auth application."""

import datetime
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.db.models import JSONField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel, ServiceProvider

logger = logging.getLogger(__name__)

User = get_user_model()


def validate_action_scope_name(value):
    if not value.startswith("action:"):
        raise ValidationError(_("Action name must start with 'action:'"))


class TokenTypeChoices(models.TextChoices):
    """Token type choices for RFC 8693."""

    ACCESS_TOKEN = "access_token", _("Access Token")
    JWT = "jwt", _("JWT")


class ServiceProviderCredentials(BaseModel):
    """
    Allow to define credentials for a Service Provider.

    We could (should?) inherit from AbstractApplication and swap Application, but
    for now we prefer to keep thing simple.
    """

    service_provider = models.ForeignKey(
        ServiceProvider,
        on_delete=models.CASCADE,
        related_name="token_exchange_credentials",
        blank=False,
        null=False,
    )
    client_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name=_("Client ID"),
    )
    client_secret = models.CharField(  # Should be hashed
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name=_("Client secret"),
    )

    allowed_origins = models.TextField(
        blank=True,
        help_text=_("Allowed origins list to enable CORS, space separated"),
        default="",
    )
    is_active = models.BooleanField(
        default=True,
    )

    def clean(self):
        """Validate allowed origins URLs."""
        super().clean()

        if allowed_origins := self.allowed_origins.strip().split():
            validator = URLValidator(
                settings.TOKEN_EXCHANGE_ALLOWED_SCHEMES, "allowed origin"
            )
            for url in allowed_origins:
                validator(url)


class TokenExchangeRule(BaseModel):
    """
    Defines a token exchange rule from one service provider to another.

    This model represents the authorization for a source service to exchange
    tokens for accessing a target service.
    """

    source_service = models.ForeignKey(
        ServiceProvider,
        related_name="exchange_out",
        on_delete=models.CASCADE,
        verbose_name=_("Source Service"),
        help_text=_("Service provider initiating the token exchange"),
    )
    target_service = models.ForeignKey(
        ServiceProvider,
        related_name="exchange_in",
        on_delete=models.CASCADE,
        verbose_name=_("Target Service"),
        help_text=_("Service provider receiving the exchanged token"),
    )

    exchanged_token_duration = models.DurationField(
        blank=True,
        default=datetime.timedelta(minutes=5),
        help_text=_("Duration of the generated token"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
    )

    class Meta:
        unique_together = ("source_service", "target_service")
        db_table = "token_exchange_rule"
        verbose_name = _("Token Exchange Rule")
        verbose_name_plural = _("Token Exchange Rules")

    def __str__(self):
        return f"{self.source_service} → {self.target_service}"


class ScopeGrant(BaseModel):
    """
    Defines a scope grant within a token exchange rule.

    Maps a source scope to a granted scope on the target service,
    with optional throttling constraints. Can perform downscoping
    (reducing privileges) or upscoping (elevating privileges)
    depending on the configuration.
    """

    rule = models.ForeignKey(
        TokenExchangeRule,
        on_delete=models.CASCADE,
        related_name="scope_grants",
        verbose_name=_("Exchange Rule"),
    )

    source_scope = models.CharField(
        max_length=255,
        verbose_name=_("Source Scope"),
        help_text=_("Scope from the source token"),
    )
    granted_scope = models.CharField(
        max_length=255,
        verbose_name=_("Granted Scope"),
        help_text=_("Scope granted on the target service"),
    )

    throttle_rate = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name=_("Throttle Rate"),
        help_text=_("Optional throttle rate (e.g., '5/h', '100/day')"),
    )

    class Meta:
        db_table = "token_exchange_scope_grant"
        verbose_name = _("Scope Grant")
        verbose_name_plural = _("Scope Grants")
        unique_together = ("rule", "source_scope", "granted_scope")

    def __str__(self):
        return f"{self.source_scope} → {self.granted_scope} (rule: {self.rule_id})"


class ActionScope(BaseModel):
    """
    Defines an action scope that can grant access to multiple services.

    An action scope is a special scope that, when requested, can grant
    access to specific scopes on different target services.
    """

    name = models.CharField(
        max_length=255,
        unique=True,
        validators=[validate_action_scope_name],
        verbose_name=_("Action Name"),
        help_text=_("Unique identifier for this action scope, starts with 'action:'"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Human-readable description of this action"),
    )

    class Meta:
        db_table = "token_exchange_action_scope"
        verbose_name = _("Action Scope")
        verbose_name_plural = _("Action Scopes")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Ensure the action name is stored in lowercase."""
        if self.name:
            self.name = self.name.lower()
        super().save(*args, **kwargs)


class ActionScopeGrant(BaseModel):
    """
    Defines a scope grant for an action on a specific target service.

    This model maps an action to specific scopes on a target service,
    with optional throttling constraints.
    """

    action = models.ForeignKey(
        ActionScope,
        on_delete=models.CASCADE,
        related_name="grants",
        verbose_name=_("Action Scope"),
    )

    target_service = models.ForeignKey(
        ServiceProvider,
        on_delete=models.CASCADE,
        related_name="action_grants",
        verbose_name=_("Target Service"),
    )
    granted_scope = models.CharField(
        max_length=255,
        verbose_name=_("Granted Scope"),
        help_text=_("Scope granted on the target service when action is used"),
    )

    throttle_rate = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name=_("Throttle Rate"),
        help_text=_("Optional throttle rate (e.g., '5/h', '100/day')"),
    )

    class Meta:
        db_table = "token_exchange_action_scope_grant"
        verbose_name = _("Action Scope Grant")
        verbose_name_plural = _("Action Scope Grants")
        unique_together = ("action", "target_service", "granted_scope")

    def __str__(self):
        return f"{self.action.name} → {self.granted_scope} on {self.target_service}"


class TokenExchangeActionPermission(BaseModel):
    """
    Defines permissions for using an action within a token exchange rule.

    This model specifies which actions can be used within a token exchange
    and what source scopes are required to use them.
    """

    rule = models.ForeignKey(
        TokenExchangeRule,
        on_delete=models.CASCADE,
        related_name="action_permissions",
        verbose_name=_("Exchange Rule"),
    )

    action = models.ForeignKey(
        ActionScope,
        on_delete=models.CASCADE,
        related_name="permissions",
        verbose_name=_("Action Scope"),
    )

    required_source_scope = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Required Source Scope"),
        help_text=_(
            "Scope required in source token to use this action (empty = no requirement)"
        ),
    )

    class Meta:
        db_table = "token_exchange_action_permission"
        verbose_name = _("Token Exchange Action Permission")
        verbose_name_plural = _("Token Exchange Action Permissions")
        unique_together = ("rule", "action")

    def __str__(self):
        return f"{self.action.name} in rule {self.rule_id}"


class ExchangedToken(BaseModel):
    """
    Model representing an exchanged token according to RFC 8693.

    This model stores tokens that have been exchanged from an external SSO
    via the token exchange endpoint. It supports both opaque tokens and
    signed JWT tokens with key rotation.
    """

    token = models.CharField(
        max_length=None,
        unique=True,
        db_index=True,
        verbose_name=_("Token"),
        help_text=_("The actual token string (opaque or JWT)"),
    )
    token_type = models.CharField(
        max_length=50,
        choices=TokenTypeChoices.choices,
        default=TokenTypeChoices.ACCESS_TOKEN,
        verbose_name=_("Token Type"),
        help_text=_("The type of token as per RFC 8693"),
    )
    jwt_kid = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("JWT Key ID"),
        help_text=_("The key ID used to sign the JWT token"),
    )
    subject_sub = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("Subject Sub"),
        help_text=_("The subject identifier (sub) from the introspection"),
    )
    subject_email = models.EmailField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("Subject Email"),
        help_text=_("The subject email from the introspection"),
    )
    audiences = ArrayField(
        models.CharField(max_length=255),
        default=list,
        verbose_name=_("Audiences"),
        help_text=_("The audiences for this token (RFC 8693 supports multiple)"),
    )
    scope = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Scope"),
        help_text=_("Space-separated scopes for this token"),
    )
    grants = JSONField(
        null=True,
        blank=True,
        default=list,
        verbose_name=_("Grants"),
        help_text=_("List of grant objects with scope and throttling information"),
    )
    expires_at = models.DateTimeField(
        db_index=True,
        verbose_name=_("Expires At"),
        help_text=_("When this token expires"),
    )
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("Revoked At"),
        help_text=_("When this token was revoked (null if not revoked)"),
    )
    actor_token = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Actor Token"),
        help_text=_("The actor token for delegation (RFC 8693)"),
    )
    may_act = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_("May Act"),
        help_text=_("The may_act claim for delegation (RFC 8693)"),
    )
    subject_token_jti = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name=_("Subject Token JTI"),
        help_text=_("The JTI of the original SSO token for traceability"),
    )
    subject_token_scope = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Subject Token Scope"),
        help_text=_("The original scopes from the SSO token"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("When this token was created"),
    )

    class Meta:
        db_table = "token_exchange_exchanged_token"
        ordering = ["-created_at"]
        verbose_name = _("Exchanged Token")
        verbose_name_plural = _("Exchanged Tokens")
        indexes = [
            models.Index(fields=["subject_sub", "created_at"]),
            models.Index(fields=["subject_email", "created_at"]),
            models.Index(fields=["expires_at", "revoked_at"]),
        ]

    def __str__(self):
        """String representation of the token."""
        identity = self.subject_email or self.subject_sub or "unknown"
        return f"{self.token_type} for {identity} (expires {self.expires_at})"

    def is_expired(self):
        """Check if the token has expired."""
        return timezone.now() >= self.expires_at

    def is_revoked(self):
        """Check if the token has been revoked."""
        return self.revoked_at is not None

    def is_valid(self):
        """Check if the token is valid (not expired and not revoked)."""
        return not self.is_expired() and not self.is_revoked()

    def revoke(self):
        """Revoke this token."""
        if not self.is_revoked():
            self.revoked_at = timezone.now()
            self.save(update_fields=["revoked_at", "updated_at"])

    def to_introspection_response(self):
        """
        Convert this token to an RFC 7662 introspection response.

        Returns:
            dict: The introspection response payload
        """
        if not self.is_valid():
            return {"active": False}

        return {
            "active": True,
            "scope": self.scope,
            "username": self.subject_email or self.subject_sub,
            "token_type": self.token_type,
            "exp": int(self.expires_at.timestamp()),
            "iat": int(self.created_at.timestamp()),
            "sub": self.subject_sub,
            "email": self.subject_email,
            "aud": self.audiences,
            "jti": self._get_jti(),
            "client_id": settings.OIDC_RS_CLIENT_ID,
        }

    def _get_jti(self):
        """Extract or generate a JTI for this token."""
        if self.token_type == TokenTypeChoices.JWT:
            # For JWT tokens, we could extract the jti from the token itself
            # For now, we use a stable identifier
            return self.subject_token_jti
        # For opaque tokens, use the token itself as identifier
        return self.token[:50]  # Truncate for readability

    def save(self, *args, **kwargs):
        """Override save to enforce token limit per user when creating a new token.

        This ensures that both tokens created through the view and tokens created
        directly in tests/fixtures will respect the per-user limit.
        """
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new:
            # Enforce token limit after creation to ensure created_at is set
            try:
                max_tokens = settings.TOKEN_EXCHANGE_MAX_ACTIVE_TOKENS_PER_USER
            except AttributeError:
                # Setting not present — nothing to enforce
                return

            if max_tokens is None:
                return

            # Filter by subject_sub or subject_email
            if self.subject_sub:
                active_tokens_qs = ExchangedToken.objects.filter(
                    subject_sub=self.subject_sub,
                    expires_at__gt=timezone.now(),
                    revoked_at__isnull=True,
                )
            elif self.subject_email:
                active_tokens_qs = ExchangedToken.objects.filter(
                    subject_email=self.subject_email,
                    expires_at__gt=timezone.now(),
                    revoked_at__isnull=True,
                )
            else:
                # No identity to group by
                return

            active_tokens_qs = active_tokens_qs.order_by("created_at")

            active_tokens_count = active_tokens_qs.count()
            if active_tokens_count > max_tokens:
                # Number to delete
                to_delete = active_tokens_count - max_tokens
                oldest = active_tokens_qs[:to_delete]
                ids = [t.id for t in oldest]
                ExchangedToken.objects.filter(id__in=ids).delete()
                logger.info(
                    "Enforced token limit for sub=%s/email=%s: deleted %d oldest tokens",
                    self.subject_sub,
                    self.subject_email,
                    to_delete,
                )
