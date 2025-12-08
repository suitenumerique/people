"""Management command to clean up expired exchanged tokens."""

import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from token_exchange.models import ExchangedToken

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Management command to clean up expired exchanged tokens."""

    help = "Clean up expired exchanged tokens"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--days",
            type=int,
            default=7,
            help="Delete tokens expired for more than N days (default: 7)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate the cleanup without actually deleting tokens",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        days = options["days"]
        dry_run = options["dry_run"]

        # Calculate the threshold date
        threshold = timezone.now() - timedelta(days=days)

        # Find expired tokens older than the threshold
        expired_tokens = ExchangedToken.objects.filter(expires_at__lt=threshold)
        count = expired_tokens.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(f"No expired tokens found older than {days} days")
            )
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"[DRY RUN] Would delete {count} expired token(s) older than {days} days"
                )
            )
            logger.info(
                "[DRY RUN] Would clean up %d expired tokens older than %d days",
                count,
                days,
            )
        else:
            # Delete the tokens
            expired_tokens.delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully deleted {count} expired token(s) older than {days} days"
                )
            )
            logger.info(
                "Cleaned up %d expired tokens older than %d days",
                count,
                days,
            )
