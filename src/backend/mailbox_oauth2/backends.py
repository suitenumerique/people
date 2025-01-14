"""Authentication backend for OIDC provider"""

import logging
from email.errors import HeaderParseError
from email.headerregistry import Address

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.core.cache import cache
from django.utils.text import slugify

from mailbox_manager.models import Mailbox

logger = logging.getLogger(__name__)


def get_username_domain_from_email(email: str):
    """Extract local part and domain from email."""
    try:
        address = Address(addr_spec=email)
        if len(address.username) > 64 or len(address.domain) > 255:
            # Simple length validation using the RFC 5321 limits
            return None, None
        return address.username, address.domain
    except (TypeError, ValueError, AttributeError, IndexError, HeaderParseError) as exc:
        logger.exception(exc)
        return None, None


class MailboxModelBackend(ModelBackend):
    """
    Custom authentication backend for OIDC provider, enforce the use of email as the username.

    Warning: This authentication backend is not suitable for general use, it is
    tailored for the OIDC provider and will only authenticate user and allow
    them to access the /o/authorize endpoint **only**.
    """

    def _get_cache_key(self, email):
        """Generate a cache key for tracking login attempts."""
        stringified_email = email.replace("@", "_at_").replace(".", "_dot_")
        return f"login_attempts_{slugify(stringified_email)}"

    def _increment_login_attempts(self, email):
        """Increment the number of failed login attempts."""
        cache_key = self._get_cache_key(email)
        attempts = cache.get(cache_key, 0) + 1
        cache.set(cache_key, attempts, settings.ACCOUNT_LOCKOUT_TIME)

    def _reset_login_attempts(self, email):
        """Reset the number of failed login attempts."""
        cache_key = self._get_cache_key(email)
        cache.delete(cache_key)

    def _is_login_attempts_exceeded(self, email) -> bool:
        """Check if the account is locked due to too many failed attempts."""
        cache_key = self._get_cache_key(email)
        attempts = cache.get(cache_key, 0)
        return attempts >= settings.MAX_LOGIN_ATTEMPTS

    def get_user(self, user_id):
        """Retrieve a user, here a mailbox, by its unique identifier."""
        try:
            mailbox = Mailbox.objects.get(pk=user_id)
        except Mailbox.DoesNotExist:
            return None

        if self.user_can_authenticate(mailbox):
            return mailbox

        return None

    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        """Authenticate a user based on email and password"""
        if username or email is None:  # ignore if username is provided
            return None

        # Disable this backend if the corresponding middleware is not defined.
        if (
            "mailbox_oauth2.middleware.one_time_email_authenticated_session"
            not in settings.MIDDLEWARE
        ):
            logger.error(
                "EmailModelBackend was triggered but the `one_time_email_authenticated_session` "
                "is not set: ignoring authentication."
            )
            return None

        # Check if the account is locked
        if self._is_login_attempts_exceeded(email):
            logger.warning("Account locked due to too many failed attempts: %s", email)
            # Run the default password hasher once to reduce the timing
            # difference between a locked account and valid one (django issue #20760)
            Mailbox().set_password(password)
            return None

        local_part, domain = get_username_domain_from_email(email)
        if local_part is None or domain is None:
            return None

        try:
            user = Mailbox.objects.select_related("domain").get(
                local_part__iexact=local_part, domain__name__iexact=domain
            )
        except Mailbox.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (django issue #20760).
            Mailbox().set_password(password)
        else:
            if not self.user_can_authenticate(user):
                # Run the default password hasher once to reduce the timing
                # difference between a user who can authenticate and another one.
                Mailbox().set_password(password)

            elif user.check_password(password):
                # Reset attempts on successful login
                self._reset_login_attempts(email)
                return user

            else:
                # Track failed attempt
                self._increment_login_attempts(email)

        return None

    def user_can_authenticate(self, user):
        """Verify the user can authenticate."""
        user_can_authenticate = super().user_can_authenticate(user)
        return user_can_authenticate and user.domain.is_identity_provider_ready()
