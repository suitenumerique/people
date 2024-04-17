"""Permission handlers for the People mailbox manager app."""

from core.api import permissions as core_permissions


class AccessPermission(core_permissions.IsAuthenticated):
    """Permission class for access objects."""

    def has_object_permission(self, request, view, obj):
        """Check permission for a given object."""
        abilities = obj.get_abilities(request.user)
        return abilities.get(request.method.lower(), False)
