"""Tests for the NameFromSiretOrganizationPlugin plugin."""

import pytest
import responses

from core.models import Organization, get_organization_metadata_schema
from core.plugins.registry import registry

from plugins.la_suite.hooks_utils.all_organizations import (
    get_organization_name_and_metadata_from_siret,
)

pytestmark = pytest.mark.django_db


# disable unused-argument for because organization_plugins_settings
# is used to set the settings not to be used in the test
# pylint: disable=unused-argument


@pytest.fixture(name="hook_settings")
def hook_settings_fixture(settings):
    """
    Fixture to set the organization plugins settings and
    leave the initial state after the test.
    """
    _original_hooks = dict(registry._hooks.items())  # pylint: disable=protected-access
    registry.register_hook(
        "organization_created", get_organization_name_and_metadata_from_siret
    )

    settings.ORGANIZATION_METADATA_SCHEMA = "fr/organization_metadata.json"

    # Reset the model validation cache
    get_organization_metadata_schema.cache_clear()
    get_organization_metadata_schema()

    yield

    # reset the hooks
    registry._hooks = _original_hooks  # pylint: disable=protected-access

    settings.ORGANIZATION_METADATA_SCHEMA = None

    # Reset the model validation cache
    get_organization_metadata_schema.cache_clear()
    get_organization_metadata_schema()


@responses.activate
@pytest.mark.parametrize(
    "nature_juridique,is_commune,is_public_service",
    [
        ("123", False, False),
        ("7210", True, False),
        ("123", False, True),
        ("7210", True, True),
    ],
)
def test_organization_plugins_run_after_create(
    hook_settings, nature_juridique, is_commune, is_public_service
):
    """Test the run_after_create method of the organization plugins for nominal case."""
    responses.get(
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
                    ],
                    "nature_juridique": nature_juridique,
                    "complements": {
                        "est_service_public": is_public_service,
                    },
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
    assert organization.metadata["is_commune"] == is_commune
    assert organization.metadata["is_public_service"] == is_public_service

    # Check that the organization has been updated in the database also
    organization.refresh_from_db()
    assert organization.name == "Amazing Organization"
    assert organization.metadata["is_commune"] == is_commune
    assert organization.metadata["is_public_service"] == is_public_service


@responses.activate
def test_organization_plugins_run_after_create_api_fail(hook_settings):
    """Test the plugin when the API call fails."""
    responses.get(
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
def test_organization_plugins_run_after_create_missing_data(hook_settings, results):
    """Test the plugin when the API call returns missing data."""
    responses.get(
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
    hook_settings,
):
    """Test the plugin does nothing when the name already differs from the registration ID."""
    organization = Organization.objects.create(
        name="Magic WOW", registration_id_list=["12345678901234"]
    )
    assert organization.name == "Magic WOW"


@responses.activate
def test_organization_plugins_run_after_create_no_list_enseignes(
    hook_settings,
):
    """Test the run_after_create method of the organization plugins for nominal case."""
    responses.get(
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
                    "nature_juridique": "123",
                    "complements": {
                        "est_service_public": True,
                    },
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
    assert organization.metadata["is_commune"] is False
    assert organization.metadata["is_public_service"] is True

    # Check that the organization has been updated in the database also
    organization.refresh_from_db()
    assert organization.name == "Amazing Organization"
    assert organization.metadata["is_commune"] is False
    assert organization.metadata["is_public_service"] is True
