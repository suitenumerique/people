"""Resource server SCIM API endpoints"""

from django.contrib.auth import get_user_model
from django.db.models import Prefetch, Q

from lasuite.oidc_resource_server.mixins import ResourceServerMixin
from rest_framework import (
    viewsets,
)

from core.api import permissions
from core.models import TeamAccess

from . import serializers
from .exceptions import scim_exception_handler
from .response import ScimJsonResponse

User = get_user_model()


class MeViewSet(ResourceServerMixin, viewsets.ViewSet):
    """
    SCIM-compliant ViewSet for the /Me endpoint.

    This endpoint provides information about the currently authenticated user
    in SCIM (System for Cross-domain Identity Management) format.

    Features:
    - Returns user details in SCIM format.
    - Includes the user's teams, restricted to the audience.

    Limitations:
    - Does not currently support managing Team hierarchies.

    Endpoint:
    GET /resource-server/v1.0/scim/Me/
        Retrieves the authenticated user's details and associated teams.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.SCIMUserSerializer

    def get_exception_handler(self):
        """Override the default exception handler to use SCIM-specific handling."""
        return scim_exception_handler

    def list(self, request, *args, **kwargs):
        """Return the current user's details in SCIM format."""
        service_provider_audience = self._get_service_provider_audience()

        user = User.objects.prefetch_related(
            Prefetch(
                "accesses",
                queryset=TeamAccess.objects.select_related("team").filter(
                    Q(team__service_providers__audience_id=service_provider_audience)
                    | Q(team__is_visible_all_services=True)
                ),
            )
        ).get(pk=request.user.pk)

        serializer = self.serializer_class(user, context={"request": request})
        return ScimJsonResponse(serializer.data)
