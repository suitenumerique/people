"""Test Team synchronization webhooks : focus on matrix client."""

import json
import logging
import re

import pytest
import responses
from rest_framework import status

from core import factories
from core.enums import WebhookProtocolChoices
from core.tests.fixtures import matrix
from core.utils.webhooks import webhooks_synchronizer

pytestmark = pytest.mark.django_db


## INVITE
@responses.activate
def test_matrix_webhook__invite_user_to_room_forbidden(caplog):
    """Cannot invite when Matrix returns forbidden. This might mean the user is an admin."""
    caplog.set_level(logging.INFO)

    user = factories.UserFactory()
    webhook = factories.TeamWebhookFactory(
        protocol=WebhookProtocolChoices.MATRIX,
        url="https://www.matrix.org/#/room/room_id:home_server",
        secret="secretaccesstoken",
    )

    # Mock successful responses
    error = matrix.mock_kick_user_forbidden(user)
    responses.post(
        re.compile(r".*/join"),
        body=str(matrix.mock_join_room_successful),
        status=status.HTTP_200_OK,
    )
    responses.post(
        re.compile(r".*/invite"),
        body=str(error["message"]),
        status=error["status_code"],
    )
    webhooks_synchronizer.invite_user_to_room(team=webhook.team, user=user)


@responses.activate
def test_matrix_webhook__invite_user_to_room_already_in_room(caplog):
    """If user is already in room, webhooks should be set to success."""
    caplog.set_level(logging.INFO)

    user = factories.UserFactory()
    webhook = factories.TeamWebhookFactory(
        protocol=WebhookProtocolChoices.MATRIX,
        url="https://www.matrix.org/#/room/room_id:home_server",
        secret="secretaccesstoken",
    )

    # Mock successful responses
    responses.post(
        re.compile(r".*/join"),
        body=str(matrix.mock_join_room_successful("room_id")["message"]),
        status=matrix.mock_join_room_successful("room_id")["status_code"],
    )
    responses.post(
        re.compile(r".*/invite"),
        body=str(matrix.mock_invite_user_already_in_room(user)["message"]),
        status=matrix.mock_invite_user_already_in_room(user)["status_code"],
    )
    webhooks_synchronizer.invite_user_to_room(team=webhook.team, user=user)

    # Logger
    log_messages = [msg.message for msg in caplog.records]
    expected_messages = (
        f"invite_user_to_room synchronization succeeded with {webhook.url}"
    )
    assert expected_messages in log_messages

    # Status
    webhook.refresh_from_db()
    assert webhook.status == "success"


@responses.activate
def test_matrix_webhook__invite_user_to_room_success(caplog):
    """The user passed to the function should get invited."""
    caplog.set_level(logging.INFO)

    user = factories.UserFactory()
    webhook = factories.TeamWebhookFactory(
        protocol=WebhookProtocolChoices.MATRIX,
        url="https://www.matrix.org/#/room/room_id:home_server",
        secret="secretaccesstoken",
    )

    # Mock successful responses
    responses.post(
        re.compile(r".*/join"),
        body=str(matrix.mock_join_room_successful("room_id")["message"]),
        status=matrix.mock_join_room_successful("room_id")["status_code"],
    )
    responses.post(
        re.compile(r".*/invite"),
        body=str(matrix.mock_invite_successful()["message"]),
        status=matrix.mock_invite_successful()["status_code"],
    )
    webhooks_synchronizer.invite_user_to_room(team=webhook.team, user=user)

    # Check headers
    headers = responses.calls[0].request.headers
    assert webhook.secret in headers["Authorization"]

    # Payload sent to Matrix API
    assert json.loads(responses.calls[1].request.body) == {
        "user_id": f"@{user.email.replace('@', ':')}",
        "reason": f"User added to team {webhook.team} on People",
    }

    # Logger
    log_messages = [msg.message for msg in caplog.records]
    expected_messages = (
        f"invite_user_to_room synchronization succeeded with {webhook.url}"
    )
    assert expected_messages in log_messages

    # Status
    webhook.refresh_from_db()
    assert webhook.status == "success"


## KICK
@responses.activate
def test_matrix_webhook__kick_user_from_room_not_in_room(caplog):
    """Webhook should report a success when user was already not in room."""
    caplog.set_level(logging.INFO)

    user = factories.UserFactory()
    webhook = factories.TeamWebhookFactory(
        protocol=WebhookProtocolChoices.MATRIX,
        url="https://www.matrix.org/#/room/room_id:home_server",
        secret="secretaccesstoken",
    )

    # Mock successful responses
    responses.post(
        re.compile(r".*/join"),
        body=str(matrix.mock_join_room_successful),
        status=status.HTTP_200_OK,
    )
    responses.post(
        re.compile(r".*/kick"),
        body=str(matrix.mock_kick_user_not_in_room()["message"]),
        status=matrix.mock_kick_user_not_in_room()["status_code"],
    )
    webhooks_synchronizer.kick_user_from_room(team=webhook.team, user=user)

    # Logger
    log_messages = [msg.message for msg in caplog.records]
    assert (
        f"kick_user_from_room synchronization succeeded with {webhook.url}"
        in log_messages
    )

    # Status
    webhook.refresh_from_db()
    assert webhook.status == "success"


@responses.activate
def test_matrix_webhook__kick_user_from_room_success(caplog):
    """The user passed to the function should get removed."""
    caplog.set_level(logging.INFO)

    user = factories.UserFactory()
    webhook = factories.TeamWebhookFactory(
        protocol=WebhookProtocolChoices.MATRIX,
        url="https://www.matrix.org/#/room/room_id:home_server",
        secret="secretaccesstoken",
    )

    responses.post(
        re.compile(r".*/join"),
        body=str(matrix.mock_join_room_successful),
        status=status.HTTP_200_OK,
    )
    responses.post(
        re.compile(r".*/kick"),
        body=str(matrix.mock_kick_successful),
        status=status.HTTP_200_OK,
    )
    webhooks_synchronizer.kick_user_from_room(team=webhook.team, user=user)

    # Payload sent to Matrix API
    assert json.loads(responses.calls[1].request.body) == {
        "user_id": f"@{user.email.replace('@', ':')}",
        "reason": f"User removed from team {webhook.team} on People",
    }

    # Logger
    log_messages = [msg.message for msg in caplog.records]
    expected_messages = (
        f"kick_user_from_room synchronization succeeded with {webhook.url}"
    )
    assert expected_messages in log_messages

    # Status
    webhook.refresh_from_db()
    assert webhook.status == "success"


@responses.activate
def test_matrix_webhook__kick_user_from_room_forbidden(caplog):
    """Cannot kick an admin."""
    caplog.set_level(logging.INFO)

    user = factories.UserFactory()
    webhook = factories.TeamWebhookFactory(
        protocol=WebhookProtocolChoices.MATRIX,
        url="https://www.matrix.org/#/room/room_id:home_server",
        secret="secretaccesstoken",
    )

    # Mock successful responses
    error = matrix.mock_kick_user_forbidden(user)
    responses.post(
        re.compile(r".*/join"),
        body=str(matrix.mock_join_room_successful),
        status=status.HTTP_200_OK,
    )
    responses.post(
        re.compile(r".*/kick"),
        body=str(error["message"]),
        status=error["status_code"],
    )
    webhooks_synchronizer.kick_user_from_room(team=webhook.team, user=user)

    # Logger
    log_messages = [msg.message for msg in caplog.records]
    assert (
        f"kick_user_from_room synchronization failed with {webhook.url}" in log_messages
    )

    # Status
    webhook.refresh_from_db()
    assert webhook.status == "failure"
