"""Resource server API endpoints"""

from django.db.models import OuterRef, Prefetch, Subquery

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
                accesses__user=self.request.user,
                service_providers__audience_id=service_provider_audience,
            )
            .annotate(user_role=Subquery(user_role_query))
        )

    def perform_create(self, serializer):
        """Set the current user as owner of the newly created team."""
        team = serializer.save()
        models.TeamAccess.objects.create(
            team=team,
            user=self.request.user,
            role=models.RoleChoices.OWNER,
        )
