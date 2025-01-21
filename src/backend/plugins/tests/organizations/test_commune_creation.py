"""Tests for the CommuneCreation plugin."""

from django.conf import settings

import pytest
import responses

from plugins.organizations import ApiCall, CommuneCreation

pytestmark = pytest.mark.django_db

def test_extract_name_from_org_data_when_commune():
    """Test the name is extracted correctly for a French commune."""
    data = {
        "results": [
            {
                "nom_complet": "COMMUNE DE VARZY",
                "nom_raison_sociale": "COMMUNE DE VARZY",
                "siege": {
                    "libelle_commune": "VARZY",
                    "liste_enseignes": ["MAIRIE"],
                    "siret": "21580304000017",
                },
                "nature_juridique": "7210",
                "matching_etablissements": [
                    {
                        "siret": "21580304000017",
                        "libelle_commune": "VARZY",
                        "liste_enseignes": ["MAIRIE"],
                    }
                ],
            }
        ]
    }

    plugin = CommuneCreation()
    name = plugin.get_organization_name_from_results(data, "21580304000017")
    assert name == "Varzy"


def test_api_call_execution():
    """Test that calling execute() faithfully executes the API call"""
    task = ApiCall()
    task.method = "POST"
    task.base = "https://some_host"
    task.url = "some_url"
    task.params = {"some_key": "some_value"}
    task.headers = {"Some-Header": "Some-Header-Value"}

    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.POST,
            url="https://some_host/some_url",
            body='{"some_key": "some_value"}',
            content_type="application/json",
            headers={"Some-Header": "Some-Header-Value"},
        )

        task.execute()


def test_tasks_on_commune_creation_include_zone_creation():
    """Test the first task in commune creation: creating the DNS sub-zone"""
    plugin = CommuneCreation()
    name = "Varzy"

    tasks = plugin.complete_commune_creation(name)

    assert tasks[0].base == "https://api.scaleway.com"
    assert tasks[0].url == "/domain/v2beta1/dns-zones"
    assert tasks[0].method == "POST"
    assert tasks[0].params == {
        "project_id": settings.DNS_PROVISIONING_RESOURCE_ID,
        "domain": "collectivite.fr",
        "subdomain": "varzy",
    }
    assert tasks[0].headers["X-Auth-Token"] == settings.DNS_PROVISIONING_API_CREDENTIALS


def test_tasks_on_commune_creation_include_dimail_domain_creation():
    """Test the second task in commune creation: creating the domain in Dimail"""
    plugin = CommuneCreation()
    name = "Merlaut"

    tasks = plugin.complete_commune_creation(name)

    assert tasks[1].base == settings.MAIL_PROVISIONING_API_URL
    assert tasks[1].url == "/domains"
    assert tasks[1].method == "POST"
    assert tasks[1].params == {
        "name": "merlaut",
        "delivery": "virtual",
        "features": ["webmail", "mailbox"],
        "context_name": "merlaut",
    }
    assert (
        tasks[1].headers["Authorization"]
        == f"Basic: {settings.MAIL_PROVISIONING_API_CREDENTIALS}"
    )

def test_tasks_on_commune_creation_include_fetching_spec():
    """Test the third task in commune creation: asking Dimail for the spec"""
    plugin = CommuneCreation()
    name = "Loc-Eguiner"

    tasks = plugin.complete_commune_creation(name)

    assert tasks[2].base == settings.MAIL_PROVISIONING_API_URL
    assert tasks[2].url == "/domains/loc-eguiner.collectivite.fr/spec"
    assert tasks[2].method == "GET"
    assert (
        tasks[2].headers["Authorization"]
        == f"Basic: {settings.MAIL_PROVISIONING_API_CREDENTIALS}"
    )
