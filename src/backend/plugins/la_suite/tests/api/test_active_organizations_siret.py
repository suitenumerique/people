"""Test for the La Suite plugin API active organizations siret"""

from importlib import import_module, reload

from django.conf import settings
from django.test.utils import override_settings

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories

pytestmark = pytest.mark.django_db

API_URL = "/la-suite/v1.0/siret/"


@override_settings(INSTALLED_PLUGINS=["plugins.la_suite.apps.LaSuitePluginConfig"])
def test_active_organizations_siret_unauthorized():
    """Test the active organizations siret API unauthorized"""
    reload(import_module(settings.ROOT_URLCONF))
    client = APIClient()
    response = client.get(API_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@override_settings(INSTALLED_PLUGINS=["plugins.la_suite.apps.LaSuitePluginConfig"])
def test_active_organizations_siret_authorized():
    """Test the active organizations siret API authorized"""
    reload(import_module(settings.ROOT_URLCONF))
    account_service = factories.AccountServiceFactory(
        name="my_account_service",
        api_key="my_api_key",
        scopes=["la-suite-list-organizations-siret"],
    )
    factories.OrganizationFactory(
        metadata={"is_public_service": True, "is_commune": True},
        registration_id_list=["12345678901234"],
        is_active=True,
    )
    factories.OrganizationFactory(
        metadata={"is_public_service": True, "is_commune": False},
        registration_id_list=["23456789012345"],
        is_active=True,
    )
    factories.OrganizationFactory(
        metadata={"is_public_service": True, "is_commune": True},
        registration_id_list=["34567890123456"],
        is_active=False,
    )
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"ApiKey {account_service.api_key}")
    response = client.get(API_URL)
    assert response.status_code == status.HTTP_200_OK

    # Check pagination structure
    assert "count" in response.data
    assert "results" in response.data
    assert "next" in response.data
    assert "previous" in response.data

    # Check the actual results
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1
    assert response.data["results"] == ["12345678901234"]
