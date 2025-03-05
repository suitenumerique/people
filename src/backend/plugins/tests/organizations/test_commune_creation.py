"""Tests for the CommuneCreation plugin."""

from django.conf import settings
from django.test.utils import override_settings

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


@override_settings(DNS_PROVISIONING_TARGET_ZONE="collectivite.fr")
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


@override_settings(DNS_PROVISIONING_TARGET_ZONE="collectivite.fr")
def test_tasks_on_commune_creation_include_dimail_domain_creation():
    """Test the second task in commune creation: creating the domain in Dimail"""
    plugin = CommuneCreation()
    name = "Merlaut"

    tasks = plugin.complete_commune_creation(name)

    assert tasks[1].base == settings.MAIL_PROVISIONING_API_URL
    assert tasks[1].url == "/domains/"
    assert tasks[1].method == "POST"
    assert tasks[1].params == {
        "name": "merlaut.collectivite.fr",
        "delivery": "virtual",
        "features": ["webmail", "mailbox"],
        "context_name": "merlaut.collectivite.fr",
    }
    assert (
        tasks[1].headers["Authorization"]
        == f"Basic {settings.MAIL_PROVISIONING_API_CREDENTIALS}"
    )


@override_settings(DNS_PROVISIONING_TARGET_ZONE="collectivite.fr")
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
        == f"Basic {settings.MAIL_PROVISIONING_API_CREDENTIALS}"
    )


@override_settings(DNS_PROVISIONING_TARGET_ZONE="collectivite.fr")
def test_tasks_on_commune_creation_include_dns_records():
    """Test the next several tasks in commune creation: creating records"""
    plugin = CommuneCreation()
    name = "Abidos"

    spec_response = [
        {"target": "", "type": "mx", "value": "mx.dev.ox.numerique.gouv.fr."},
        {
            "target": "dimail._domainkey",
            "type": "txt",
            "value": "v=DKIM1; h=sha256; k=rsa; p=MIICIjANB<truncated>AAQ==",
        },
        {"target": "imap", "type": "cname", "value": "imap.dev.ox.numerique.gouv.fr."},
        {"target": "smtp", "type": "cname", "value": "smtp.dev.ox.numerique.gouv.fr."},
        {
            "target": "",
            "type": "txt",
            "value": "v=spf1 include:_spf.dev.ox.numerique.gouv.fr -all",
        },
        {
            "target": "webmail",
            "type": "cname",
            "value": "webmail.dev.ox.numerique.gouv.fr.",
        },
    ]

    tasks = plugin.complete_commune_creation(name)
    tasks[2].response_data = spec_response

    expected = {
        "changes": [
            {
                "add": {
                    "records": [
                        {
                            "name": item["target"],
                            "type": item["type"].upper(),
                            "data": item["value"],
                            "ttl": 3600,
                        }
                        for item in spec_response
                    ]
                }
            }
        ]
    }

    zone_call = plugin.complete_zone_creation(tasks[2])
    assert zone_call.params == expected
    assert zone_call.url == "/domain/v2beta1/dns-zones/abidos.collectivite.fr/records"
    assert (
        zone_call.headers["X-Auth-Token"] == settings.DNS_PROVISIONING_API_CREDENTIALS
    )


@override_settings(DNS_PROVISIONING_TARGET_ZONE="collectivite.fr")
def test_tasks_on_grant_access():
    """Test the final tasks after making user admin of an org"""
    plugin = CommuneCreation()

    tasks = plugin.complete_grant_access("some-sub", "mezos.collectivite.fr")

    assert tasks[0].base == settings.MAIL_PROVISIONING_API_URL
    assert tasks[0].url == "/users/"
    assert tasks[0].method == "POST"
    assert tasks[0].params == {
        "name": "some-sub",
        "password": "no",
        "is_admin": False,
        "perms": [],
    }
    assert (
        tasks[0].headers["Authorization"]
        == f"Basic {settings.MAIL_PROVISIONING_API_CREDENTIALS}"
    )

    assert tasks[1].base == settings.MAIL_PROVISIONING_API_URL
    assert tasks[1].url == "/allows/"
    assert tasks[1].method == "POST"
    assert tasks[1].params == {
        "user": "some-sub",
        "domain": "mezos.collectivite.fr",
    }
    assert (
        tasks[1].headers["Authorization"]
        == f"Basic {settings.MAIL_PROVISIONING_API_CREDENTIALS}"
    )


def test_normalize_name():
    """Test name normalization"""
    plugin = CommuneCreation()
    assert plugin.normalize_name("Asnières-sur-Saône") == "asnieres-sur-saone"
    assert plugin.normalize_name("Bâgé-le-Châtel") == "bage-le-chatel"
    assert plugin.normalize_name("Courçais") == "courcais"
    assert plugin.normalize_name("Moÿ-de-l'Aisne") == "moy-de-l-aisne"
    assert plugin.normalize_name("Salouël") == "salouel"
    assert (
        plugin.normalize_name("Bors (Canton de Tude-et-Lavalette)")
        == "bors-canton-de-tude-et-lavalette"
    )


@override_settings(DNS_PROVISIONING_TARGET_ZONE="collectivite.fr")
def test_zone_name():
    """Test transforming a commune name to a sub-zone of collectivite.fr"""
    plugin = CommuneCreation()
    assert plugin.zone_name("Bâgé-le-Châtel") == "bage-le-chatel.collectivite.fr"
