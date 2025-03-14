"""Tests the core application loads the management command as tasks."""

from unittest.mock import patch

from people.celery_app import app as celery_app


def test_fill_organization_metadata_as_task(settings):
    """Check the fill_organization_metadata command is loaded as a task."""
    # Verify the command is configured to be loaded as a task
    assert "fill_organization_metadata" in settings.MANAGEMENT_COMMAND_AS_TASK

    # The task should be registered in the format "app_name.command_name"
    task_name = "core.fill_organization_metadata"
    assert task_name in celery_app.tasks

    # Test that the task can be executed properly
    with patch("core.apps.call_command") as mock_call_command:
        # Get the registered task
        task = celery_app.tasks[task_name]

        # Execute the task
        result = task("arg1", "arg2", kwarg1="value1", kwarg2="value2")

        # Verify call_command was called with the correct command name
        mock_call_command.assert_called_once()
        assert mock_call_command.call_args[0][0] == "fill_organization_metadata"
        assert mock_call_command.call_args[0][1] == "arg1"
        assert mock_call_command.call_args[0][2] == "arg2"
        assert mock_call_command.call_args[1]["kwarg1"] == "value1"
        assert mock_call_command.call_args[1]["kwarg2"] == "value2"

        # Verify the task returns a dictionary with stdout and stderr
        assert isinstance(result, dict)
        assert "stdout" in result
        assert "stderr" in result
