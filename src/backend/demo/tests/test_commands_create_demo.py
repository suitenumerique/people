"""Test the `create_demo` management command"""

from unittest import mock

from django.core.management import call_command
from django.test import override_settings

import pytest

from core import models

from demo import defaults

TEST_NB_OBJECTS = {
    "users": 5,
    "teams": 3,
    "max_identities_per_user": 3,
    "max_users_per_team": 5,
}

pytestmark = pytest.mark.django_db


@override_settings(DEBUG=True)
@mock.patch.dict(defaults.NB_OBJECTS, TEST_NB_OBJECTS)
def test_commands_create_demo():
    """The create_demo management command should create objects as expected."""
    call_command("create_demo")

    assert models.User.objects.count() == 5
    assert models.Identity.objects.exists()
    assert models.Team.objects.count() == 3
    assert models.TeamAccess.objects.count() >= 3


def test_commands_createsuperuser():
    """
    The createsuperuser management command should create a user
    with superuser permissions.
    """

    call_command("createsuperuser")

    assert models.User.objects.count() == 1
