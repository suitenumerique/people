from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from mailbox_manager.models import Mailbox, MailDomain
from .authentication import OrganizationOneTimeTokenAuthentication
from .serializers import OrganizationActivationSerializer
from .throttle import OrganizationTokenAnonRateThrottle


class OrganizationActivationViewSet(viewsets.ViewSet):
    authentication_classes = [OrganizationOneTimeTokenAuthentication]
    throttle_classes = [OrganizationTokenAnonRateThrottle]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='activate-organization')
    def activate_organization(self, request):
        """Activate the organization by creating the first user."""
        organization = request.user

        serializer = OrganizationActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        domain = organization.mail_domains.get()  # should fail on purpose

        with transaction.atomic():
            # Create the first mailbox which will allow the user to log in
            # Enable the organization
            # Disable the one-time token
            mailbox = Mailbox.objects.create(
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
                local_part=serializer.validated_data['email_local_part'],
                is_active=True,
                domain=domain,
            )
            mailbox.set_password(serializer.validated_data['password'])
            mailbox.save()

            # XXX: CALL DIMAIL API TO CREATE THE MAILBOX AND ENABLE IT

            organization.is_active = True
            organization.save(update_fields=['is_active', "updated_at"])

            token = self.request.auth
            token.enabled = False
            token.used_at = timezone.now()
            token.save(update_fields=['enabled', 'used_at'])

        return Response(status=status.HTTP_201_CREATED, data={'message': 'Organization activated.'})
