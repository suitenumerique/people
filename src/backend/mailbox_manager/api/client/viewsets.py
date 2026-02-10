"""API endpoints"""

from django.db.models import Q, Subquery
from django.http import Http404

from rest_framework import exceptions, filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core import models as core_models
from core.api.client.serializers import UserSerializer

from mailbox_manager import enums, models
from mailbox_manager.api import permissions
from mailbox_manager.api.client import serializers
from mailbox_manager.exceptions import EmailAlreadyKnownException
from mailbox_manager.utils.dimail import DimailAPIClient


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
        - support_email: str
        Return newly created domain

    POST /api/<version>/mail-domains/<domain-slug>/fetch/
        Fetch domain status and expected config from dimail.
    """

    permission_classes = [
        permissions.DomainPermission,
        permissions.DomainResourcePermission,
    ]
    serializer_class = serializers.MailDomainSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "name"]
    ordering = ["-created_at"]
    lookup_field = "slug"
    queryset = models.MailDomain.objects.all()

    def get_queryset(self):
        """Restrict results to the current user's domain."""
        return self.queryset.filter(accesses__user=self.request.user)

    def perform_create(self, serializer):
        """Set the current user as owner of the newly created mail domain."""

        domain = serializer.save()
        serializers.MailDomainAccessSerializer().create(
            validated_data={
                "user": self.request.user,
                "domain": domain,
                "role": str(core_models.RoleChoices.OWNER),
            }
        )

    @action(detail=True, methods=["post"], url_path="fetch")
    def fetch_from_dimail(self, request, *args, **kwargs):
        """Fetch domain status and expected config from dimail."""
        domain = self.get_object()
        client = DimailAPIClient()
        client.fetch_domain_status(domain)
        client.fetch_domain_expected_config(domain)
        return Response(
            serializers.MailDomainSerializer(domain, context={"request": request}).data
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

    GET /api/v1.0/mail-domains/<domain_slug>/accesses/users/
        Return list of all users who can have an access to the domain

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

    permission_classes = [permissions.DomainResourcePermission]
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

    @action(detail=False, url_path="users", methods=["get"])
    def get_available_users(self, request, domain_slug):
        """API endpoint to search user to give them new access.
        More filters and permission will be added soon.
        """
        domain = models.MailDomain.objects.get(slug=domain_slug)
        abilities = domain.get_abilities(request.user)
        if not abilities["manage_accesses"]:
            raise exceptions.PermissionDenied()

        queryset = (
            core_models.User.objects.order_by("-created_at")
            # exclude inactive users and get users from identified user's organization
            .filter(is_active=True, organization_id=request.user.organization_id)
            # exclude all users with already an access config
            .exclude(mail_domain_accesses__domain__slug=domain_slug)
        )
        # Search by case-insensitive and accent-insensitive
        if query := request.GET.get("q", ""):
            queryset = queryset.filter(
                Q(name__unaccent__icontains=query) | Q(email__unaccent__icontains=query)
            )
        return Response(UserSerializer(queryset.all(), many=True).data)


class MailBoxViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
):
    """MailBox ViewSet

    GET /api/<version>/mail-domains/<domain_slug>/mailboxes/
        Return a list of mailboxes on the domain

    POST /api/<version>/mail-domains/<domain_slug>/mailboxes/ with expected data:
        - first_name: str
        - last_name: str
        - local_part: str
        - secondary_email: str (optional)
        Sends request to email provisioning API and returns newly created mailbox

    POST /api/<version>/mail-domains/<domain_slug>/mailboxes/<mailbox_id>/disable/
        Send a request to dimail to disable mailbox and change status of the mailbox in our DB

    POST /api/<version>/mail-domains/<domain_slug>/mailboxes/<mailbox_id>/enable/
        Send a request to dimail to enable mailbox and change status of the mailbox in our DB

    POST /api/<version>/mail-domains/<domain_slug>/mailboxes/<mailbox_id>/reset/
        Send a request to mail-provider to reset password.

    PUT /api/<version>/mail-domains/<domain_slug>/mailboxes/<mailbox_id>/
        Send a request to update mailbox. Cannot modify domain or local_part.

    PATCH /api/<version>/mail-domains/<domain_slug>/mailboxes/<mailbox_id>/
        Send a request to partially update mailbox. Cannot modify domain or local_part.
    """

    permission_classes = [permissions.DomainResourcePermission]
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

    def get_serializer_context(self):
        """Extra context provided to the serializer class."""
        context = super().get_serializer_context()
        context["domain_slug"] = self.kwargs["domain_slug"]
        return context

    def get_permissions(self):
        """Add a specific permission for domain viewers to update their own mailbox."""
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.DomainPermission]
        elif self.action in ["update", "partial_update"]:
            permission_classes = [
                permissions.DomainResourcePermission
                | permissions.IsMailboxOwnerPermission
            ]
        else:
            return super().get_permissions()

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Chooses list or detail serializer according to the action."""
        if self.action in {"update", "partial_update"}:
            return serializers.MailboxUpdateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create new mailbox."""
        domain_slug = self.kwargs.get("domain_slug", "")
        if domain_slug:
            serializer.validated_data["domain"] = models.MailDomain.objects.get(
                slug=domain_slug
            )
        super().perform_create(serializer)

    @action(detail=True, methods=["post"])
    def disable(self, request, domain_slug, pk=None):  # pylint: disable=unused-argument
        """Disable mailbox. Send a request to dimail and change status in our DB"""
        mailbox = self.get_object()
        client = DimailAPIClient()
        client.disable_mailbox(mailbox, request.user.sub)
        mailbox.status = enums.MailboxStatusChoices.DISABLED
        mailbox.save()
        return Response(serializers.MailboxSerializer(mailbox).data)

    @action(detail=True, methods=["post"])
    def enable(self, request, domain_slug, pk=None):  # pylint: disable=unused-argument
        """Enable mailbox. Send a request to dimail and change status in our DB"""
        mailbox = self.get_object()
        client = DimailAPIClient()
        client.enable_mailbox(mailbox, request.user.sub)
        mailbox.status = enums.MailboxStatusChoices.ENABLED
        mailbox.save()
        return Response(serializers.MailboxSerializer(mailbox).data)

    @action(detail=True, methods=["post"])
    def reset_password(self, request, domain_slug, pk=None):  # pylint: disable=unused-argument
        """Send a request to dimail to change password
        and email new password to mailbox's secondary email."""
        mailbox = self.get_object()
        dimail = DimailAPIClient()
        dimail.reset_password(mailbox)
        return Response(serializers.MailboxSerializer(mailbox).data)


