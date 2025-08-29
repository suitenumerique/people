"""Permission handlers for the People mailbox manager app."""

from rest_framework import permissions

from core.api import permissions as core_permissions

from mailbox_manager import models


class AccessPermission(core_permissions.IsAuthenticated):
    """Permission class for access objects."""

    def has_object_permission(self, request, view, obj):
        """Check permission for a given object."""
        abilities = obj.get_abilities(request.user)
        return abilities.get(request.method.lower(), False)


class MailBoxPermission(AccessPermission):
    """Permission class to manage mailboxes for a mail domain"""

    def has_permission(self, request, view):
        """Check permission based on domain."""
        domain = models.MailDomain.objects.get(slug=view.kwargs.get("domain_slug", ""))
        abilities = domain.get_abilities(request.user)
        return abilities.get(request.method.lower(), False)


class IsMailboxOwnerPermission(permissions.BasePermission):
    """Authorize update for domain viewers on their own mailbox."""

    def has_permission(self, request, view):
        """This permission is specifically about updates"""
        domain = models.MailDomain.objects.get(slug=view.kwargs.get("domain_slug", ""))
        abilities = domain.get_abilities(request.user)
        return abilities["get"]

    def has_object_permission(self, request, view, obj):
        """If the user is trying to update their own mailbox."""
        return obj.get_email() == request.user.email


class MailDomainAccessRolePermission(core_permissions.IsAuthenticated):
    """Permission class to manage mailboxes for a mail domain"""

    def has_object_permission(self, request, view, obj):
        """Check permission for a given object."""
        abilities = obj.get_abilities(request.user)
        return abilities.get(request.method.lower(), False)
