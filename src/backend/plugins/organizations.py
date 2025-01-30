"""Organization related plugins."""

import logging

import requests
from requests.adapters import HTTPAdapter, Retry

from core.plugins.base import BaseOrganizationPlugin

logger = logging.getLogger(__name__)


class NameFromSiretOrganizationPlugin(BaseOrganizationPlugin):
    """
    This plugin is used to convert the organization registration ID
    to the proper name. For French organization the registration ID
    is the SIRET.

    This is a very specific plugin for French organizations and this
    first implementation is very basic. It surely needs to be improved
    later.
    """

    _api_url = "https://recherche-entreprises.api.gouv.fr/search?q={siret}"

    @staticmethod
    def get_organization_name_from_results(data, siret):
        """Return the organization name from the results of a SIRET search."""
        for result in data["results"]:
            is_commune = (
                result.get("nature_juridique") == "7210"
            )  # INSEE code for commune
            for organization in result["matching_etablissements"]:
                if organization.get("siret") == siret:
                    if is_commune:
                        return organization["libelle_commune"].title()

                    store_signs = organization.get("liste_enseignes") or []
                    if store_signs:
                        return store_signs[0].title()
                    if name := result.get("nom_raison_sociale"):
                        return name.title()

        logger.warning("No organization name found for SIRET %s", siret)
        return None

    def run_after_create(self, organization):
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
            response = s.get(self._api_url.format(siret=siret), timeout=10)
            response.raise_for_status()
            data = response.json()
            name = self.get_organization_name_from_results(data, siret)
            if not name:
                return
        except requests.RequestException as exc:
            logger.exception("%s: Unable to fetch organization name from SIRET", exc)
            return

        organization.name = name
        organization.save(update_fields=["name", "updated_at"])
        logger.info("Organization %s name updated to %s", organization, name)
