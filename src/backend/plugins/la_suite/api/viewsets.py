"""API viewsets for La Suite plugin."""

from functools import reduce
from operator import iconcat

from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response

from core.authentication.backends import AccountServiceAuthentication
from core.models import Organization

from mailbox_manager.models import Mailbox
from mailbox_manager.utils.dimail import DimailAPIClient
from plugins.la_suite.authentication import OrganizationOneTimeTokenAuthentication

from .serializers import OrganizationActivationSerializer
from .throttle import OrganizationTokenAnonRateThrottle


class ScopeAPIPermission(BasePermission):
    """Permission to check if the user has the correct scope."""

    def has_permission(self, request, view):
        """Check if the user has the correct scope."""
        if not request.auth:
            return False
        return view.scope in request.user.scopes


class ActiveOrganizationsSiret(viewsets.GenericViewSet, ListModelMixin):
    """
    ViewSet to list all SIRET of active communes.

    * Requires API key authentication.
    * Only services with the correct scope are able to access this view.
    """

    authentication_classes = [AccountServiceAuthentication]
    permission_classes = [ScopeAPIPermission]
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
        registration_ids = reduce(iconcat, registration_ids_lists, [])

        return Response(registration_ids)


class OrganizationActivation(viewsets.ViewSet):
    """ViewSet to activate an organization.

    Activate organization and create a mailbox for the first user.
    Endpoint: POST /la-suite/v1.0/activate-organization/
    """

    authentication_classes = [OrganizationOneTimeTokenAuthentication]
    throttle_classes = [OrganizationTokenAnonRateThrottle]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="activate-organization")
    def activate_organization(self, request):
        """Activate the organization by creating the first user.

        Args:
            request: The HTTP request object

        Returns:
            Response: Success message with 201 status code

        Raises:
            ValidationError: If request data is invalid
            MailDomain.DoesNotExist: If organization has no mail domain
        """
        organization = request.user

        serializer = OrganizationActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        domain = organization.mail_domains.get()  # should fail on purpose

        mailbox_data = {
            "first_name": serializer.data["first_name"],
            "last_name": serializer.data["last_name"],
            "local_part": serializer.data["email_local_part"],
            "domain": domain,
            "password": make_password(request.data["password"]),
        }

        with transaction.atomic():
            # Create the first mailbox which will allow the user to log in
            mailbox = Mailbox.objects.create(**mailbox_data)

            # send new mailbox request to dimail
            client = DimailAPIClient()
            client.create_mailbox(mailbox)

            # Enable the organization
            organization.is_active = True
            organization.save(update_fields=["is_active", "updated_at"])

            # Disable the one-time token
            token = self.request.auth
            token.enabled = False
            token.used_at = timezone.now()
            token.save(update_fields=["enabled", "used_at"])

        return Response(
            status=status.HTTP_201_CREATED,
            data={"message": "Organization activated. First user created."},
        )
