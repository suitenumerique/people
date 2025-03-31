"""API viewsets for La Suite plugin"""

from rest_framework import viewsets
from rest_framework.mixins import ListModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from core.authentication.backends import AccountServiceAuthentication
from core.models import Organization


class ScopeAPIPermission(BasePermission):
    """Permission to check if the user has the correct scope."""

    def has_permission(self, request, view):
        """Check if the user has the correct scope."""
        if not request.auth:
            return False
        return view.scope in request.user.scopes


class Pagination(PageNumberPagination):
    """Pagination to display no more than 1000 objects per page"""

    page_size = 100
    max_page_size = 1000
    page_size_query_param = "page_size"


class ActiveOrganizationsSiret(viewsets.GenericViewSet, ListModelMixin):
    """
    ViewSet to list all SIRET of active communes.

    * Requires API key authentication.
    * Only services with the correct scope are able to access this view.
    """

    authentication_classes = [AccountServiceAuthentication]
    permission_classes = [ScopeAPIPermission]
    pagination_class = Pagination
    scope = "la-suite-list-organizations-siret"

    def get_queryset(self):
        """
        Return queryset of active communes.
        """
        return Organization.objects.filter(
            metadata__is_commune=True,
            registration_id_list__isnull=False,
            is_active=True,
        ).order_by("-created_at")

    def list(self, request, *args, **kwargs):
        """
        Return a list of all SIRET of active communes.
        """
        registration_ids_lists = self.get_queryset().values_list(
            "registration_id_list", flat=True
        )
        registration_ids = [
            registration_id
            for registration_ids_list in registration_ids_lists
            for registration_id in registration_ids_list
        ]

        page = self.paginate_queryset(registration_ids)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(registration_ids)
