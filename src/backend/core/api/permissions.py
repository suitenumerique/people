"""Permission handlers for the People core app."""

from django.core import exceptions

from rest_framework import permissions

from core import models


class IsAuthenticated(permissions.BasePermission):
    """
    Allows access only to authenticated users. Alternative method checking the presence
    of the auth token to avoid hitting the database.
    """

    def has_permission(self, request, view):
        """Check auth token first."""
        return bool(request.auth) if request.auth else request.user.is_authenticated


class IsSelf(IsAuthenticated):
    """
    Allows access only to user's own data.
    """

    def has_object_permission(self, request, view, obj):
        """Write permissions are only allowed to the user itself."""
        return obj == request.user


class IsOwnedOrPublic(IsAuthenticated):
    """
    Allows access to authenticated users only for objects that are owned or not related
    to any user via the "owner" field.
    """

    def has_object_permission(self, request, view, obj):
        """Unsafe permissions are only allowed for the owner of the object."""
        if obj.owner == request.user:
            return True

        if request.method in permissions.SAFE_METHODS and obj.owner is None:
            return True

        try:
            return obj.user == request.user
        except exceptions.ObjectDoesNotExist:
            return False


class AccessPermission(IsAuthenticated):
    """Permission class for access objects."""

    def has_object_permission(self, request, view, obj):
        """Check permission for a given object."""
        abilities = obj.get_abilities(request.user)
        return abilities.get(request.method.lower(), False)


class TeamPermission(IsAuthenticated):
    """Permission class for team objects viewset."""

    def has_permission(self, request, view):
        """Check permission only when the user tries to create a new team."""
        if not super().has_permission(request, view):
            return False

        if request.method != "POST":
            return True

        abilities = request.user.get_abilities()
        return abilities["teams"]["can_create"]


class TeamInvitationCreationPermission(IsAuthenticated):
    """Permission class that allows only team owners and admins to perform actions."""

    def has_permission(self, request, view):
        """Check if user is authenticated and has required role for the team."""
        if not super().has_permission(request, view):
            return False

        # Only check roles for edition operations
        if request.method in permissions.SAFE_METHODS:
            return True

        team_id = view.kwargs.get("team_id")
        if not team_id:
            return False

        team_access = models.TeamAccess.objects.filter(
            team_id=team_id,
            user=request.user,
            role__in=[models.RoleChoices.OWNER, models.RoleChoices.ADMIN],
        ).exists()

        return team_access
