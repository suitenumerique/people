"""Test for the La Suite plugin API active organizations siret"""

from django.test import override_settings

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core import factories

pytestmark = pytest.mark.django_db

API_URL = "/la-suite/v1.0/siret/"


# pylint: disable=unused-argument
def test_active_organizations_siret_unauthorized(plugin_urls):
    """Test the active organizations siret API unauthorized"""
    client = APIClient()
    response = client.get(API_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# pylint: disable=unused-argument
@override_settings(ACCOUNT_SERVICE_SCOPES=["la-suite-list-organizations-siret"])
def test_active_organizations_siret_authorized(plugin_urls):
    """Test the active organizations siret API authorized"""
    account_service = factories.AccountServiceFactory(
        name="my_account_service",
        api_key="my_api_key",
        scopes=["la-suite-list-organizations-siret"],
    )
    factories.OrganizationFactory(
        metadata={"is_public_service": True, "is_commune": True},
        registration_id_list=["11111111111111", "22222222222222"],
        is_active=True,
    )
    factories.OrganizationFactory(
        metadata={"is_public_service": True, "is_commune": False},
        registration_id_list=["33333333333333"],
        is_active=True,
    )
    factories.OrganizationFactory(
        metadata={"is_public_service": True, "is_commune": True},
        registration_id_list=["44444444444444"],
        is_active=False,
    )
    factories.OrganizationFactory(
        metadata={"is_public_service": True, "is_commune": False},
        registration_id_list=["55555555555555"],
        is_active=True,
    )
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"ApiKey {account_service.api_key}")

    response = client.get(API_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == ["11111111111111", "22222222222222"]
