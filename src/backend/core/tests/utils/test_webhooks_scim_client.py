"""Test Team synchronization webhooks."""

import json
import random
import re
from logging import Logger
from unittest import mock

import pytest
import responses

from core import factories
from core.utils.webhooks import scim_synchronizer

pytestmark = pytest.mark.django_db


def test_utils_webhooks_add_user_to_group_no_webhooks():
    """If no webhook is declared on the team, the function should not make any request."""
    access = factories.TeamAccessFactory()

    with responses.RequestsMock():
        scim_synchronizer.add_user_to_group(access.team, access.user)

    assert len(responses.calls) == 0


@mock.patch.object(Logger, "info")
def test_utils_webhooks_add_user_to_group_success(mock_info):
    """The user passed to the function should get added."""
    user = factories.UserFactory()
    access = factories.TeamAccessFactory(user=user)
    webhooks = factories.TeamWebhookFactory.create_batch(2, team=access.team)

    with responses.RequestsMock() as rsps:
        # Ensure successful response by scim provider using "responses":
        rsps.add(
            rsps.PATCH,
            re.compile(r".*/Groups/.*"),
            body="{}",
            status=200,
            content_type="application/json",
        )

        scim_synchronizer.add_user_to_group(access.team, access.user)

        for i, webhook in enumerate(webhooks):
            assert rsps.calls[i].request.url == webhook.url

            # Check headers
            headers = rsps.calls[i].request.headers
            assert "Authorization" not in headers
            assert headers["Content-Type"] == "application/json"

        # Payload sent to scim provider
        for call in rsps.calls:
            payload = json.loads(call.request.body)
            assert payload == {
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
                "Operations": [
                    {
                        "op": "add",
                        "path": "members",
                        "value": [
                            {
                                "value": str(access.user.id),
                                "email": user.email,
                                "type": "User",
                            }
                        ],
                    }
                ],
            }

    # Logger
    for webhook in webhooks:
        expected_messages = {
            (
                "%s synchronization succeeded with %s",
                "add_user_to_group",
                webhook.url,
            )
        }
        actual_messages = {args for args, _ in mock_info.call_args_list}
        assert expected_messages.issubset(actual_messages)

    # Status
    for webhook in webhooks:
        webhook.refresh_from_db()
        assert webhook.status == "success"


@mock.patch.object(Logger, "info")
def test_utils_webhooks_remove_user_from_group_success(mock_info):
    """The user passed to the function should get removed."""
    user = factories.UserFactory()
    access = factories.TeamAccessFactory(user=user)
    webhooks = factories.TeamWebhookFactory.create_batch(2, team=access.team)

    with responses.RequestsMock() as rsps:
        # Ensure successful response by scim provider using "responses":
        rsps.add(
            rsps.PATCH,
            re.compile(r".*/Groups/.*"),
            body="{}",
            status=200,
            content_type="application/json",
        )

        scim_synchronizer.remove_user_from_group(access.team, access.user)

        for i, webhook in enumerate(webhooks):
            assert rsps.calls[i].request.url == webhook.url

        # Payload sent to scim provider
        for call in rsps.calls:
            payload = json.loads(call.request.body)
            assert payload == {
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
                "Operations": [
                    {
                        "op": "remove",
                        "path": "members",
                        "value": [
                            {
                                "value": str(access.user.id),
                                "email": user.email,
                                "type": "User",
                            }
                        ],
                    }
                ],
            }

    # Logger
    for webhook in webhooks:
        expected_messages = {
            (
                "%s synchronization succeeded with %s",
                "remove_user_from_group",
                webhook.url,
            )
        }
        actual_messages = {args for args, _ in mock_info.call_args_list}
        assert expected_messages.issubset(actual_messages)

    # Status
    for webhook in webhooks:
        webhook.refresh_from_db()
        assert webhook.status == "success"


@mock.patch.object(Logger, "error")
def test_utils_webhooks_add_user_to_group_failure(mock_error):
    """The logger should be called on webhook call failure."""
    user = factories.UserFactory()
    access = factories.TeamAccessFactory(user=user)
    webhooks = factories.TeamWebhookFactory.create_batch(2, team=access.team)

    with responses.RequestsMock() as rsps:
        # Simulate webhook failure using "responses":
        rsps.add(
            rsps.PATCH,
            re.compile(r".*/Groups/.*"),
            body="{}",
            status=random.choice([404, 301, 302]),
            content_type="application/json",
        )

        scim_synchronizer.add_user_to_group(access.team, access.user)

        for i, webhook in enumerate(webhooks):
            assert rsps.calls[i].request.url == webhook.url

        # Payload sent to scim provider
        for call in rsps.calls:
            payload = json.loads(call.request.body)
            assert payload == {
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
                "Operations": [
                    {
                        "op": "add",
                        "path": "members",
                        "value": [
                            {
                                "value": str(access.user.id),
                                "email": user.email,
                                "type": "User",
                            }
                        ],
                    }
                ],
            }

    # Logger
    for webhook in webhooks:
        expected_messages = {
            (
                "%s synchronization failed with %s",
                "add_user_to_group",
                webhook.url,
            )
        }
        actual_messages = {args for args, _ in mock_error.call_args_list}
        assert expected_messages.issubset(actual_messages)

    # Status
    for webhook in webhooks:
        webhook.refresh_from_db()
        assert webhook.status == "failure"


