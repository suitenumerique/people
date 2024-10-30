"""Test the `create_demo` management command"""

from unittest import mock

from django.core.management import call_command
from django.test import override_settings

import pytest

from core import models

from demo import defaults
from mailbox_manager import models as mailbox_models

TEST_NB_OBJECTS = {
    "users": 5,
    "teams": 3,
    "max_users_per_team": 5,
    "domains": 2,
}

pytestmark = pytest.mark.django_db


@override_settings(DEBUG=True)
@mock.patch.dict(defaults.NB_OBJECTS, TEST_NB_OBJECTS)
def test_commands_create_demo():
    """The create_demo management command should create objects as expected."""
    call_command("create_demo")

    assert (
        models.User.objects.count() == TEST_NB_OBJECTS["users"] + 3
    )  # Monique Test, Jeanne Test and Jean Something (quick fix for e2e)
    assert models.Team.objects.count() == TEST_NB_OBJECTS["teams"]
    assert models.TeamAccess.objects.count() >= TEST_NB_OBJECTS["teams"]
    assert mailbox_models.MailDomain.objects.count() == TEST_NB_OBJECTS["domains"]
    assert mailbox_models.MailDomainAccess.objects.count() == TEST_NB_OBJECTS["domains"]


def test_commands_createsuperuser():
    """
    The createsuperuser management command should create a user
    with superuser permissions.
    """

    call_command("createsuperuser", username="admin", password="admin")

    assert models.User.objects.count() == 1
    user = models.User.objects.get()
    assert user.sub == "admin"
