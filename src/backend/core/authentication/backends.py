"""Authentication Backends for the People core app."""

import logging
from email.headerregistry import Address
from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import SuspiciousOperation
from django.utils.translation import gettext_lazy as _

import requests
from mozilla_django_oidc.auth import (
    OIDCAuthenticationBackend as MozillaOIDCAuthenticationBackend,
)

from core.models import (
    Contact,
    Organization,
    OrganizationAccess,
    OrganizationRoleChoices,
)

logger = logging.getLogger(__name__)

User = get_user_model()


def get_domain_from_email(email: Optional[str]) -> Optional[str]:
    """Extract domain from email."""
    try:
        return Address(addr_spec=email).domain
    except (ValueError, AttributeError):
        return None


class OIDCAuthenticationBackend(MozillaOIDCAuthenticationBackend):
    """Custom OpenID Connect (OIDC) Authentication Backend.

    This class overrides the default OIDC Authentication Backend to accommodate differences
    in the User model, and handles signed and/or encrypted UserInfo response.
    """

    def get_userinfo(self, access_token, id_token, payload):
        """Return user details dictionary.

        Parameters:
        - access_token (str): The access token.
        - id_token (str): The id token (unused).
        - payload (dict): The token payload (unused).

        Note: The id_token and payload parameters are unused in this implementation,
        but were kept to preserve base method signature.

        Note: It handles signed and/or encrypted UserInfo Response. It is required by
        Agent Connect, which follows the OIDC standard. It forces us to override the
        base method, which deal with 'application/json' response.

        Returns:
        - dict: User details dictionary obtained from the OpenID Connect user endpoint.
        """

        user_response = requests.get(
            self.OIDC_OP_USER_ENDPOINT,
            headers={"Authorization": f"Bearer {access_token}"},
            verify=self.get_settings("OIDC_VERIFY_SSL", True),
            timeout=self.get_settings("OIDC_TIMEOUT", None),
            proxies=self.get_settings("OIDC_PROXY", None),
        )
        user_response.raise_for_status()
        userinfo = self.verify_token(user_response.text)
        return userinfo

    def get_or_create_user(self, access_token, id_token, payload):
        """Return a User based on userinfo. Create a new user if no match is found.

        Parameters:
        - access_token (str): The access token.
        - id_token (str): The ID token.
        - payload (dict): The user payload.

        Returns:
        - User: An existing or newly created User instance.

        Raises:
        - Exception: Raised when user creation is not allowed and no existing user is found.
        """

        user_info = self.get_userinfo(access_token, id_token, payload)

        sub = user_info.get("sub")
        if not sub:
            raise SuspiciousOperation(
                _("User info contained no recognizable user identification")
            )

        # Get user's full name from OIDC fields defined in settings
        full_name = self.compute_full_name(user_info)
        email = user_info.get("email")

        claims = {
            "sub": sub,
            "email": email,
            "name": full_name,
        }
        if settings.OIDC_ORGANIZATION_REGISTRATION_ID_FIELD:
            claims[settings.OIDC_ORGANIZATION_REGISTRATION_ID_FIELD] = user_info.get(
                settings.OIDC_ORGANIZATION_REGISTRATION_ID_FIELD
            )

        # if sub is absent, try matching on email
        user = self.get_existing_user(sub, email)

        if user:
            if not user.is_active:
                raise SuspiciousOperation(_("User account is disabled"))
            self.update_user_if_needed(user, claims)
        elif self.get_settings("OIDC_CREATE_USER", True):
            user = self.create_user(claims)

        # Data cleaning, to be removed when user organization is null=False
        # or all users have an organization.
        # See https://github.com/suitenumerique/people/issues/504
        if not user.organization_id:
            organization_registration_id = claims.get(
                settings.OIDC_ORGANIZATION_REGISTRATION_ID_FIELD
            )
            domain = get_domain_from_email(email)
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

        return user

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
        organization_registration_id = claims.get(
            settings.OIDC_ORGANIZATION_REGISTRATION_ID_FIELD
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

        user = self.UserModel.objects.create(
            organization=organization,
            password="!",  # noqa: S106
            sub=sub,
            email=email,
            name=name,
        )
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

    def compute_full_name(self, user_info):
        """Compute user's full name based on OIDC fields in settings."""
        name_fields = settings.USER_OIDC_FIELDS_TO_NAME
        full_name = " ".join(
            user_info[field] for field in name_fields if user_info.get(field)
        )
        return full_name or None

    def get_existing_user(self, sub, email):
        """Fetch existing user by sub or email."""
        try:
            return User.objects.get(sub=sub)
        except User.DoesNotExist:
            if email and settings.OIDC_FALLBACK_TO_EMAIL_FOR_IDENTIFICATION:
                try:
                    return User.objects.get(email=email)
                except User.DoesNotExist:
                    pass
        return None

    def update_user_if_needed(self, user, claims):
        """Update user claims if they have changed."""
        updated_claims = {}
        for key in ["email", "name"]:
            claim_value = claims.get(key)
            if claim_value and claim_value != getattr(user, key):
                updated_claims[key] = claim_value

        if updated_claims:
            self.UserModel.objects.filter(sub=user.sub).update(**updated_claims)
