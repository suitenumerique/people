from django.db import models

from core.models import Organization


class OneTimeToken(models.Model):
    key = models.CharField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    used_at = models.DateTimeField(null=True, blank=True)
    enabled = models.BooleanField(default=True)

    class Meta:
        abstract = True


class OrganizationOneTimeToken(OneTimeToken):

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="one_time_tokens",
    )

    class Meta:
        db_table = "people_organization_one_time_token"
        verbose_name = "Organization One Time Token"
        verbose_name_plural = "Organization One Time Tokens"
