"""
Test users API endpoints in the People core app.
"""

import pytest
from rest_framework.status import (
    HTTP_200_OK,
)
from rest_framework.test import APIClient

from core import factories

pytestmark = pytest.mark.django_db


def test_api_config_anonymous():
    """Anonymous users should be allowed to get the configuration."""
    client = APIClient()
    response = client.get("/api/v1.0/config/")
    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "CRISP_WEBSITE_ID": None,
        "LANGUAGES": [["en-us", "English"], ["fr-fr", "French"]],
        "COMMIT": "NA",
        "FEATURES": {
            "CONTACTS_DISPLAY": True,
            "CONTACTS_CREATE": True,
            "MAILBOXES_CREATE": True,
            "TEAMS_DISPLAY": True,
            "TEAMS_CREATE": True,
        },
        "RELEASE": "NA",
    }


def test_api_config_authenticated():
    """Authenticated users should be allowed to get the configuration."""
    user = factories.UserFactory()

    client = APIClient()
    client.force_login(user)

    response = client.get("/api/v1.0/config/")
    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "CRISP_WEBSITE_ID": None,
        "LANGUAGES": [["en-us", "English"], ["fr-fr", "French"]],
        "COMMIT": "NA",
        "FEATURES": {
            "CONTACTS_DISPLAY": True,
            "CONTACTS_CREATE": True,
            "MAILBOXES_CREATE": True,
            "TEAMS_DISPLAY": True,
            "TEAMS_CREATE": True,
        },
        "RELEASE": "NA",
    }
