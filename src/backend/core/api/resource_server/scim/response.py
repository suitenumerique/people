"""SCIM API response classes."""

from rest_framework.response import Response


class ScimJsonResponse(Response):
    """
    Custom JSON response class for SCIM API.

    This class sets the content type to "application/json+scim" for SCIM
    responses.
    """

    def __init__(self, *args, **kwargs):
        """JSON response with enforced SCIM content type."""
        super().__init__(*args, content_type="application/json+scim", **kwargs)
