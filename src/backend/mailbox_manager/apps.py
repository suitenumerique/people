"""People additionnal application, to manage email adresses."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MailboxManagerConfig(AppConfig):
    """Configuration class for the Mailbox manager app."""

    name = "mailbox_manager"
    verbose_name = _("Mailbox manager")
    app_label = "mailbox_manager"

    def ready(self):
        """
        Import signals when the app is ready.
        """
        # pylint: disable=import-outside-toplevel, unused-import
        import mailbox_manager.signals  # noqa: PLC0415
