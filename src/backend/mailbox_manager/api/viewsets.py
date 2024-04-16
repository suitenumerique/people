"""API endpoints"""

from rest_framework import mixins, viewsets
from rest_framework import permissions as drf_permissions

from mailbox_manager import models

from . import serializers


class MailDomainViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """MailDomain ViewSet"""

    permission_classes = [drf_permissions.IsAuthenticated]
    serializer_class = serializers.MailDomainSerializer
    queryset = models.MailDomain.objects.all()


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
        domain_id = self.kwargs.get("domain_id", "")
        if domain_id:
            return self.queryset.filter(domain__id=domain_id)
        return self.queryset

    def perform_create(self, serializer):
        """Create new mailbox."""
        domain_id = self.kwargs.get("domain_id", "")
        if domain_id:
            serializer.validated_data["domain"] = models.MailDomain.objects.get(
                id=domain_id
            )
        super().perform_create(serializer)
