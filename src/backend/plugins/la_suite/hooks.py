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


@register_hook("organization_created")
def get_organization_name_and_metadata_from_siret_hook(organization):
    """After creating an organization, update the organization name & metadata."""
    get_organization_name_and_metadata_from_siret(organization)
