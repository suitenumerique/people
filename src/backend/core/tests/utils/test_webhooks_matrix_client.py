"""Test Team synchronization webhooks : focus on matrix client."""

import json
import logging
import re

from django.test import override_settings

import pytest
import responses
from rest_framework import status

from core import factories
from core.enums import WebhookProtocolChoices
from core.tests.fixtures import matrix
from core.utils.matrix import MatrixAPIClient
from core.utils.webhooks import webhooks_synchronizer

pytestmark = pytest.mark.django_db


## SEARCH
@responses.activate
def test_matrix_webhook__search_user_unknown(caplog):
    """When searching for a user in the Matrix federation but cannot find any,
    we invite a (future ?) user using user's email and room's server."""
    caplog.set_level(logging.INFO)

    user = factories.UserFactory()
    webhook = factories.TeamWebhookFactory(
        protocol=WebhookProtocolChoices.MATRIX,
        url="https://www.matrix.org/#/room/room_id:room_server.au",
        secret="secret-access-token",
    )

    client = MatrixAPIClient()
    # Mock successful responses
    responses.post(
        re.compile(r".*/search"),
        body=json.dumps(matrix.mock_search_empty()["message"]),
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
    response = client.get_user_id(user=user, webhook=webhook)
    assert response == f"@{user.email.replace('@', '-')}:room_server.au"


@responses.activate
def test_matrix_webhook__search_multiple_ids(caplog):
    """When searching for a user in Matrix federation,
    if user directory returns multiple ids, invite the first one."""
    caplog.set_level(logging.INFO)

    user = factories.UserFactory()
    webhook = factories.TeamWebhookFactory(
        protocol=WebhookProtocolChoices.MATRIX,
        url="https://www.matrix.org/#/room/room_id:room_server.au",
        secret="secret-access-token",
    )

    client = MatrixAPIClient()
    # Mock successful responses
    responses.post(
        re.compile(r".*/search"),
        body=json.dumps(matrix.mock_search_successful_multiple(user)["message"]),
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
    response = client.get_user_id(user=user, webhook=webhook)
    assert response == f"@{user.email.replace('@', '-')}:user_server1.com"


## INVITE
@responses.activate
def test_matrix_webhook__invite_user_to_room_forbidden(caplog):
    """Cannot invite when Matrix returns forbidden. This might mean the user is an admin."""
    caplog.set_level(logging.INFO)

    user = factories.UserFactory()
    webhook = factories.TeamWebhookFactory(
        protocol=WebhookProtocolChoices.MATRIX,
        url="https://www.matrix.org/#/room/room_id:home_server",
        secret="secret-access-token",
    )

    # Mock successful responses
    error = matrix.mock_kick_user_forbidden(user)
    responses.post(
        re.compile(r".*/join"),
        body=str(matrix.mock_join_room_successful),
        status=status.HTTP_200_OK,
    )
    responses.post(
        re.compile(r".*/search"),
        body=json.dumps(matrix.mock_search_successful(user)["message"]),
        status=matrix.mock_search_successful(user)["status_code"],
    )
    responses.post(
        re.compile(r".*/invite"),
        body=str(error["message"]),
        status=error["status_code"],
    )
    webhooks_synchronizer.add_user_to_group(team=webhook.team, user=user)


@responses.activate
def test_matrix_webhook__invite_user_to_room_already_in_room(caplog):
    """If user is already in room, webhooks should be set to success."""
    caplog.set_level(logging.INFO)

    user = factories.UserFactory()
    webhook = factories.TeamWebhookFactory(
        protocol=WebhookProtocolChoices.MATRIX,
        url="https://www.matrix.org/#/room/room_id:home_server",
        secret="secret-access-token",
    )

    # Mock successful responses
    responses.post(
        re.compile(r".*/join"),
        body=str(matrix.mock_join_room_successful("room_id")["message"]),
        status=matrix.mock_join_room_successful("room_id")["status_code"],
    )
    responses.post(
        re.compile(r".*/search"),
        body=json.dumps(matrix.mock_search_successful(user)["message"]),
        status=matrix.mock_search_successful(user)["status_code"],
    )
    responses.post(
        re.compile(r".*/invite"),
        body=str(matrix.mock_invite_user_already_in_room(user)["message"]),
        status=matrix.mock_invite_user_already_in_room(user)["status_code"],
    )
    webhooks_synchronizer.add_user_to_group(team=webhook.team, user=user)

    # Logger
    log_messages = [msg.message for msg in caplog.records]
    expected_messages = (
        f"add_user_to_group synchronization succeeded with {webhook.url}"
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
        secret="secret-access-token",
    )

    # Mock successful responses
    responses.post(
        re.compile(r".*/join"),
        body=str(matrix.mock_join_room_successful("room_id")["message"]),
        status=matrix.mock_join_room_successful("room_id")["status_code"],
    )
    responses.post(
        re.compile(r".*/search"),
        body=json.dumps(matrix.mock_search_successful(user)["message"]),
        status=matrix.mock_search_successful(user)["status_code"],
    )
    responses.post(
        re.compile(r".*/invite"),
        body=str(matrix.mock_invite_successful()["message"]),
        status=matrix.mock_invite_successful()["status_code"],
    )
    webhooks_synchronizer.add_user_to_group(team=webhook.team, user=user)

    # Check headers
    headers = responses.calls[0].request.headers
    assert webhook.secret in headers["Authorization"]

    # Check payloads sent to Matrix API
    assert json.loads(responses.calls[2].request.body) == {
        "user_id": f"@{user.email.replace('@', '-')}:user_server.com",
        "reason": f"User added to team {webhook.team} on People",
    }

    # Logger
    log_messages = [msg.message for msg in caplog.records]
    expected_messages = (
        f"add_user_to_group synchronization succeeded with {webhook.url}"
    )
    assert expected_messages in log_messages

    # Status
    webhook.refresh_from_db()
    assert webhook.status == "success"


@responses.activate
@override_settings(MATRIX_BOT_ACCESS_TOKEN="TCHAP_TOKEN")
def test_matrix_webhook__override_secret_for_tchap():
    """The user passed to the function should get invited."""
    user = factories.UserFactory()
    webhook = factories.TeamWebhookFactory(
        protocol=WebhookProtocolChoices.MATRIX,
        url="https://www.tchap.gouv.fr/#/room/room_id:home_server",
        secret=None,
    )

    # Mock successful responses
    responses.post(
        re.compile(r".*/join"),
        body=str(matrix.mock_join_room_successful("room_id")["message"]),
        status=matrix.mock_join_room_successful("room_id")["status_code"],
    )
    responses.post(
        re.compile(r".*/search"),
        body=json.dumps(matrix.mock_search_successful(user)["message"]),
        status=matrix.mock_search_successful(user)["status_code"],
    )
    responses.post(
        re.compile(r".*/invite"),
        body=str(matrix.mock_invite_successful()["message"]),
        status=matrix.mock_invite_successful()["status_code"],
    )
    webhooks_synchronizer.add_user_to_group(team=webhook.team, user=user)

    # Check headers
    headers = responses.calls[0].request.headers
    assert "TCHAP_TOKEN" in headers["Authorization"]

    # Check correctly inferred base url from room_id
    assert "matrix.home_server" in responses.calls[0].request.url


## KICK
@responses.activate
def test_matrix_webhook__kick_user_from_room_not_in_room(caplog):
    """Webhook should report a success when user was already not in room."""
    caplog.set_level(logging.INFO)

    user = factories.UserFactory()
    webhook = factories.TeamWebhookFactory(
        protocol=WebhookProtocolChoices.MATRIX,
        url="https://www.matrix.org/#/room/room_id:home_server",
        secret="secret-access-token",
    )

    # Mock successful responses
    responses.post(
        re.compile(r".*/join"),
        body=str(matrix.mock_join_room_successful),
        status=status.HTTP_200_OK,
    )
    responses.post(
        re.compile(r".*/search"),
        body=json.dumps(matrix.mock_search_successful(user)["message"]),
        status=matrix.mock_search_successful(user)["status_code"],
    )
    responses.post(
        re.compile(r".*/kick"),
        body=str(matrix.mock_kick_user_not_in_room()["message"]),
        status=matrix.mock_kick_user_not_in_room()["status_code"],
    )
    webhooks_synchronizer.remove_user_from_group(team=webhook.team, user=user)

    # Logger
    log_messages = [msg.message for msg in caplog.records]
    assert (
        f"remove_user_from_group synchronization succeeded with {webhook.url}"
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
        url="https://www.matrix.org/#/room/room_id:room_server",
        secret="secret-access-token",
    )

    responses.post(
        re.compile(r".*/join"),
        body=str(matrix.mock_join_room_successful),
        status=status.HTTP_200_OK,
    )
    responses.post(
        re.compile(r".*/search"),
        body=json.dumps(matrix.mock_search_successful(user)["message"]),
        status=matrix.mock_search_successful(user)["status_code"],
    )
    responses.post(
        re.compile(r".*/kick"),
        body=str(matrix.mock_kick_successful),
        status=status.HTTP_200_OK,
    )
    webhooks_synchronizer.remove_user_from_group(team=webhook.team, user=user)

    # Check payloads sent to Matrix API
    assert json.loads(responses.calls[2].request.body) == {
        "user_id": f"@{user.email.replace('@', '-')}:user_server.com",
        "reason": f"User removed from team {webhook.team} on People",
    }

    # Logger
    log_messages = [msg.message for msg in caplog.records]
    expected_messages = (
        f"remove_user_from_group synchronization succeeded with {webhook.url}"
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
        secret="secret-access-token",
    )

    # Mock successful responses
    error = matrix.mock_kick_user_forbidden(user)
    responses.post(
        re.compile(r".*/join"),
        body=str(matrix.mock_join_room_successful),
        status=status.HTTP_200_OK,
    )
    responses.post(
        re.compile(r".*/search"),
        body=json.dumps(matrix.mock_search_successful(user)["message"]),
        status=matrix.mock_search_successful(user)["status_code"],
    )
    responses.post(
        re.compile(r".*/kick"),
        body=str(error["message"]),
        status=error["status_code"],
    )
    webhooks_synchronizer.remove_user_from_group(team=webhook.team, user=user)

    # Logger
    log_messages = [msg.message for msg in caplog.records]
    assert (
        f"remove_user_from_group synchronization failed with {webhook.url}"
        in log_messages
    )

    # Status
    webhook.refresh_from_db()
    assert webhook.status == "failure"