class MailDomainInvitationViewset(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """API ViewSet for user invitations to domain management.

    GET /api/<version>/mail-domains/<domain_slug>/invitations/:<invitation_id>/
        Return list of invitations related to that domain or one
        domain access if an id is provided.

    POST /api/<version>/mail-domains/<domain_slug>/invitations/ with expected data:
        - email: str
        - role: str [owner|admin|member]
        - issuer : User, automatically added from user making query, if allowed
        - domain : Domain, automatically added from requested URI
        Return a newly created invitation
        or an access if email is already linked to an existing user

    PUT / PATCH : Not permitted. Instead of updating your invitation,
        delete and create a new one.

    DELETE /api/<version>/mail-domains/<domain_slug>/invitations/:<invitation_id>/
        Delete targeted invitation
    """

    lookup_field = "id"
    permission_classes = [permissions.DomainResourcePermission]
    queryset = (
        models.MailDomainInvitation.objects.all()
        .select_related("domain")
        .order_by("-created_at")
    )
    serializer_class = serializers.MailDomainInvitationSerializer

    def get_serializer_context(self):
        """Extra context provided to the serializer class."""
        context = super().get_serializer_context()
        context["domain_slug"] = self.kwargs["domain_slug"]
        return context

    def get_queryset(self):
        """Return the queryset according to the action."""
        queryset = super().get_queryset()
        queryset = queryset.filter(domain__slug=self.kwargs["domain_slug"])

        if self.action == "list":
            # Determine which role the logged-in user has in the domain
            user_role_query = models.MailDomainAccess.objects.filter(
                user=self.request.user, domain__slug=self.kwargs["domain_slug"]
            ).values("role")

            queryset = (
                # The logged-in user should be part of a domain to see its accesses
                queryset.filter(
                    domain__accesses__user=self.request.user,
                )
                # Abilities are computed based on logged-in user's role and
                # the user role on each domain access
                .annotate(user_role=Subquery(user_role_query))
                .distinct()
            )

        return queryset

    def create(self, request, *args, **kwargs):
        """Attempt to create invitation. If user is already registered,
        they don't need an invitation but an access, which we create here."""
        email = request.data["email"]
        try:
            return super().create(request, *args, **kwargs)
        except EmailAlreadyKnownException as exc:
            user = models.User.objects.get(email__iexact=email)

            models.MailDomainAccess.objects.create(
                user=user,
                domain=models.MailDomain.objects.get(slug=kwargs["domain_slug"]),
                role=request.data["role"],
            )
            raise exc


class AliasViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """API ViewSet for aliases.

    GET /api/<version>/mail-domains/<domain_slug>/aliases/
        Return list of aliases related to that domain

    POST /api/<version>/mail-domains/<domain_slug>/aliases/ with expected data:
        - local_part: str
        - destination: str
        Return a newly created alias

    DELETE /api/<version>/mail-domains/<domain_slug>/aliases/<alias_pk>/
        Delete targeted alias

    DELETE /api/<version>/mail-domains/<domain_slug>/aliases/?local_part=<local_part>/
        Delete all aliases of targeted local_part
    """

    lookup_field = "pk"
    permission_classes = [permissions.DomainResourcePermission]
    serializer_class = serializers.AliasSerializer
    queryset = models.Alias.objects.all().select_related("domain")
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["local_part"]
    ordering = ["local_part"]

    def get_serializer_context(self):
        """Extra context provided to the serializer class."""
        context = super().get_serializer_context()
        context["domain_slug"] = self.kwargs["domain_slug"]
        return context

    def get_queryset(self):
        """Return the queryset according to the action."""
        queryset = super().get_queryset()
        queryset = queryset.filter(domain__slug=self.kwargs["domain_slug"])

        if self.action == "list":
            # Determine which role the logged-in user has in the domain
            user_role_query = models.MailDomainAccess.objects.filter(
                user=self.request.user, domain__slug=self.kwargs["domain_slug"]
            ).values("role")

            queryset = (
                queryset
                # Abilities are computed based on logged-in user's role and
                # the user role on each domain access
                .annotate(user_role=Subquery(user_role_query)).distinct()
            )

        return queryset

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy method to delete specific alias and send request to dimail.
        """
        instance = self.get_object()
        self.perform_destroy(instance)

        client = DimailAPIClient()
        dimail_response = client.delete_alias(instance)

        if dimail_response.status_code == status.HTTP_404_NOT_FOUND:
            return Response(
                "Domain out of sync with mailbox provider, please contact our support.",
                status=status.HTTP_200_OK,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["DELETE"], detail=False)
    def delete(self, request, *args, **kwargs):
        """Bulk delete aliases. Filtering is required and accepted filter is local_part."""

        if "local_part" not in self.request.query_params:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        local_part = self.request.query_params["local_part"]
        queryset = self.get_queryset().filter(
            local_part=local_part
        )  # Manually call get_queryset to filter by domain and role
        if not queryset:
            raise Http404("No Alias matches the given query.")

        # view is bounded to a domain, fetch is from the queryset to spare a dedicated DB request"
        domain_name = queryset[0].domain.name
        queryset.delete()

        client = DimailAPIClient()
        client.delete_multiple_alias(local_part, domain_name)

        return Response(status=status.HTTP_204_NO_CONTENT)
