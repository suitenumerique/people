"""API endpoints"""

import datetime

from django.conf import settings
from django.db.models import OuterRef, Q, Subquery
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import (
    decorators,
    filters,
    mixins,
    pagination,
    response,
    throttling,
    views,
    viewsets,
)
from rest_framework.permissions import AllowAny

from core import models
from core.api import permissions
from core.api.client import serializers
from core.utils.raw_sql import gen_sql_filter_json_array

from mailbox_manager import enums
from mailbox_manager import models as domains_models


class NestedGenericViewSet(viewsets.GenericViewSet):
    """
    A generic Viewset aims to be used in a nested route context.
    e.g: `/api/v1.0/resource_1/<resource_1_pk>/resource_2/<resource_2_pk>/`

    It allows to define all url kwargs and lookup fields to perform the lookup.
    """

    lookup_fields: list[str] = ["pk"]
    lookup_url_kwargs: list[str] = []

    def __getattribute__(self, item):
        """
        This method is overridden to allow to get the last lookup field or lookup url kwarg
        when accessing the `lookup_field` or `lookup_url_kwarg` attribute. This is useful
        to keep compatibility with all methods used by the parent class `GenericViewSet`.
        """
        if item in ["lookup_field", "lookup_url_kwarg"]:
            return getattr(self, item + "s", [None])[-1]

        return super().__getattribute__(item)

    def get_queryset(self):
        """
        Get the list of items for this view.

        `lookup_fields` attribute is enumerated here to perform the nested lookup.
        """
        queryset = super().get_queryset()

        # The last lookup field is removed to perform the nested lookup as it corresponds
        # to the object pk, it is used within get_object method.
        lookup_url_kwargs = (
            self.lookup_url_kwargs[:-1]
            if self.lookup_url_kwargs
            else self.lookup_fields[:-1]
        )

        filter_kwargs = {}
        for index, lookup_url_kwarg in enumerate(lookup_url_kwargs):
            if lookup_url_kwarg not in self.kwargs:
                raise KeyError(
                    f"Expected view {self.__class__.__name__} to be called with a URL "
                    f'keyword argument named "{lookup_url_kwarg}". Fix your URL conf, or '
                    "set the `.lookup_fields` attribute on the view correctly."
                )

            filter_kwargs.update(
                {self.lookup_fields[index]: self.kwargs[lookup_url_kwarg]}
            )

        return queryset.filter(**filter_kwargs)


class SerializerPerActionMixin:
    """
    A mixin to allow to define serializer classes for each action.

    This mixin is useful to avoid to define a serializer class for each action in the
    `get_serializer_class` method.

    Example:
    ```
    class MyViewSet(SerializerPerActionMixin, viewsets.GenericViewSet):
        serializer_class = MySerializer
        list_serializer_class = MyListSerializer
        retrieve_serializer_class = MyRetrieveSerializer
    ```
    """

    def get_serializer_class(self):
        """
        Return the serializer class to use depending on the action.
        """
        if serializer_class := getattr(self, f"{self.action}_serializer_class", None):
            return serializer_class
        return super().get_serializer_class()


class Pagination(pagination.PageNumberPagination):
    """Pagination to display no more than 100 objects per page sorted by creation date."""

    max_page_size = 100
    page_size_query_param = "page_size"


class BurstRateThrottle(throttling.UserRateThrottle):
    """
    Throttle rate for minutes. See DRF section in settings for default value.
    """

    scope = "burst"


class SustainedRateThrottle(throttling.UserRateThrottle):
    """
    Throttle rate for hours. See DRF section in settings for default value.
    """

    scope = "sustained"

class OrganizationViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    Organization ViewSet

    GET /api/organizations/<organization_id>/
        Return the organization details for the given id.

    PUT /api/organizations/<organization_id>/
        Update the organization details for the given id.

    PATCH /api/organizations/<organization_id>/
        Partially update the organization details for the given id.
    """

    permission_classes = [permissions.AccessPermission]
    queryset = models.Organization.objects.all()
    serializer_class = serializers.OrganizationSerializer
    throttle_classes = [BurstRateThrottle, SustainedRateThrottle]

    def get_queryset(self):
        """Limit listed organizations to the one the user belongs to."""
        return (
            super()
            .get_queryset()
            .filter(pk=self.request.user.organization_id)
            .annotate(
                user_role=Subquery(
                    models.OrganizationAccess.objects.filter(
                        user=self.request.user, organization=OuterRef("pk")
                    ).values("role")[:1]
                )
            )
        )


class UserViewSet(
    SerializerPerActionMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
):
    """
    User viewset for all interactions with user infos.

    GET /api/users/&q=query
        Return a list of users whose email or name matches the query.
    """

    permission_classes = [permissions.IsSelf]
    queryset = (
        models.User.objects.select_related("organization").all().order_by("-created_at")
    )
    serializer_class = serializers.UserSerializer
    get_me_serializer_class = serializers.UserMeSerializer
    throttle_classes = [BurstRateThrottle, SustainedRateThrottle]
    pagination_class = Pagination

    def get_queryset(self):
        """Limit listed users by a query. Pagination and throttle protection apply."""
        queryset = self.queryset

        if self.action == "list":
            # Filter active users
            # and users from same organization
            queryset = queryset.filter(
                is_active=True, organization_id=self.request.user.organization_id
            )

            # Search by case-insensitive and accent-insensitive
            if query := self.request.GET.get("q", ""):
                queryset = queryset.filter(
                    Q(name__unaccent__icontains=query)
                    | Q(email__unaccent__icontains=query)
                )

        return queryset

    @decorators.action(
        detail=False,
        methods=["get"],
        url_name="me",
        url_path="me",
    )
    def get_me(self, request):
        """
        Return information on currently logged user
        """
        user = request.user
        return response.Response(self.get_serializer(user).data)


class ConfigView(views.APIView):
    """API ViewSet for sharing some public settings."""

    permission_classes = [AllowAny]

    def get(self, request):
        """
        GET /api/v1.0/config/
            Return a dictionary of public settings.
        """
        array_settings = [
            "LANGUAGES",
            "FEATURES",
            "RELEASE",
            "COMMIT",
        ]
        dict_settings = {}
        for setting in array_settings:
            dict_settings[setting] = getattr(settings, setting)

        return response.Response(dict_settings)


class StatView(views.APIView):
    """API ViewSet for sharing some public metrics."""

    permission_classes = [AllowAny]

    @method_decorator(cache_page(3600))
    def get(self, request):
        """
        GET /api/v1.0/stats/
            Return a dictionary of public metrics.
        """
        context = {
            "total_users": models.User.objects.count(),
            "mau": models.User.objects.filter(
                last_login__gte=timezone.now() - datetime.timedelta(30)
            ).count(),
            "active_domains": domains_models.MailDomain.objects.filter(
                status=enums.MailDomainStatusChoices.ENABLED
            ).count(),
            "mailboxes": domains_models.Mailbox.objects.count(),
            "aliases": domains_models.Alias.objects.count(),
        }
        return response.Response(context)


class ServiceProviderFilter(filters.BaseFilterBackend):
    """
    Filter service providers.
    """

    def filter_queryset(self, request, queryset, view):
        """
        Filter service providers by audience or name.
        """
        if name := request.GET.get("name"):
            queryset = queryset.filter(name__icontains=name)
        if audience_id := request.GET.get("audience_id"):
            queryset = queryset.filter(audience_id=audience_id)
        return queryset


class ServiceProviderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    API ViewSet for all interactions with service providers.

    GET /api/v1.0/service-providers/
        Return a list of service providers.

    GET /api/v1.0/service-providers/<service_provider_id>/
        Return a service provider.
    """

    permission_classes = [permissions.IsAuthenticated]
    queryset = models.ServiceProvider.objects.all()
    serializer_class = serializers.ServiceProviderSerializer
    throttle_classes = [BurstRateThrottle, SustainedRateThrottle]
    pagination_class = Pagination
    filter_backends = [filters.OrderingFilter, ServiceProviderFilter]
    ordering = ["name"]
    ordering_fields = ["name", "created_at"]

    def get_queryset(self):
        """Filter the queryset to limit results to user's organization."""
        queryset = super().get_queryset()
        queryset = queryset.filter(organizations__id=self.request.user.organization_id)
        return queryset
