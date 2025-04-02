"""Authentication Backends for the People core app."""

import logging

from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.utils.translation import gettext_lazy as _

from lasuite.oidc_login.backends import (
    OIDCAuthenticationBackend as LaSuiteOIDCAuthenticationBackend,
)
from lasuite.tools.email import get_domain_from_email
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from core.models import (
    AccountService,
    Contact,
    Organization,
    OrganizationAccess,
    OrganizationRoleChoices,
)

logger = logging.getLogger(__name__)


class OIDCAuthenticationBackend(LaSuiteOIDCAuthenticationBackend):
    """Custom OpenID Connect (OIDC) Authentication Backend.

    This class overrides the default OIDC Authentication Backend to accommodate differences
    in the User model, and handles signed and/or encrypted UserInfo response.
    """

    def get_extra_claims(self, user_info):
        """
        Return extra claims from user_info.

        Args:
          user_info (dict): The user information dictionary.

        Returns:
          dict: A dictionary of extra claims.

        """
        extra_claims = super().get_extra_claims(user_info)
        if settings.OIDC_ORGANIZATION_REGISTRATION_ID_FIELD:
            extra_claims[settings.OIDC_ORGANIZATION_REGISTRATION_ID_FIELD] = (
                user_info.get(settings.OIDC_ORGANIZATION_REGISTRATION_ID_FIELD)
            )
        return extra_claims

    def post_get_or_create_user(self, user, claims):
        """
        Post-processing after user creation or retrieval.

        Args:
          user (User): The user instance.
          claims (dict): The claims dictionary.

        Returns:
        - None

        """
        # Data cleaning, to be removed when user organization is null=False
        # or all users have an organization.
        # See https://github.com/suitenumerique/people/issues/504
        if not user.organization_id:
            organization_registration_id = claims.get(
                settings.OIDC_ORGANIZATION_REGISTRATION_ID_FIELD
            )
            domain = get_domain_from_email(claims["email"])
            try:
                organization, organization_created = (
                    Organization.objects.get_or_create_from_user_claims(
                        registration_id=organization_registration_id,
                        domain=domain,
                    )
                )
                if organization_created:
                    logger.info("Organization %s created", organization)
                    # For this case, we don't create an OrganizationAccess we will
                    # manage this manually later, because we don't want the first
                    # user who log in after the release to be the admin of their
                    # organization. We will keep organization without admin, and
                    # we will have to manually clean things up (while there is
                    # not that much organization in the database).
            except ValueError as exc:
                # Raised when there is no recognizable organization
                # identifier (domain or registration_id)
                logger.warning("Unable to update user organization: %s", exc)
            else:
                user.organization = organization
                user.save()
                logger.info(
                    "User %s updated with organization %s", user.pk, organization
                )

    def create_user(self, claims):
        """Return a newly created User instance."""
        sub = claims.get("sub")
        if sub is None:
            raise SuspiciousOperation(
                _("Claims contained no recognizable user identification")
            )
        email = claims.get("email")
        name = claims.get("name")

        # Extract or create the organization from the data
        organization_registration_id = claims.pop(
            settings.OIDC_ORGANIZATION_REGISTRATION_ID_FIELD,
            None,
        )
        domain = get_domain_from_email(email)
        try:
            organization, organization_created = (
                Organization.objects.get_or_create_from_user_claims(
                    registration_id=organization_registration_id,
                    domain=domain,
                )
            )
        except ValueError as exc:
            raise SuspiciousOperation(
                _("Claims contained no recognizable organization identification")
            ) from exc

        if organization_created:
            logger.info("Organization %s created", organization)

        logger.info("Creating user %s / %s", sub, email)

        user = super().create_user(claims | {"organization": organization})

        if organization_created:
            # Warning: we may remove this behavior in the near future when we
            # add a feature to claim the organization ownership.
            OrganizationAccess.objects.create(
                organization=organization,
                user=user,
                role=OrganizationRoleChoices.ADMIN,
            )

        # Initiate the user's profile
        Contact.objects.create(
            owner=user,
            user=user,
            full_name=name or email,
            data={
                "emails": [
                    {"type": "Work", "value": email},
                ],
            },
        )

        return user


class AccountServiceAuthentication(BaseAuthentication):
    """Authentication backend for account services using Authorization header.
    The Authorization header is used to authenticate the request.
    The api key is stored in the AccountService model.

    Header format:
        Authorization: ApiKey <api_key>
    """

    def authenticate(self, request):
        """Authenticate the request. Find the account service and check the api key.

        Should return either:
        - a tuple of (account_service, api_key) if allowed,
        - None to pass on other authentication backends
        - raise an AuthenticationFailed exception to stop propagation.
        """
        auth_header = request.headers.get("Authorization", "")
        if not auth_header:
            return None
        try:
            auth_mode, api_key = auth_header.split(" ")
        except (IndexError, ValueError) as err:
            raise AuthenticationFailed(_("Invalid authorization header.")) from err
        if auth_mode.lower() != "apikey" or not api_key:
            raise AuthenticationFailed(_("Invalid authorization header."))
        try:
            account_service = AccountService.objects.get(api_key=api_key)
        except AccountService.DoesNotExist as err:
            logger.warning("Invalid api_key: %s", api_key)
            raise AuthenticationFailed(_("Invalid api key.")) from err
        return (account_service, account_service.api_key)

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return "apikey"
