"""Permissions for token exchange app."""

from rest_framework.permissions import BasePermission

from core.models import ServiceProvider


class IsServiceProviderAuthenticated(BasePermission):
    """
    Allows access only to authenticated ServiceProvider.
    """

    def has_permission(self, request, view):
        """Check if the user is an authenticated ServiceProvider."""
        return bool(
            isinstance(request.user, ServiceProvider)
            and request.user
            and request.user.is_authenticated
        )
