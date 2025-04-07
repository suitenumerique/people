"""Models for the la suite plugin."""

import secrets

from django.db import models

from core.models import Organization


class OneTimeToken(models.Model):
    """
    An abstract model for a one-time token.
    """

    key = models.CharField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    used_at = models.DateTimeField(null=True, blank=True)
    enabled = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Override the save method to generate a key if it is not set.
        """
        if not self.key:
            self.key = secrets.token_urlsafe(16)
        return super().save(*args, **kwargs)


class OrganizationOneTimeToken(OneTimeToken):
    """
    A one-time token for an organization.
    """

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="one_time_tokens",
    )

    class Meta:
        db_table = "people_organization_one_time_token"
        verbose_name = "Organization One Time Token"
        verbose_name_plural = "Organization One Time Tokens"

    def __str__(self):
        """
        Return the string representation of the one-time token.
        """
        return f"One time token for {self.organization.name}"
