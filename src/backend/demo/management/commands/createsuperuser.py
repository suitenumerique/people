"""
Management command overriding the "createsuperuser" command to allow creating users
with their email and no username.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    """
    Management command to create superusers from a username and a password for demo purposes.
    """

    help = "Create a superuser with a username and a password for demo purposes"

    def add_arguments(self, parser):
        """Define required arguments "username" and "password"."""
        parser.add_argument(
            "--username",
            help=("Username for the user."),
        )
        parser.add_argument(
            "--password",
            help="Password for the user.",
        )

    def handle(self, *args, **options):
        """
        Given an email and a password, create a superuser or upgrade the existing
        user to superuser status.
        """
        username = options.get("username")
        try:
            user = User.objects.get(sub=username)
        except User.DoesNotExist:
            user = User(sub=username)
            message = "Superuser created successfully."
        else:
            if user.is_superuser and user.is_staff:
                message = "Superuser already exists."
            else:
                message = "User already existed and was upgraded to superuser."

        user.is_superuser = True
        user.is_staff = True
        user.set_password(options["password"])
        user.save()

        self.stdout.write(self.style.SUCCESS(message))
