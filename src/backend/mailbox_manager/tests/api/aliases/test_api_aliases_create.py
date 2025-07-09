"""
Tests for mailbox Aliases API endpoint in People's app mailbox_manager.
Focus on "create" action.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from mailbox_manager import enums, factories, models
from mailbox_manager.api.client import serializers

pytestmark = pytest.mark.django_db

def test_api_aliases_create__anonymous():
    """Anonymous user should not create aliases"""
    mailbox = factories.MailboxFactory()
    
    response = APIClient().post(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/aliases/",
        {"whatever": "this should not be updated"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not models.Alias.objects.exists()


def test_api_aliases_create__no_access_forbidden():
    """User authenticated but having no access to domain should not create aliases."""
    mailbox = factories.MailboxFactory()

    client = APIClient()
    client.force_login(user)
    response = client.post(
        f"/api/v1.0/mail-domains/{mailbox.domain.slug}/aliases/",
        {"whatever": "this should not be updated"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not models.Alias.objects.exists()