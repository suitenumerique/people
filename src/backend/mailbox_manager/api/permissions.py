"""Permission handlers for the People mailbox manager app."""

from core.api import permissions as core_permissions

from mailbox_manager import models


class AccessPermission(core_permissions.IsAuthenticated):
    """Permission class for access objects."""

    def has_object_permission(self, request, view, obj):
        """Check permission for a given object."""
        abilities = obj.get_abilities(request.user)
        return abilities.get(request.method.lower(), False)


class MailBoxPermission(core_permissions.IsAuthenticated):
    """Permission class to manage mailboxes for a mail domain"""

    def has_permission(self, request, view):
        """Check permission based on domain."""
        domain = models.MailDomain.objects.get(slug=view.kwargs.get("domain_slug", ""))
        abilities = domain.get_abilities(request.user)

        # Authorize "patch" for all domain roles so that domain viewers
        # can updating the secondary email of their own address.
        # Finer permissions will be calculated in "has_object_permission"
        if request.resolver_match.url_name == "mailboxes-detail":
            abilities["patch"] = abilities["get"]

        return abilities.get(request.method.lower(), False)

    def has_object_permission(self, request, view, obj):
        """Check permission for a given object."""
        abilities = obj.get_abilities(request.user)
        return abilities.get(request.method.lower(), False)


class MailDomainAccessRolePermission(core_permissions.IsAuthenticated):
    """Permission class to manage mailboxes for a mail domain"""

    def has_object_permission(self, request, view, obj):
        """Check permission for a given object."""
        abilities = obj.get_abilities(request.user)
        return abilities.get(request.method.lower(), False)
