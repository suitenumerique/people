"""
Project custom models for the OAuth2 provider.

We replace the former user model with a mailbox model.
"""

from django.db import models

from oauth2_provider.models import (
    AbstractAccessToken,
    AbstractGrant,
    AbstractIDToken,
    AbstractRefreshToken,
)


class Grant(AbstractGrant):
    """
    A Grant instance represents a token with a short lifetime that can
    be swapped for an access token, as described in :rfc:`4.1.2`

    Replaces the user with a mailbox instance.
    """

    user = models.ForeignKey(
        "mailbox_manager.Mailbox",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s",
    )


class IDToken(AbstractIDToken):
    """
    An IDToken instance represents the actual token to
    access user's resources, as in :openid:`2`.

    Replaces the user with a mailbox instance.
    """

    user = models.ForeignKey(
        "mailbox_manager.Mailbox",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s",
    )


class AccessToken(AbstractAccessToken):
    """
    An AccessToken instance represents the actual access token to
    access user's resources, as in :rfc:`5`.

    Replaces the user with a mailbox instance.
    """

    user = models.ForeignKey(
        "mailbox_manager.Mailbox",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s",
    )


class RefreshToken(AbstractRefreshToken):
    """
    A RefreshToken instance represents a token that can be swapped for a new
    access token when it expires.

    Replaces the user with a mailbox instance.
    """

    user = models.ForeignKey(
        "mailbox_manager.Mailbox",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s",
    )