@mock.patch.object(Logger, "error")
@mock.patch.object(Logger, "info")
def test_utils_webhooks_add_user_to_group_retries(mock_info, mock_error):
    """webhooks synchronization supports retries."""
    user = factories.UserFactory()
    access = factories.TeamAccessFactory(user=user)
    webhook = factories.TeamWebhookFactory(team=access.team)

    url = re.compile(r".*/Groups/.*")
    with responses.RequestsMock() as rsps:
        # Make webhook fail 3 times before succeeding using "responses"
        all_rsps = [
            rsps.add(rsps.PATCH, url, status=500, content_type="application/json"),
            rsps.add(rsps.PATCH, url, status=500, content_type="application/json"),
            rsps.add(rsps.PATCH, url, status=500, content_type="application/json"),
            rsps.add(rsps.PATCH, url, status=200, content_type="application/json"),
        ]

        scim_synchronizer.add_user_to_group(access.team, access.user)

        for i in range(4):
            assert all_rsps[i].call_count == 1
            assert rsps.calls[i].request.url == webhook.url
            payload = json.loads(rsps.calls[i].request.body)
            assert payload == {
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
                "Operations": [
                    {
                        "op": "add",
                        "path": "members",
                        "value": [
                            {
                                "value": str(access.user.id),
                                "email": user.email,
                                "type": "User",
                            }
                        ],
                    }
                ],
            }

    # Logger
    assert not mock_error.called
    expected_messages = {
        (
            "%s synchronization succeeded with %s",
            "add_user_to_group",
            webhook.url,
        )
    }
    actual_messages = {args for args, _ in mock_info.call_args_list}
    assert expected_messages.issubset(actual_messages)

    # Status
    webhook.refresh_from_db()
    assert webhook.status == "success"


@mock.patch.object(Logger, "error")
def test_utils_synchronize_course_runs_max_retries_exceeded(mock_error):
    """Webhooks synchronization has exceeded max retries and should get logged."""
    user = factories.UserFactory()
    access = factories.TeamAccessFactory(user=user)
    webhook = factories.TeamWebhookFactory(team=access.team)

    with responses.RequestsMock() as rsps:
        # Simulate webhook temporary failure using "responses":
        rsp = rsps.add(
            rsps.PATCH,
            re.compile(r".*/Groups/.*"),
            body="{}",
            status=random.choice([500, 502]),
            content_type="application/json",
        )

        scim_synchronizer.add_user_to_group(access.team, access.user)

        assert rsp.call_count == 5
        assert rsps.calls[0].request.url == webhook.url
        payload = json.loads(rsps.calls[0].request.body)
        assert payload == {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
            "Operations": [
                {
                    "op": "add",
                    "path": "members",
                    "value": [
                        {
                            "value": str(access.user.id),
                            "email": user.email,
                            "type": "User",
                        }
                    ],
                }
            ],
        }

    # Logger
    expected_messages = {
        (
            "%s synchronization failed due to max retries exceeded with url %s",
            "add_user_to_group",
            webhook.url,
        )
    }
    actual_messages = {args for args, _ in mock_error.call_args_list}
    assert expected_messages.issubset(actual_messages)

    # Status
    webhook.refresh_from_db()
    assert webhook.status == "failure"


def test_utils_webhooks_add_user_to_group_authorization():
    """Secret token should be passed in authorization header when set."""
    user = factories.UserFactory()
    access = factories.TeamAccessFactory(user=user)
    webhook = factories.TeamWebhookFactory(team=access.team, secret="123")

    with responses.RequestsMock() as rsps:
        # Ensure successful response by scim provider using "responses":
        rsps.add(
            rsps.PATCH,
            re.compile(r".*/Groups/.*"),
            body="{}",
            status=200,
            content_type="application/json",
        )

        scim_synchronizer.add_user_to_group(access.team, access.user)
        assert rsps.calls[0].request.url == webhook.url

        # Check headers
        headers = rsps.calls[0].request.headers
        assert headers["Authorization"] == "Bearer 123"
        assert headers["Content-Type"] == "application/json"

    # Status
    webhook.refresh_from_db()
    assert webhook.status == "success"
