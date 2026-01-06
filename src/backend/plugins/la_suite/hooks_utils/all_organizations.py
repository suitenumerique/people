"""
This hook is used to convert the organization registration ID
to the proper name. For French organization the registration ID
is the SIRET.

This is a very specific plugin for French organizations and this
first implementation is very basic. It surely needs to be improved
later.
"""

import logging

import requests
from requests.adapters import HTTPAdapter, Retry

logger = logging.getLogger(__name__)


API_URL = "https://recherche-entreprises.api.gouv.fr/search?q={siret}"


def _get_organization_name_and_metadata_from_results(data, siret):
    """Return the organization name and metadata from the results of a SIRET search."""
    # Find matching organization
    match = next(
        (
            (res, org)
            for res in data.get("results", [])
            for org in res.get("matching_etablissements", [])
            if org.get("siret") == siret
        ),
        None,
    )

    if not match:
        logger.warning("No organization name found for SIRET %s", siret)
        return None, {}

    result, organization = match

    # Extract metadata
    is_commune = str(result.get("nature_juridique", "")) == "7210"
    metadata = {
        "is_public_service": result.get("complements", {}).get(
            "est_service_public", False
        ),
        "is_commune": is_commune,
    }

    # Extract name (priority: commune name > store signs > business name)
    name = None
    if is_commune:
        name = result.get("siege", {}).get("libelle_commune")
    if not name:  # Fallback for non-communes OR if commune has no libelle_commune
        store_signs = organization.get("liste_enseignes") or []
        name = store_signs[0] if store_signs else result.get("nom_raison_sociale")

    if name:
        return name.title(), metadata

    logger.warning("No organization name found for SIRET %s", siret)
    return None, metadata


def get_organization_name_and_metadata_from_siret(organization):
    """After creating an organization, update the organization name."""
    if not organization.registration_id_list:
        # No registration ID to convert...
        return

    if organization.name not in organization.registration_id_list:
        # The name has probably already been customized
        return

    # In the nominal case, there is only one registration ID because
    # the organization as been created from it.
    try:
        # Retry logic as the API may be rate limited
        s = requests.Session()
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[429])
        s.mount("https://", HTTPAdapter(max_retries=retries))

        siret = organization.registration_id_list[0]
        response = s.get(API_URL.format(siret=siret), timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        logger.exception("%s: Unable to fetch organization name from SIRET", exc)
        return

    name, metadata = _get_organization_name_and_metadata_from_results(data, siret)
    if not name:  # don't consider metadata either
        return

    organization.name = name
    organization.metadata = (organization.metadata or {}) | metadata

    organization.save(update_fields=["name", "metadata", "updated_at"])
    logger.info("Organization %s name updated to %s", organization, name)
