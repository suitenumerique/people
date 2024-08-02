"""API endpoints"""

from rest_framework import filters, mixins, viewsets
from rest_framework import permissions as drf_permissions

from core import models as core_models

from mailbox_manager import models
from mailbox_manager.api import permissions, serializers


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
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    MailDomainAccess viewset.
    """

    permission_classes = [drf_permissions.IsAuthenticated]
    serializer_class = serializers.MailDomainAccessSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "user", "domain", "role"]
    ordering = ["-created_at"]
    queryset = models.MailDomainAccess.objects.all()


class MailBoxViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """MailBox ViewSet"""

    permission_classes = [drf_permissions.IsAuthenticated]
    serializer_class = serializers.MailboxSerializer
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
