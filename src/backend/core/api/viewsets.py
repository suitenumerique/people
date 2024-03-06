"""API endpoints"""

from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Func, Max, OuterRef, Prefetch, Q, Subquery, Value

from rest_framework import (
    decorators,
    exceptions,
    filters,
    mixins,
    pagination,
    response,
    viewsets,
)
from rest_framework.throttling import UserRateThrottle

from core import models

from . import permissions, serializers

EMAIL_SIMILARITY_THRESHOLD = 0.01
# TrigramSimilarity threshold is lower for searching email than for names,
# to improve matching results


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
    """

    serializer_classes: dict[str, type] = {}
    default_serializer_class: type = None

    def get_serializer_class(self):
        """
        Return the serializer class to use depending on the action.
        """
        return self.serializer_classes.get(self.action, self.default_serializer_class)


class Pagination(pagination.PageNumberPagination):
    """Pagination to display no more than 100 objects per page sorted by creation date."""

    ordering = "-created_on"
    max_page_size = 100
    page_size_query_param = "page_size"


class BurstRateThrottle(UserRateThrottle):
    """
    Throttle rate for minutes. See DRF section in settings for default value.
    """

    scope = "burst"


class SustainedRateThrottle(UserRateThrottle):
    """
    Throttle rate for hours. See DRF section in settings for default value.
    """

    scope = "sustained"


# pylint: disable=too-many-ancestors
class ContactViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Contact ViewSet"""

    permission_classes = [permissions.IsOwnedOrPublic]
    queryset = models.Contact.objects.all()
    serializer_class = serializers.ContactSerializer
    throttle_classes = [BurstRateThrottle, SustainedRateThrottle]

    def list(self, request, *args, **kwargs):
        """Limit listed users by a query with throttle protection."""
        user = self.request.user
        queryset = self.filter_queryset(self.get_queryset())

        # Exclude contacts that:
        queryset = queryset.filter(
            # - belong to another user (keep public and owned contacts)
            Q(owner__isnull=True) | Q(owner=user),
            # - are profile contacts for a user
            user__isnull=True,
            # - are overriden base contacts
            overriding_contacts__isnull=True,
        )

        # Search by case-insensitive and accent-insensitive trigram similarity
        if query := self.request.GET.get("q", ""):
            query = Func(Value(query), function="unaccent")
            similarity = TrigramSimilarity(
                Func("full_name", function="unaccent"),
                query,
            ) + TrigramSimilarity(Func("short_name", function="unaccent"), query)
            queryset = (
                queryset.annotate(similarity=similarity)
                .filter(
                    similarity__gte=0.05
                )  # Value determined by testing (test_api_contacts.py)
                .order_by("-similarity")
            )

        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)

    def perform_create(self, serializer):
        """Set the current user as owner of the newly created contact."""
        user = self.request.user
        serializer.validated_data["owner"] = user
        return super().perform_create(serializer)


