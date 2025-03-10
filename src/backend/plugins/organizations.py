"""Organization related plugins."""

import logging
import re

from django.conf import settings
from django.utils.text import slugify

import requests
from requests.adapters import HTTPAdapter, Retry

from core.plugins.base import BaseOrganizationPlugin

from mailbox_manager.enums import MailDomainRoleChoices
from mailbox_manager.models import MailDomain, MailDomainAccess

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
    def get_organization_name_and_metadata_from_results(data, siret):
        """Return the organization name and metadata from the results of a SIRET search."""
        org_metadata = {}
        for result in data["results"]:
            for organization in result["matching_etablissements"]:
                if organization.get("siret") == siret:
                    org_metadata["is_public_service"] = result.get(
                        "complements", {}
                    ).get("est_service_public", False)
                    org_metadata["is_commune"] = (
                        str(result.get("nature_juridique", "")) == "7210"
                    )

                    store_signs = organization.get("liste_enseignes") or []
                    if store_signs:
                        return store_signs[0].title(), org_metadata
                    if name := result.get("nom_raison_sociale"):
                        return name.title(), org_metadata

        logger.warning("No organization name found for SIRET %s", siret)
        return None, org_metadata

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
        except requests.RequestException as exc:
            logger.exception("%s: Unable to fetch organization name from SIRET", exc)
            return

        name, metadata = self.get_organization_name_and_metadata_from_results(
            data, siret
        )
        if not name:  # don't consider metadata either
            return

        organization.name = name
        organization.metadata = (organization.metadata or {}) | metadata

        organization.save(update_fields=["name", "metadata", "updated_at"])
        logger.info("Organization %s name updated to %s", organization, name)

    def run_after_grant_access(self, organization_access):
        """After granting an organization access, we don't need to do anything."""


class ApiCall:
    """Encapsulates a call to an external API"""

    inputs: dict = {}
    method: str = "GET"
    base: str = ""
    url: str = ""
    params: dict = {}
    headers: dict = {}
    response_data = None

    def execute(self):
        """Call the specified API endpoint with supplied parameters and record response"""
        if self.method in ("POST", "PATCH"):
            response = requests.request(
                method=self.method,
                url=f"{self.base}/{self.url}",
                json=self.params,
                headers=self.headers,
                timeout=20,
            )
        else:
            response = requests.request(
                method=self.method,
                url=f"{self.base}/{self.url}",
                params=self.params,
                headers=self.headers,
                timeout=20,
            )
        self.response_data = response.json()
        logger.info(
            "API call: %s %s %s %s",
            self.method,
            self.url,
            self.params,
            self.response_data,
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
            if commune:
                return result["siege"]["libelle_commune"].title()

        logger.warning("Not a commune: SIRET %s", siret)
        return None

    def dns_call(self, spec):
        """Call to add a DNS record"""
        zone_name = self.zone_name(spec.inputs["name"])

        records = [
            {
                "name": item["target"],
                "type": item["type"].upper(),
                "data": item["value"],
                "ttl": 3600,
            }
            for item in spec.response_data
        ]
        result = ApiCall()
        result.method = "PATCH"
        result.base = "https://api.scaleway.com"
        result.url = f"/domain/v2beta1/dns-zones/{zone_name}/records"
        result.params = {"changes": [{"add": {"records": records}}]}
        result.headers = {"X-Auth-Token": settings.DNS_PROVISIONING_API_CREDENTIALS}
        return result

    def normalize_name(self, name: str) -> str:
        """Map the name to a standard form"""
        name = re.sub("'", "-", name)
        return slugify(name)

    def zone_name(self, name: str) -> str:
        """Derive the zone name from the commune name"""
        normalized = self.normalize_name(name)
        return f"{normalized}.collectivite.fr"

    def complete_commune_creation(self, name: str) -> ApiCall:
        """Specify the tasks to be completed after a commune is created."""
        inputs = {"name": self.normalize_name(name)}

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

        zone_name = self.zone_name(inputs["name"])

        create_domain = ApiCall()
        create_domain.method = "POST"
        create_domain.base = settings.MAIL_PROVISIONING_API_URL
        create_domain.url = "/domains/"
        create_domain.params = {
            "name": zone_name,
            "delivery": "virtual",
            "features": ["webmail", "mailbox"],
            "context_name": zone_name,
        }
        create_domain.headers = {
            "Authorization": f"Basic {settings.MAIL_PROVISIONING_API_CREDENTIALS}"
        }

        spec_domain = ApiCall()
        spec_domain.inputs = inputs
        spec_domain.base = settings.MAIL_PROVISIONING_API_URL
        spec_domain.url = f"/domains/{zone_name}/spec"
        spec_domain.headers = {
            "Authorization": f"Basic {settings.MAIL_PROVISIONING_API_CREDENTIALS}"
        }

        return [create_zone, create_domain, spec_domain]

    def complete_zone_creation(self, spec_call):
        """Specify the tasks to be performed to set up the zone."""
        return self.dns_call(spec_call)

    def run_after_create(self, organization):
        """After creating an organization, update the organization name."""
        logger.info("In CommuneCreation")
        if not organization.registration_id_list:
            # No registration ID to convert...
            return

        # In the nominal case, there is only one registration ID because
        # the organization has been created from it.
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
            # Not a commune ?
            if not name:
                return
        except requests.RequestException as exc:
            logger.exception("%s: Unable to fetch organization name from SIRET", exc)
            return

        organization.name = name
        organization.save(update_fields=["name", "updated_at"])
        logger.info("Organization %s name updated to %s", organization, name)

        zone_name = self.zone_name(name)
        support = "support-regie@numerique.gouv.fr"
        MailDomain.objects.get_or_create(name=zone_name, support_email=support)

        # Compute and execute the rest of the process
        tasks = self.complete_commune_creation(name)
        for task in tasks:
            task.execute()
        last_task = self.complete_zone_creation(tasks[-1])
        last_task.execute()

    def complete_grant_access(self, sub, zone_name):
        """Specify the tasks to be completed after making a user admin"""
        create_user = ApiCall()
        create_user.method = "POST"
        create_user.base = settings.MAIL_PROVISIONING_API_URL
        create_user.url = "/users/"
        create_user.params = {
            "name": sub,
            "password": "no",
            "is_admin": False,
            "perms": [],
        }
        create_user.headers = {
            "Authorization": f"Basic {settings.MAIL_PROVISIONING_API_CREDENTIALS}"
        }

        grant_access = ApiCall()
        grant_access.method = "POST"
        grant_access.base = settings.MAIL_PROVISIONING_API_URL
        grant_access.url = "/allows/"
        grant_access.params = {
            "user": sub,
            "domain": zone_name,
        }
        grant_access.headers = {
            "Authorization": f"Basic {settings.MAIL_PROVISIONING_API_CREDENTIALS}"
        }

        return [create_user, grant_access]

    def run_after_grant_access(self, organization_access):
        """After granting an organization access, check for needed domain access grant."""
        orga = organization_access.organization
        user = organization_access.user
        zone_name = self.zone_name(orga.name)

        try:
            domain = MailDomain.objects.get(name=zone_name)
        except MailDomain.DoesNotExist:
            domain = None

        if domain:
            MailDomainAccess.objects.create(
                domain=domain, user=user, role=MailDomainRoleChoices.OWNER
            )

            tasks = self.complete_grant_access(user.sub, zone_name)
            for task in tasks:
                task.execute()
