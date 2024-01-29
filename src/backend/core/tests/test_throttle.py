"""
Test Throttle in People's app.
"""
import pytest
from rest_framework.test import APIClient

from core import factories

from people.settings import REST_FRAMEWORK  # pylint: disable=E0611

from .utils import OIDCToken

pytestmark = pytest.mark.django_db


def test_throttle():
    """
    Throttle protection should block requests if too many.
    """
    identity = factories.IdentityFactory()
    user = identity.user
    jwt_token = OIDCToken.for_user(user)

    client = APIClient()
    endpoint = "/api/v1.0/users/"

    # loop to activate throttle protection
    throttle_limit = int(
        REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["burst"].replace("/minute", "")
    )
    for _ in range(0, throttle_limit):
        client.get(endpoint, HTTP_AUTHORIZATION=f"Bearer {jwt_token}")

    # this call should err
    response = client.get(endpoint, HTTP_AUTHORIZATION=f"Bearer {jwt_token}")
    assert response.status_code == 429  # too many requests
