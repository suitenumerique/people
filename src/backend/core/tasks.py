"""
Celery tasks for the core app.
"""

from django.conf import settings
from django.core.management import call_command

from people.celery_app import app as celery_app


@celery_app.task
def run_management_command(*, command_name, command_args, command_options):
    """
    Executes a Django management command from a Celery task.

    Args:
        command_name (str): Name of the management command to run
        command_args (list): List of positional arguments to pass to the command
        command_options (dict): Dictionary of keyword arguments to pass to the command

    Returns:
        None
    """
    if command_name not in settings.TASK_MANAGEMENT_COMMAND_ALLOWLIST:
        raise ValueError(
            f"Command {command_name} is not in the TASK_MANAGEMENT_COMMAND_ALLOWLIST"
        )

    call_command(command_name, *command_args, **command_options)
