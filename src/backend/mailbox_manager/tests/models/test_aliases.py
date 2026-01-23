"""
Unit tests for the Alias model
"""

import pytest

from mailbox_manager import factories, models

pytestmark = pytest.mark.django_db


def test_models_aliases__devnull_destination_ok():
    """Can create alias where destination is devnull@devnull."""

    models.Alias.objects.create(
        local_part="spam",
        domain=factories.MailDomainEnabledFactory(),
        destination="devnull@devnull",
    )
