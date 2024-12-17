"""Resource server API endpoints"""

import operator
from functools import reduce

from django.db.models import OuterRef, Prefetch, Q, Subquery, Value
from django.db.models.functions import Coalesce

from rest_framework import (
    filters,
    mixins,
    viewsets,
)

from core import models
from core.api import permissions
from core.api.client.viewsets import Pagination
from core.resource_server.mixins import ResourceServerMixin

from . import serializers


class TeamViewSet(  # pylint: disable=too-many-ancestors
    ResourceServerMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    Team ViewSet dedicated to the resource server.

    The DELETE method is not allowed for now, because the use case is
    not clear yet and it comes with complexity to know if we can delete
    a team or not (eg. if a team has other SP, it might not be deleted
    but what do we do then, only remove the current SP?).

    GET /resource-server/v1.0/teams/
        Return list of Teams of the user and available for the audience.

    POST /resource-server/v1.0/teams/
        Create a new Team for the user for the audience.

    GET /resource-server/v1.0/teams/{team_id}/
        Return the Team details if available for the audience.

    PUT /resource-server/v1.0/teams/{team_id}/
        Update the Team details (only name for now).

    """

    permission_classes = [permissions.AccessPermission]
    serializer_class = serializers.TeamSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    queryset = models.Team.objects.all()
    pagination_class = Pagination

    def get_queryset(self):
        """Custom queryset to get user related teams."""
        teams_queryset = models.Team.objects.filter(
            accesses__user=self.request.user,
        )
        depth_path = teams_queryset.values("depth", "path")

        if not depth_path:
            return models.Team.objects.none()

        user_role_query = models.TeamAccess.objects.filter(
            user=self.request.user, team=OuterRef("pk")
        ).values("role")[:1]

        service_provider_audience = self._get_service_provider_audience()
        service_provider_prefetch = Prefetch(
            "service_providers",
            queryset=models.ServiceProvider.objects.filter(
                audience_id=service_provider_audience
            ),
        )

        return (
            models.Team.objects.prefetch_related(
                "accesses",
                service_provider_prefetch,
            )
            .filter(
                reduce(
                    operator.or_,
                    (
                        Q(
                            # The team the user has access to
                            depth=d["depth"],
                            path=d["path"],
                        )
                        | Q(
                            # The parent team the user has access to
                            depth__lt=d["depth"],
                            path__startswith=d["path"][: models.Team.steplen],
                            organization_id=self.request.user.organization_id,
                        )
                        for d in depth_path
                    ),
                ),
                service_providers__audience_id=service_provider_audience,
            )
            # Abilities are computed based on logged-in user's role for the team
            # and if the user does not have access, it's ok to consider them as a member
            # because it's a parent team.
            .annotate(
                user_role=Coalesce(
                    Subquery(user_role_query), Value(models.RoleChoices.MEMBER.value)
                )
            )
        )

    def perform_create(self, serializer):
        """Set the current user as owner of the newly created team."""
        team = serializer.save()
        models.TeamAccess.objects.create(
            team=team,
            user=self.request.user,
            role=models.RoleChoices.OWNER,
        )
