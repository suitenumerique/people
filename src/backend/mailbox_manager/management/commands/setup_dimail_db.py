"""Management command creating a  dimail-api container, for test purposes."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

import requests
from rest_framework import status

User = get_user_model()


DIMAIL_URL = "http://host.docker.internal:8001"
admin = {"username": "admin", "password": "admin"}
regie = {"username": "la_regie", "password": "password"}


class Command(BaseCommand):
    """
    Management command populate local dimail database, to ease dev
    """

    help = "Populate local dimail database, for dev purposes."

    def handle(self, *args, **options):
        """Handling of the management command."""
        if not settings.DEBUG:
            raise CommandError(
                ("This command is meant to run in local dev environment.")
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

        # we create a dimail user for keycloak+regie user John Doe
        # This way, la Régie will be able to make request in the name of
        # this user
        people_base_user = User.objects.get(name="John Doe")
        self.create_user(name=people_base_user.sub, password="whatever")  # noqa S106

        # we create a domain and add John Doe to it
        domain_name = "test.domain.com"
        self.create_domain(domain_name)
        self.create_allows(people_base_user.sub, domain_name)

        self.stdout.write("DONE", ending="\n")

    def create_user(
        self,
        name,
        password,
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
