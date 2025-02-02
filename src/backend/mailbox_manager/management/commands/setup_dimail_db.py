"""Management command creating a  dimail-api container, for test purposes."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

import requests
from rest_framework import status

from mailbox_manager import enums
from mailbox_manager.models import MailDomain, MailDomainAccess

User = get_user_model()


DIMAIL_URL = settings.MAIL_PROVISIONING_API_URL
admin = {"username": "admin", "password": "admin"}
regie = {"username": "la_regie", "password": "password"}


class Command(BaseCommand):
    """
    Management command populate local dimail database, to ease dev
    """

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

        # Create a first superuser for dimail-api container. User creation is usually
        # protected behind admin rights but dimail allows to create a first user
        # when database is empty
        self.create_user(
            auth=(None, None),
            name=admin["username"],
            password=admin["password"],
            perms=[],
        )

        # Create Regie user, auth for all remaining requests
        # and your own dev
        self.create_user(
            auth=(admin["username"], admin["password"]),
            name=regie["username"],
            password=regie["password"],
            perms=["new_domain", "create_users", "manage_users"],
        )

        # we create a domain and add John Doe to it
        domain_name = "test.domain.com"
        domain = MailDomain.objects.get_or_create(
            name=domain_name,
            defaults={
                "status": enums.MailDomainStatusChoices.ENABLED,
                "support_email": f"support@{domain_name}",
            },
        )[0]
        self.create_domain(domain_name)

        # we create a dimail user for keycloak+regie user John Doe
        # This way, la Régie will be able to make request in the name of
        # this user
        try:
            people_base_user = User.objects.get(email="people@people.world")
        except User.DoesNotExist:
            self.stdout.write("people@people.world user not found", ending="\n")
        else:
            # create accesses for john doe
            self.create_user(name=people_base_user.sub)
            self.create_allows(people_base_user.sub, domain_name)
            MailDomainAccess.objects.get_or_create(
                user=people_base_user,
                domain=domain,
                defaults={"role": enums.MailDomainRoleChoices.OWNER},
            )

        if options["populate_from_people"]:
            self._populate_dimail_from_people()

        self.stdout.write("DONE", ending="\n")

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

    def create_domain(self, name, auth=(regie["username"], regie["password"])):
        """
        Send a request to create a new domain.
        """
        response = requests.post(
            url=f"{DIMAIL_URL}/domains/",
            json={
                "name": name,
                "context_name": "context",
                "features": ["webmail", "mailbox", "alias"],
            },
            auth=auth,
            timeout=10,
        )

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

    def create_allows(self, user, domain, auth=(regie["username"], regie["password"])):
        """
        Send a request to create a new allows between user and domain.
        """
        response = requests.post(
            url=f"{DIMAIL_URL}/allows/",
            json={
                "domain": domain,
                "user": user,
            },
            auth=auth,
            timeout=10,
        )

        if response.status_code == status.HTTP_201_CREATED:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Creating permissions for {user} on {domain} ........ OK"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"Creating permissions for {user} on {domain}\
                     ........ failed: {response.json()['detail']}"
                )
            )

    def _populate_dimail_from_people(self):
        self.stdout.write("Creating accounts from people database", ending="\n")

        user_to_create = set()
        domain_to_create = set()
        access_to_create = set()
        for mail_access in MailDomainAccess.objects.select_related(
            "domain", "user"
        ).all():
            user_to_create.add(mail_access.user)
            domain_to_create.add(mail_access.domain)
            access_to_create.add(mail_access)

        # create missing domains
        for domain in domain_to_create:
            # enforce domain status
            if domain.status != enums.MailDomainStatusChoices.ENABLED:
                self.stdout.write(
                    f"  - {domain.name} status {domain.status} -> ENABLED"
                )
                domain.status = enums.MailDomainStatusChoices.ENABLED
                domain.save()
            self.create_domain(domain.name)

        # create missing users
        for user in user_to_create:
            self.create_user(
                auth=(admin["username"], admin["password"]),
                name=user.sub,
                perms=[],  # no permission needed for "classic" users
            )

        # create missing accesses
        for access in access_to_create:
            self.create_allows(access.user.sub, access.domain.name)
