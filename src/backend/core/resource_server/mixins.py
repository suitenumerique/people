"""
Mixins for resource server views.
"""

from rest_framework import exceptions as drf_exceptions

from .authentication import ResourceServerAuthentication


class ResourceServerMixin:
    """
    Mixin for resource server views:
     - Restrict the authentication class to ResourceServerAuthentication.
     - Adds the Service Provider ID to the serializer context.
     - Fetch the Service Provider ID from the OIDC introspected token stored
       in the request.

    This Mixin *must* be used in every view that should act as a resource server.
    """

    authentication_classes = [ResourceServerAuthentication]

    def get_serializer_context(self):
        """Extra context provided to the serializer class."""
        context = super().get_serializer_context()

        # When used as a resource server, we need to know the audience to automatically:
        # - add the Service Provider to the team "scope" on creation
        context["from_service_provider_audience"] = (
            self._get_service_provider_audience()
        )

        return context

    def _get_service_provider_audience(self):
        """Return the audience of the Service Provider from the OIDC introspected token."""
        if not isinstance(
            self.request.successful_authenticator, ResourceServerAuthentication
        ):
            # We could check request.resource_server_token_audience here, but it's
            # more explicit to check the authenticator type and assert the attribute
            # existence.
            return None

        # When used as a resource server, the request has a token audience
        service_provider_audience = self.request.resource_server_token_audience

        if not service_provider_audience:  # should not happen
            raise drf_exceptions.AuthenticationFailed(
                "Resource server token audience not found in request"
            )

        return service_provider_audience
