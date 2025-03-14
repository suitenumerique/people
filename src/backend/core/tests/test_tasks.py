"""Tests for the core tasks module."""

from unittest.mock import patch

import pytest

from core.tasks import run_management_command

pytestmark = pytest.mark.django_db


@patch("core.tasks.call_command")
def test_calls_allowed_command(mock_call_command, settings):
    """Test that allowed commands are executed with call_command."""
    settings.TASK_MANAGEMENT_COMMAND_ALLOWLIST = ["allowed_command"]

    run_management_command(
        command_name="allowed_command",
        command_args=["arg1", "arg2"],
        command_options={"option1": "value1"},
    )

    mock_call_command.assert_called_once_with(
        "allowed_command", "arg1", "arg2", option1="value1"
    )


def test_raises_error_for_disallowed_command(settings):
    """Test that disallowed commands raise ValueError."""
    settings.TASK_MANAGEMENT_COMMAND_ALLOWLIST = []

    with pytest.raises(ValueError) as exc_info:
        run_management_command(
            command_name="disallowed_command", command_args=[], command_options={}
        )

    assert (
        "Command disallowed_command is not in the TASK_MANAGEMENT_COMMAND_ALLOWLIST"
        in str(exc_info.value)
    )
