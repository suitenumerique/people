"""Resource Server views"""

from django.core.exceptions import ImproperlyConfigured

from joserfc.jwk import KeySet
from rest_framework.response import Response
from rest_framework.views import APIView

from . import utils


class JWKSView(APIView):
    """
    API endpoint for retrieving a JSON Web Keys Set (JWKS).

    Returns:
        Response: JSON response containing the JWKS data.
    """

    authentication_classes = []  # disable authentication
    permission_classes = []  # disable permission

    def get(self, request):
        """Handle GET requests to retrieve JSON Web Keys Set (JWKS).

        Returns:
            Response: JSON response containing the JWKS data.
        """

        try:
            private_key = utils.import_private_key_from_settings()
        except (ImproperlyConfigured, ValueError) as err:
            return Response({"error": str(err)}, status=500)

        try:
            jwk = KeySet([private_key]).as_dict(private=False)
        except (TypeError, ValueError, AttributeError):
            return Response({"error": "Could not load key"}, status=500)

        return Response(jwk)
