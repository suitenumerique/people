"""App configuration for the token_exchange application."""

import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class TokenExchangeConfig(AppConfig):
    """Configuration for the token_exchange application."""

    name = "token_exchange"
    verbose_name = "Token Exchange (RFC 8693)"

    def ready(self):
        """Import tasks when app is ready."""
        # Import tasks to register periodic tasks
        try:
            import token_exchange.tasks  # noqa: PLC0415 # pylint: disable=unused-import, import-outside-toplevel
        except ImportError:
            logger.error("Failed to import tasks for token_exchange")
