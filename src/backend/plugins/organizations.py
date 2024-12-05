"""Organization related plugins."""

import logging

import requests

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
    def _extract_name_from_organization_data(organization_data):
        """Extract the name from the organization data."""
        try:
            return organization_data["liste_enseignes"][0].title()
        except KeyError:
            logger.warning("Missing key 'liste_enseignes' in %s", organization_data)
        except IndexError:
            logger.warning("Empty list 'liste_enseignes' in %s", organization_data)
        return None

    def _get_organization_name_from_siret(self, siret):
        """Return the organization name from the SIRET."""
        try:
            response = requests.get(self._api_url.format(siret=siret), timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            logger.exception("%s: Unable to fetch organization name from SIRET", exc)
            return None

        for result in data["results"]:
            for organization in result["matching_etablissements"]:
                if organization.get("siret") == siret:
                    return self._extract_name_from_organization_data(organization)

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
        name = self._get_organization_name_from_siret(
            organization.registration_id_list[0]
        )
        if not name:
            return

        organization.name = name
        organization.save(update_fields=["name", "updated_at"])
        logger.info("Organization %s name updated to %s", organization, name)
