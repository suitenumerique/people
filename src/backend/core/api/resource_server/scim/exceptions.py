"""Exceptions for SCIM API."""

from django.conf import settings

from core.api.resource_server.scim.response import ScimJsonResponse


def scim_exception_handler(exc, _context):
    """Handle SCIM exceptions and return them in the correct format."""
    data = {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
        "status": str(exc.status_code),
        "detail": str(exc.detail) if settings.DEBUG else "",
    }

    return ScimJsonResponse(data, status=exc.status_code)
