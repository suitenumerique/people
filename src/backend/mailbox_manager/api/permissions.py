"""Permission handlers for the People mailbox manager app."""

from django.shortcuts import get_object_or_404

from rest_framework import permissions

from core.api.permissions import IsAuthenticated

from mailbox_manager import models


class DomainPermission(IsAuthenticated):
    """Permission class to manage mailboxes and aliases for a mail domain"""

    def has_permission(self, request, view):
        """Check permission based on domain."""

        if not super().has_permission(request, view):
            return False

        if not view.kwargs.get("domain_slug"):
            return True

        domain = get_object_or_404(
            models.MailDomain,
            slug=view.kwargs.get("domain_slug", ""),
            accesses__user=request.user,
        )
        # domain = models.MailDomain.objects.get(slug=view.kwargs.get("domain_slug", ""))
        abilities = domain.get_abilities(request.user)
        if request.method.lower() == "delete":
            return abilities.get("manage_accesses", False)

        return abilities.get(request.method.lower(), False)


class DomainResourcePermission(DomainPermission):
    """Permission class for access objects."""

    def has_object_permission(self, request, view, obj):
        """Check permission for a given object."""
        abilities = obj.get_abilities(request.user)
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
