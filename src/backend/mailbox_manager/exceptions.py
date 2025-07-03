"""
Custom exceptions for mailbox manager app
"""

from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import APIException


class EmailAlreadyKnownException(APIException):
    """Exception raised when trying to create a user with an already existing email address."""

    status_code = status.HTTP_201_CREATED
    default_detail = _(
        "Email already known. Invitation not sent but access created instead."
    )
    default_code = "email already known"
