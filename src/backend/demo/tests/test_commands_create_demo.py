"""Test the `create_demo` management command"""

from unittest import mock

from django.conf import settings
from django.core.management import call_command

import pytest

from core import models

from demo import defaults
from mailbox_manager import models as mailbox_models

pytestmark = pytest.mark.django_db


TEST_NB_OBJECTS = {
    "users": 100,
    "teams": 100,
    "max_users_per_team": 5,
    "domains": 10,
    "mailboxes_per_domain": 2,
    "aliases_per_domain": 2,
}


@mock.patch.dict(defaults.NB_OBJECTS, TEST_NB_OBJECTS)
def test_commands_create_demo():
    """The create_demo management command should create objects as expected."""
    settings.DEBUG = True

    call_command("create_demo")

    # Monique Test, Jeanne Test and Jean Something (quick fix for e2e)
    # 3 users with team rights
    # 3 users with domain rights
    # 3 x 3 user with both rights
    assert models.User.objects.count() == TEST_NB_OBJECTS["users"] + 3 + 3 + 3 + 9

    assert models.Team.objects.count() == TEST_NB_OBJECTS["teams"]
    assert models.TeamAccess.objects.count() >= TEST_NB_OBJECTS["teams"]

    # nb_domains + enabled + many-boxed-domain
    assert (
        mailbox_models.MailDomain.objects.count() == TEST_NB_OBJECTS["domains"] + 1 + 1
    )

    # 3 x 3 domain access for E2E group users
    # + 3 domain accesses for E2E domain-only users
    # + 2 domains for E2E mail owner user
    assert (
        mailbox_models.MailDomainAccess.objects.count()
        == TEST_NB_OBJECTS["domains"] + 3 + 9 + 2
    )

    # TEST_NB_OBJECTS["domains"]*TEST_NB_OBJECTS["mailboxes_per_domain"] = 20
    # + 30 in the many-object-domain
    assert mailbox_models.Mailbox.objects.count() == 50

    # TEST_NB_OBJECTS["domains"]*TEST_NB_OBJECTS["mailboxes_per_alias"] = 20
    # + 30 in the many-object-domain
    assert mailbox_models.Alias.objects.count() == 50


def test_commands_createsuperuser():
    """
    The createsuperuser management command should create a user
    with superuser permissions.
    """

    call_command("createsuperuser", username="admin", password="admin")

    assert models.User.objects.count() == 1
    user = models.User.objects.get()
    assert user.sub == "admin"
