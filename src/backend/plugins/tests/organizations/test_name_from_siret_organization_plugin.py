"""Tests for the NameFromSiretOrganizationPlugin plugin."""

import pytest
import responses

from core.models import Organization
from core.plugins.loader import get_organization_plugins

pytestmark = pytest.mark.django_db


# disable unused-argument for because organization_plugins_settings
# is used to set the settings not to be used in the test
# pylint: disable=unused-argument


@pytest.fixture(name="organization_plugins_settings")
def organization_plugins_settings_fixture(settings):
    """
    Fixture to set the organization plugins settings and
    leave the initial state after the test.
    """
    _original_plugins = settings.ORGANIZATION_PLUGINS

    settings.ORGANIZATION_PLUGINS = [
        "plugins.organizations.NameFromSiretOrganizationPlugin"
    ]

    # reset get_organization_plugins cache
    get_organization_plugins.cache_clear()
    get_organization_plugins()  # call to populate the cache

    yield

    # reset get_organization_plugins cache
    settings.ORGANIZATION_PLUGINS = _original_plugins
    get_organization_plugins.cache_clear()
    get_organization_plugins()  # call to populate the cache


@responses.activate
def test_organization_plugins_run_after_create(organization_plugins_settings):
    """Test the run_after_create method of the organization plugins for nominal case."""
    responses.add(
        responses.GET,
        "https://recherche-entreprises.api.gouv.fr/search?q=12345678901234",
        json={
            "results": [
                {
                    # skipping some fields
                    "matching_etablissements": [
                        # skipping some fields
                        {
                            "liste_enseignes": ["AMAZING ORGANIZATION"],
                            "siret": "12345678901234",
                        }
                    ]
                }
            ],
            "total_results": 1,
            "page": 1,
            "per_page": 10,
            "total_pages": 1,
        },
        status=200,
    )

    organization = Organization.objects.create(
        name="12345678901234", registration_id_list=["12345678901234"]
    )
    assert organization.name == "Amazing Organization"

    # Check that the organization has been updated in the database also
    organization.refresh_from_db()
    assert organization.name == "Amazing Organization"


@responses.activate
def test_organization_plugins_run_after_create_api_fail(organization_plugins_settings):
    """Test the plugin when the API call fails."""
    responses.add(
        responses.GET,
        "https://recherche-entreprises.api.gouv.fr/search?q=12345678901234",
        json={"error": "Internal Server Error"},
        status=500,
    )

    organization = Organization.objects.create(
        name="12345678901234", registration_id_list=["12345678901234"]
    )
    assert organization.name == "12345678901234"


@responses.activate
@pytest.mark.parametrize(
    "results",
    [
        {"results": []},
        {"results": [{"matching_etablissements": []}]},
        {"results": [{"matching_etablissements": [{"siret": "12345678901234"}]}]},
        {
            "results": [
                {
                    "matching_etablissements": [
                        {"siret": "12345678901234", "liste_enseignes": []}
                    ]
                }
            ]
        },
    ],
)
def test_organization_plugins_run_after_create_missing_data(
    organization_plugins_settings, results
):
    """Test the plugin when the API call returns missing data."""
    responses.add(
        responses.GET,
        "https://recherche-entreprises.api.gouv.fr/search?q=12345678901234",
        json=results,
        status=200,
    )

    organization = Organization.objects.create(
        name="12345678901234", registration_id_list=["12345678901234"]
    )
    assert organization.name == "12345678901234"


@responses.activate
def test_organization_plugins_run_after_create_name_already_set(
    organization_plugins_settings,
):
    """Test the plugin does nothing when the name already differs from the registration ID."""
    organization = Organization.objects.create(
        name="Magic WOW", registration_id_list=["12345678901234"]
    )
    assert organization.name == "Magic WOW"


@responses.activate
def test_organization_plugins_run_after_create_no_list_enseignes(
    organization_plugins_settings,
):
    """Test the run_after_create method of the organization plugins for nominal case."""
    responses.add(
        responses.GET,
        "https://recherche-entreprises.api.gouv.fr/search?q=12345678901234",
        json={
            "results": [
                {
                    "nom_raison_sociale": "AMAZING ORGANIZATION",
                    # skipping some fields
                    "matching_etablissements": [
                        # skipping some fields
                        {
                            "liste_enseignes": None,
                            "siret": "12345678901234",
                        }
                    ],
                }
            ],
            "total_results": 1,
            "page": 1,
            "per_page": 10,
            "total_pages": 1,
        },
        status=200,
    )

    organization = Organization.objects.create(
        name="12345678901234", registration_id_list=["12345678901234"]
    )
    assert organization.name == "Amazing Organization"

    # Check that the organization has been updated in the database also
    organization.refresh_from_db()
    assert organization.name == "Amazing Organization"
