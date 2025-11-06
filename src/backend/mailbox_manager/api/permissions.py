"""Permission handlers for the People mailbox manager app."""

from rest_framework import permissions

from core.api import permissions as core_permissions

from mailbox_manager import models


class DomainResourcePermission(core_permissions.IsAuthenticated):
    """Permission class for access objects."""

    def has_object_permission(self, request, view, obj):
        """Check permission for a given object."""
        abilities = obj.get_abilities(request.user)
        return abilities.get(request.method.lower(), False)


class DomainPermission(DomainResourcePermission):
    """Permission class to manage mailboxes and aliases for a mail domain"""

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


class IsAliasDestinationPermission(core_permissions.IsAuthenticated):
    """Can delete an alias if the alias points to their own email address."""

    def has_permission(self, request, view):
        """This permission is specifically about updates"""
        domain = models.MailDomain.objects.get(slug=view.kwargs.get("domain_slug", ""))
        abilities = domain.get_abilities(request.user)
        return abilities["get"]

    def has_object_permission(self, request, view, obj):
        """If the user is trying to update their own mailbox."""
        return obj.destination == request.user.email
