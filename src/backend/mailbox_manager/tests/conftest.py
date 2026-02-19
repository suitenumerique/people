"""
Fixtures for mailbox manager tests
"""

import re

import pytest
import responses
from rest_framework import status

from mailbox_manager import factories


## DIMAIL RESPONSES
@pytest.fixture(name="dimail_token_ok")
def fixture_dimail_token_ok():
    """Mock dimail response when /token/ endpoit is given valid credentials."""
    responses.get(
        re.compile(r".*/token/"),
        json={"access_token": "token", "token_type": "bearer"},
        status=status.HTTP_200_OK,
        content_type="application/json",
    )


@pytest.fixture(name="mailbox_data")
def fixture_mailbox_data():
    """Provides valid mailbox data for tests."""
    example = factories.MailboxFactory.build()
    return {
        "first_name": example.first_name,
        "last_name": example.last_name,
        "local_part": example.local_part,
        "secondary_email": example.secondary_email,
    }
