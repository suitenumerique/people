"""Test the `setup_dimail_db` management command"""

from django.contrib.auth import get_user_model
from django.core.management import call_command

import pytest
import responses

from mailbox_manager import factories as mailbox_factories
from mailbox_manager.management.commands.setup_dimail_db import DIMAIL_URL, admin

pytestmark = pytest.mark.django_db

admin_auth = (admin["username"], admin["password"])
User = get_user_model()


@responses.activate
def test_commands_setup_dimail_db(settings):
    """The create_demo management command should create objects as expected."""
    settings.DEBUG = True  # required to run the command

    # mock dimail API
    responses.post(f"{DIMAIL_URL}/users/", status=201)
    responses.post(f"{DIMAIL_URL}/domains/", status=201)
    responses.get(
        f"{DIMAIL_URL}/users/",
        json=[
            {
                "is_admin": True,
                "name": "admin",
                "perms": [],
            },
            {
                "is_admin": False,
                "name": "la_regie",
                "perms": [
                    "new_domain",
                    "create_users",
                    "manage_users",
                ],
            },
        ],
    )

    call_command("setup_dimail_db")

    # check dimail API received the expected requests
    assert len(responses.calls) == 2
    assert responses.calls[0].request.url == f"{DIMAIL_URL}/users/"
    assert (
        responses.calls[0].request.body
        == b'{"name": "admin", "password": "admin", "is_admin": true, "perms": []}'
    )

    assert responses.calls[1].request.url == f"{DIMAIL_URL}/users/"
    assert responses.calls[1].request.body == (
        b'{"name": "la_regie", "password": "password", "is_admin": false, '
        b'"perms": ["new_domain", "create_users", "manage_users"]}'
    )

    # reset the responses counter
    responses.calls.reset()  # pylint: disable=no-member

    # check the command with "populate-from-people" option
    mailbox_factories.MailDomainAccessFactory(
        domain__name="some.domain.com", user__sub="sub.toto.123"
    )

    call_command("setup_dimail_db", "--populate-from-people")

    # check dimail API received the expected requests
    assert len(responses.calls) == 3  # calls for some.domain.com and test.domain.com

    dimail_calls = []
    for call in responses.calls[3:]:
        dimail_calls.append((call.request.url, call.request.body))

    assert responses.calls[2].request.body == (
        b'{"name": "some.domain.com", "context_name": "some.domain.com", '
        b'"features": ["webmail", "mailbox", "alias"], '
        b'"delivery": "virtual"}'
    )
