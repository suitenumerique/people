"""Authentication backends for the token exchanges API endpoints."""

from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import AuthenticationFailed

from . import models


class ServiceProviderBasicAuthentication(BasicAuthentication):
    """
    Authentication backend for the token exchanges API endpoints.

    A Service Provider can authenticate to have access to the endpoints.
    """

    www_authenticate_realm = "token-exchange"

    def authenticate_credentials(self, client_id, client_secret, request=None):
        """
        Authenticate a service provider.
        """
        if client_id is None or client_secret is None:
            raise AuthenticationFailed("No credentials provided.")

        try:
            credentials = models.ServiceProviderCredentials.objects.select_related(
                "service_provider"
            ).get(
                client_id=client_id,
                client_secret=client_secret,
            )
        except models.ServiceProviderCredentials.DoesNotExist as exc:
            raise AuthenticationFailed("Service provider does not exist.") from exc

        if not credentials.is_active:
            raise AuthenticationFailed("Service provider inactive or deleted.")

        credentials.service_provider.is_authenticated = True

        return (credentials.service_provider, None)
