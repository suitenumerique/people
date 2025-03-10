"""
Management command for filling organization metadata with default values.
"""

from django.core.management.base import BaseCommand

from core import models
from core.utils.json_schema import generate_default_from_schema


class Command(BaseCommand):
    """Management command to fill organization metadata with default values."""

    help = "Fill organization metadata with default values"

    def handle(self, *args, **options):
        """Fill organizations metadata missing values with default values."""
        organization_metadata_schema = models.get_organization_metadata_schema()

        if not organization_metadata_schema:
            message = "No organization metadata schema defined."
            self.stdout.write(self.style.ERROR(message))
            return

        default_metadata = generate_default_from_schema(organization_metadata_schema)
        for organization in models.Organization.objects.all():
            organization.metadata = {**default_metadata, **organization.metadata}

            # Save the organization with the updated metadata
            # We don't use bulk update because we want to trigger the clean method
            organization.save(update_fields=["metadata", "updated_at"])

        message = "Organization metadata filled with default values."
        self.stdout.write(self.style.SUCCESS(message))
