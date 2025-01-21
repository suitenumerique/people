"""Organization related plugins."""

from django.conf import settings

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
            for organization in result["matching_etablissements"]:
                if organization.get("siret") == siret:
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

class ApiCall:
    """Encapsulates a call to an external API"""

    method: str = "GET"
    base: str = ""
    url: str = ""
    params: dict = {}
    headers: dict = {}
    response = None

    def execute(self):
        """Call the specified API endpoint with supplied parameters and record response"""
        if self.method == "POST":
            self.response = requests.request(
                method=self.method,
                url=f"{self.base}/{self.url}",
                json=self.params,
                headers=self.headers,
                timeout=5,
            )


class CommuneCreation(BaseOrganizationPlugin):
    """
    This plugin handles setup tasks for French communes.
    """

    _api_url = "https://recherche-entreprises.api.gouv.fr/search?q={siret}"

    def get_organization_name_from_results(self, data, siret):
        """Return the organization name from the results of a SIRET search."""
        for result in data["results"]:
            nature = "nature_juridique"
            commune = nature in result and result[nature] == "7210"
            for organization in result["matching_etablissements"]:
                if organization.get("siret") == siret:
                    if commune:
                        return organization["libelle_commune"].title()

        logger.warning("No organization name found for SIRET %s", siret)
        return None

    def complete_commune_creation(self, name: str) -> ApiCall:
        """Specify the tasks to be completed after a commune is created."""
        inputs = {"name": name.lower()}

        create_zone = ApiCall()
        create_zone.method = "POST"
        create_zone.base = "https://api.scaleway.com"
        create_zone.url = "/domain/v2beta1/dns-zones"
        create_zone.params = {
            "project_id": settings.DNS_PROVISIONING_RESOURCE_ID,
            "domain": "collectivite.fr",
            "subdomain": inputs["name"],
        }
        create_zone.headers = {
            "X-Auth-Token": settings.DNS_PROVISIONING_API_CREDENTIALS
        }

        create_domain = ApiCall()
        create_domain.method = "POST"
        create_domain.base = settings.MAIL_PROVISIONING_API_URL
        create_domain.url = "/domains"
        create_domain.params = {
            "name": inputs["name"],
            "delivery": "virtual",
            "features": ["webmail","mailbox"],
            "context_name": inputs["name"],
        }
        create_domain.headers = {
            "Authorization": f"Basic: {settings.MAIL_PROVISIONING_API_CREDENTIALS}"
        }

        spec_domain = ApiCall()
        spec_domain.base = settings.MAIL_PROVISIONING_API_URL
        spec_domain.url = f"/domains/{inputs["name"]}.collectivite.fr/spec"
        spec_domain.headers = {
            "Authorization": f"Basic: {settings.MAIL_PROVISIONING_API_CREDENTIALS}"
        }

        return [create_zone, create_domain, spec_domain]

    def run_after_create(self, organization):
        """After creating an organization, update the organization name."""
        if not organization.registration_id_list:
            # No registration ID to convert...
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
