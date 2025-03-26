"""
Hooks registration for the la_suite plugin.

This module is automagically loaded by the plugin system.
Putting hooks registration here allows to test the "utils"
function without registering the hook unwillingly.
"""

from core.plugins.registry import register_hook

from plugins.la_suite.hooks_utils.all_organizations import (
    get_organization_name_and_metadata_from_siret,
)
from plugins.la_suite.hooks_utils.communes import CommuneCreation


@register_hook("organization_created")
def get_organization_name_and_metadata_from_siret_hook(organization):
    """After creating an organization, update the organization name & metadata."""
    get_organization_name_and_metadata_from_siret(organization)


@register_hook("organization_created")
def commune_organization_created(organization):
    """After creating an organization, update the organization name."""
    CommuneCreation().run_after_create(organization)


@register_hook("organization_access_granted")
def commune_organization_access_granted(organization_access):
    """After granting an organization access, check for needed domain access grant."""
    CommuneCreation().run_after_grant_access(organization_access)
