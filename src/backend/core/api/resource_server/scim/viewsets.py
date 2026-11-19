"""Resource server SCIM API endpoints"""

from django.contrib.auth import get_user_model

from lasuite.oidc_resource_server.mixins import ResourceServerMixin
from rest_framework import (
    viewsets,
)

from core.api import permissions

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

    Endpoint:
    GET /resource-server/v1.0/scim/Me/
        Retrieves the authenticated user's details.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.SCIMUserSerializer

    def get_exception_handler(self):
        """Override the default exception handler to use SCIM-specific handling."""
        return scim_exception_handler

    def list(self, request, *args, **kwargs):
        """Return the current user's details in SCIM format."""
        user = User.objects.get(pk=request.user.pk)

        serializer = self.serializer_class(user, context={"request": request})
        return ScimJsonResponse(serializer.data)
