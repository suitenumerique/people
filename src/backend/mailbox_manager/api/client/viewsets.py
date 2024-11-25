"""API endpoints"""

from django.db.models import Subquery

from rest_framework import exceptions, filters, mixins, viewsets

from core import models as core_models

from mailbox_manager import enums, models
from mailbox_manager.api import permissions
from mailbox_manager.api.client import serializers


# pylint: disable=too-many-ancestors
class MailDomainViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    MailDomain viewset.

    GET /api/<version>/mail-domains/
        Return a list of mail domains user has access to.

    GET /api/<version>/mail-domains/<domain-slug>/
        Return details for a mail domain user has access to.

    POST /api/<version>/mail-domains/ with expected data:
        - name: str
        Return newly created domain
    """

    permission_classes = [permissions.AccessPermission]
    serializer_class = serializers.MailDomainSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "name"]
    ordering = ["-created_at"]
    lookup_field = "slug"
    queryset = models.MailDomain.objects.all()

    def get_queryset(self):
        """Restrict results to the current user's team."""
        return self.queryset.filter(accesses__user=self.request.user)

    def perform_create(self, serializer):
        """Set the current user as owner of the newly created mail domain."""

        domain = serializer.save()
        models.MailDomainAccess.objects.create(
            user=self.request.user,
            domain=domain,
            role=core_models.RoleChoices.OWNER,
        )


# pylint: disable=too-many-ancestors
class MailDomainAccessViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
):
    """
    API ViewSet for all interactions with mail domain accesses.

    GET /api/v1.0/mail-domains/<domain_slug>/accesses/:<domain_access_id>
        Return list of all domain accesses related to the logged-in user and one
        domain access if an id is provided.

    POST /api/v1.0/mail-domains/<domain_slug>/accesses/ with expected data:
        - user: str
        - role: str [owner|admin|viewer]
        Return newly created mail domain access

    PUT /api/v1.0/mail-domains/<domain_slug>/accesses/<domain_access_id>/ with expected data:
        - role: str [owner|admin|viewer]
        Return updated domain access

    PATCH /api/v1.0/mail-domains/<domain_slug>/accesses/<domain_access_id>/ with expected data:
        - role: str [owner|admin|viewer]
        Return partially updated domain access

    DELETE /api/v1.0/mail-domains/<domain_slug>/accesses/<domain_access_id>/
        Delete targeted domain access
    """

    permission_classes = [permissions.MailDomainAccessRolePermission]
    serializer_class = serializers.MailDomainAccessSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["role", "user__email", "user__name"]
    ordering = ["-created_at"]
    queryset = (
        models.MailDomainAccess.objects.all()
        .select_related("user")
        .order_by("-created_at")
    )
    list_serializer_class = serializers.MailDomainAccessReadOnlySerializer
    detail_serializer_class = serializers.MailDomainAccessSerializer

    def get_serializer_class(self):
        """Chooses list or detail serializer according to the action."""
        if self.action in {"list", "retrieve"}:
            return self.list_serializer_class
        return self.detail_serializer_class

    def get_serializer_context(self):
        """Extra context provided to the serializer class."""
        context = super().get_serializer_context()
        context["domain_slug"] = self.kwargs["domain_slug"]
        context["authenticated_user"] = self.request.user
        return context

    def get_queryset(self):
        """Return the queryset according to the action."""
        queryset = super().get_queryset()
        queryset = queryset.filter(domain__slug=self.kwargs["domain_slug"])

        if self.action in {"list", "retrieve"}:
            # Determine which role the logged-in user has in the domain
            user_role_query = models.MailDomainAccess.objects.filter(
                user=self.request.user, domain__slug=self.kwargs["domain_slug"]
            ).values("role")[:1]

            queryset = (
                # The logged-in user should be part of a domain to see its accesses
                queryset.filter(
                    domain__accesses__user=self.request.user,
                )
                # Abilities are computed based on logged-in user's role and
                # the user role on each domain access
                .annotate(
                    user_role=Subquery(user_role_query),
                )
                .select_related("user")
                .distinct()
            )
        return queryset

    def perform_update(self, serializer):
        """Check that we don't change the role if it leads to losing the last owner."""
        instance = serializer.instance

        # Check if the role is being updated and the new role is not "owner"
        if (
            "role" in self.request.data
            and self.request.data["role"] != enums.MailDomainRoleChoices.OWNER
        ):
            domain = instance.domain
            # Check if the access being updated is the last owner access for the domain
            if (
                instance.role == enums.MailDomainRoleChoices.OWNER
                and domain.accesses.filter(
                    role=enums.MailDomainRoleChoices.OWNER
                ).count()
                == 1
            ):
                message = "Cannot change the role to a non-owner role for the last owner access."
                raise exceptions.PermissionDenied({"role": message})
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """Forbid deleting the last owner access"""
        instance = self.get_object()
        domain = instance.domain

        # Check if the access being deleted is the last owner access for the domain
        if (
            instance.role == enums.MailDomainRoleChoices.OWNER
            and domain.accesses.filter(role=enums.MailDomainRoleChoices.OWNER).count()
            == 1
        ):
            message = "Cannot delete the last owner access for the domain."
            raise exceptions.PermissionDenied({"detail": message})

        return super().destroy(request, *args, **kwargs)


class MailBoxViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """MailBox ViewSet

    GET /api/<version>/mail-domains/<domain-slug>/mailboxes/
        Return a list of mailboxes on the domain

    POST /api/<version>/mail-domains/<domain-slug>/mailboxes/ with expected data:
        - first_name: str
        - last_name: str
        - local_part: str
        - secondary_email: str
        Sends request to email provisioning API and returns newly created mailbox
    """

    permission_classes = [permissions.MailBoxPermission]
    serializer_class = serializers.MailboxSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ["-created_at"]
    queryset = models.Mailbox.objects.all()

    def get_queryset(self):
        """Custom queryset to get mailboxes related to a mail domain."""
        domain_slug = self.kwargs.get("domain_slug", "")
        if domain_slug:
            return self.queryset.filter(domain__slug=domain_slug)
        return self.queryset

    def perform_create(self, serializer):
        """Create new mailbox."""
        domain_slug = self.kwargs.get("domain_slug", "")
        if domain_slug:
            serializer.validated_data["domain"] = models.MailDomain.objects.get(
                slug=domain_slug
            )
        super().perform_create(serializer)
