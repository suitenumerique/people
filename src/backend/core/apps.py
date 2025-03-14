"""People Core application"""

import logging

from django.apps import AppConfig
from django.conf import settings
from django.core.management import call_command, get_commands
from django.utils.translation import gettext_lazy as _

from core.utils.io import TeeStringIO

from people.celery_app import app as celery_app

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    """Configuration class for the People core app."""

    name = "core"
    app_label = "core"
    verbose_name = _("People core application")

    def ready(self):
        """
        Register management command which are enabled via MANAGEMENT_COMMAND_AS_TASK setting.
        """
        for command_name in settings.MANAGEMENT_COMMAND_AS_TASK:
            # Check if the command is a valid management command
            try:
                app_name = get_commands()[command_name]
            except KeyError:
                logging.error(
                    "Command %s is not a valid management command.", command_name
                )
                continue

            command_full_name = ".".join([app_name, command_name])

            # Create a closure to capture the current value of command_full_name and command_name
            def create_task(cmd_name, cmd_full_name):
                @celery_app.task(name=cmd_full_name)
                def task_wrapper(*command_args, **command_options):
                    stdout = TeeStringIO(logging.getLogger(cmd_full_name).info)
                    stderr = TeeStringIO(logging.getLogger(cmd_full_name).error)

                    call_command(
                        cmd_name,
                        *command_args,
                        no_color=True,
                        stdout=stdout,
                        stderr=stderr,
                        **command_options,
                    )

                    stdout.seek(0)
                    stderr.seek(0)
                    return {
                        "stdout": str(stdout.read()),
                        "stderr": str(stderr.read()),
                    }

                return task_wrapper

            # Create the task with the current values
            create_task(command_name, command_full_name)
