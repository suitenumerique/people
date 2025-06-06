"""Management command creating a  dimail-api container, for test purposes."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

import requests
from rest_framework import status

from mailbox_manager import enums
from mailbox_manager.models import MailDomain, MailDomainAccess
from mailbox_manager.utils.dimail import DimailAPIClient

User = get_user_model()


DIMAIL_URL = settings.MAIL_PROVISIONING_API_URL
admin = {"username": "admin", "password": "admin"}
regie = {"username": "la_regie", "password": "password"}


class Command(BaseCommand):
    """
    Management command populate local dimail database, to ease dev
    """

    client = DimailAPIClient()

    help = "Populate local dimail database, for dev purposes."

    def add_arguments(self, parser):
        """Add arguments to the command."""
        parser.add_argument(
            "--populate-from-people",
            action="store_true",
            help="Create accounts from already exising account in people database.",
        )

    def handle(self, *args, **options):
        """Handling of the management command."""
        # Allow only in local dev environment: debug or django-configuration is "local"
        if (
            not settings.DEBUG
            and str(settings.CONFIGURATION) != "people.settings.Local"
        ):
            raise CommandError(
                f"This command is not meant to run in {settings.CONFIGURATION} environment."
            )

        # Create a first superuser for dimail-api container.
        # User creation is usually protected behind admin rights
        # but dimail allows to create a first user when database is empty
        self.create_user(
            auth=("", ""),
            name=admin["username"],
            password=admin["password"],
            perms=[],
        )

        # Create Regie user,
        # auth for all remaining requests and your own local setup
        self.create_user(
            auth=(admin["username"], admin["password"]),
            name=regie["username"],
            password=regie["password"],
            perms=["new_domain", "create_users", "manage_users"],
        )

        # Create a test domain for local development
        try:
            people_base_user = User.objects.get(email="people@people.world")
        except User.DoesNotExist:
            self.stdout.write("people@people.world user not found", ending="\n")
        else:
            domain_name = "test.domain.com"
            domain = MailDomain.objects.get_or_create(
                name=domain_name,
                defaults={
                    "status": enums.MailDomainStatusChoices.ENABLED,
                    "support_email": f"support@{domain_name}",
                },
            )[0]
            self.create_domain(domain_name)
            # create accesses for john doe
            MailDomainAccess.objects.get_or_create(
                user=people_base_user,
                domain=domain,
                defaults={"role": enums.MailDomainRoleChoices.OWNER},
            )

        if options["populate_from_people"]:
            self._populate_dimail_from_people()

        self.stdout.write("DONE 🎉", ending="\n")

    def create_user(
        self,
        name,
        password="no",  # noqa S107
        perms=None,
        auth=(regie["username"], regie["password"]),
    ):
        """
        Send a request to create a new user.
        """

        response = requests.post(
            url=f"{DIMAIL_URL}/users/",
            json={
                "name": name,
                "password": password,
                "is_admin": name == admin["username"],
                "perms": perms or [],
            },
            auth=auth,
            timeout=10,
        )

        if response.status_code == status.HTTP_201_CREATED:
            self.stdout.write(self.style.SUCCESS(f"Creating user {name}......... OK"))
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"Creating user {name} ......... failed: {response.json()['detail']}"
                )
            )

    def create_domain(self, name):
        """
        Send a request to create a new domain using DimailAPIClient.
        """
        response = self.client.create_domain(name, request_user="setup_dimail_db.py")

        if response.status_code == status.HTTP_201_CREATED:
            self.stdout.write(
                self.style.SUCCESS(f"Creating domain '{name}' ........ OK")
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"Creating domain '{name}' ........ failed: {response.json()['detail']}"
                )
            )

    def _populate_dimail_from_people(self):
        """Populate dimail so that it reflects people's domains."""
        self.stdout.write("Creating domain from people database", ending="\n")

        # create missing domains
        for domain in MailDomain.objects.all():
            # enforce domain status
            if domain.status != enums.MailDomainStatusChoices.ENABLED:
                self.stdout.write(
                    f"  - {domain.name} status {domain.status} -> ENABLED"
                )
                domain.status = enums.MailDomainStatusChoices.ENABLED
                domain.save()
            self.create_domain(domain.name)