class UserViewSet(
    mixins.UpdateModelMixin, viewsets.GenericViewSet, mixins.ListModelMixin
):
    """
    User viewset for all interactions with user infos and teams.

    GET /api/users/&q=query
        Return a list of users whose email matches the query. Similarity is
        calculated using trigram similarity, allowing for partial,
        case-insensitive matches and accented queries.
    """

    permission_classes = [permissions.IsSelf]
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    throttle_classes = [BurstRateThrottle, SustainedRateThrottle]
    pagination_class = Pagination

    def get_queryset(self):
        """Limit listed users by a query. Pagination and throttle protection apply."""
        queryset = self.queryset

        if self.action == "list":
            # Exclude inactive contacts
            queryset = queryset.filter(
                is_active=True,
            ).prefetch_related(
                Prefetch(
                    "identities",
                    queryset=models.Identity.objects.filter(is_main=True),
                    to_attr="main_identity",
                )
            )

            # Search by case-insensitive and accent-insensitive trigram similarity
            if query := self.request.GET.get("q", ""):
                similarity = Max(
                    TrigramSimilarity(
                        Func("identities__email", function="unaccent"),
                        Func(Value(query), function="unaccent"),
                    )
                )
                queryset = (
                    queryset.annotate(similarity=similarity)
                    .filter(similarity__gte=EMAIL_SIMILARITY_THRESHOLD)
                    .order_by("-similarity")
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
        user.main_identity = models.Identity.objects.filter(
            user=user, is_main=True
        ).first()
        return response.Response(
            self.serializer_class(user, context={"request": request}).data
        )


class TeamViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Team ViewSet"""

    permission_classes = [permissions.AccessPermission]
    serializer_class = serializers.TeamSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    queryset = models.Team.objects.all()

    def get_queryset(self):
        """Custom queryset to get user related teams."""
        user_role_query = models.TeamAccess.objects.filter(
            user=self.request.user, team=OuterRef("pk")
        ).values("role")[:1]
        return models.Team.objects.filter(accesses__user=self.request.user).annotate(
            user_role=Subquery(user_role_query)
        )

    def perform_create(self, serializer):
        """Set the current user as owner of the newly created team."""
        team = serializer.save()
        models.TeamAccess.objects.create(
            team=team,
            user=self.request.user,
            role=models.RoleChoices.OWNER,
        )


class TeamAccessViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    API ViewSet for all interactions with team accesses.

    GET /api/v1.0/teams/<team_id>/accesses/:<team_access_id>
        Return list of all team accesses related to the logged-in user or one
        team access if an id is provided.

    POST /api/v1.0/teams/<team_id>/accesses/ with expected data:
        - user: str
        - role: str [owner|admin|member]
        Return newly created team access

    PUT /api/v1.0/teams/<team_id>/accesses/<team_access_id>/ with expected data:
        - role: str [owner|admin|member]
        Return updated team access

    PATCH /api/v1.0/teams/<team_id>/accesses/<team_access_id>/ with expected data:
        - role: str [owner|admin|member]
        Return partially updated team access

    DELETE /api/v1.0/teams/<team_id>/accesses/<team_access_id>/
        Delete targeted team access
    """

    lookup_field = "pk"
    pagination_class = Pagination
    permission_classes = [permissions.AccessPermission]
    queryset = models.TeamAccess.objects.all().select_related("user")
    list_serializer_class = serializers.TeamAccessReadOnlySerializer
    detail_serializer_class = serializers.TeamAccessSerializer

    def get_permissions(self):
        """User only needs to be authenticated to list team accesses"""
        if self.action == "list":
            permission_classes = [permissions.IsAuthenticated]
        else:
            return super().get_permissions()

        return [permission() for permission in permission_classes]

    def get_serializer_context(self):
        """Extra context provided to the serializer class."""
        context = super().get_serializer_context()
        context["team_id"] = self.kwargs["team_id"]
        return context

    def get_serializer_class(self):
        if self.action in {"list", "retrieve"}:
            return self.list_serializer_class
        return self.detail_serializer_class

    def get_queryset(self):
        """Return the queryset according to the action."""
        queryset = super().get_queryset()
        queryset = queryset.filter(team=self.kwargs["team_id"])

        if self.action in {"list", "retrieve"}:
            # Determine which role the logged-in user has in the team
            user_role_query = models.TeamAccess.objects.filter(
                user=self.request.user, team=self.kwargs["team_id"]
            ).values("role")[:1]

            queryset = (
                # The logged-in user should be part of a team to see its accesses
                queryset.filter(
                    team__accesses__user=self.request.user,
                )
                .prefetch_related(
                    Prefetch(
                        "user__identities",
                        queryset=models.Identity.objects.filter(is_main=True),
                        to_attr="main_identity",
                    )
                )
                # Abilities are computed based on logged-in user's role and
                # the user role on each team access
                .annotate(user_role=Subquery(user_role_query))
                .distinct()
            )
        return queryset

    def destroy(self, request, *args, **kwargs):
        """Forbid deleting the last owner access"""
        instance = self.get_object()
        team = instance.team

        # Check if the access being deleted is the last owner access for the team
        if instance.role == "owner" and team.accesses.filter(role="owner").count() == 1:
            return response.Response(
                {"detail": "Cannot delete the last owner access for the team."},
                status=400,
            )

        return super().destroy(request, *args, **kwargs)

    def perform_update(self, serializer):
        """Check that we don't change the role if it leads to losing the last owner."""
        instance = serializer.instance

        # Check if the role is being updated and the new role is not "owner"
        if (
            "role" in self.request.data
            and self.request.data["role"] != models.RoleChoices.OWNER
        ):
            team = instance.team
            # Check if the access being updated is the last owner access for the team
            if (
                instance.role == models.RoleChoices.OWNER
                and team.accesses.filter(role=models.RoleChoices.OWNER).count() == 1
            ):
                message = "Cannot change the role to a non-owner role for the last owner access."
                raise exceptions.ValidationError({"role": message})

        serializer.save()
