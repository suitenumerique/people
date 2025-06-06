# ruff: noqa: S311, S106
"""create_demo management command"""

import logging
import random
import time
from collections import defaultdict
from uuid import uuid4

from django import db
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from faker import Faker
from oauth2_provider.models import Application
from treebeard.mp_tree import MP_Node

from core import models

from demo import defaults
from mailbox_manager import models as mailbox_models
from mailbox_manager.enums import (
    MailboxStatusChoices,
    MailDomainRoleChoices,
    MailDomainStatusChoices,
)

fake = Faker()

logger = logging.getLogger("people.commands.demo.create_demo")


def random_true_with_probability(probability):
    """return True with the requested probability, False otherwise."""
    return random.random() < probability


class BulkQueue:
    """A utility class to create Django model instances in bulk by just pushing to a queue."""

    BATCH_SIZE = 20000

    def __init__(self, stdout, *args, **kwargs):
        """Define the queue as a dict of lists."""
        self.queue = defaultdict(list)
        self.stdout = stdout

    def _bulk_create(self, objects):
        """Actually create instances in bulk in the database."""
        if not objects:
            return

        objects_model = objects[0]._meta.model  # noqa: SLF001
        if issubclass(objects_model, MP_Node):
            # For treebeard models, we need to create the tree structure
            # in a specific way. This is not perfect but it works for the
            # current use case.
            model_fields = {
                field
                for field in objects_model._meta.concrete_fields  # noqa: SLF001
                if field.name not in {"depth", "numchild", "path"}
            }
            bulk_data = [
                {
                    "data": {
                        field.name: field.value_from_object(obj)
                        for field in model_fields
                        if field.value_from_object(obj)
                    }
                }
                for obj in objects
            ]
            objects_model.load_bulk(bulk_data)
        else:
            objects_model.objects.bulk_create(
                objects,
                ignore_conflicts=False,
            )

        # In debug mode, Django keeps query cache which creates a memory leak in this case
        db.reset_queries()
        self.queue[objects[0]._meta.model.__name__] = []  # noqa: SLF001

    def push(self, obj):
        """Add a model instance to queue to that it gets created in bulk."""
        objects = self.queue[obj._meta.model.__name__]  # noqa: SLF001
        objects.append(obj)
        if len(objects) > self.BATCH_SIZE:
            self._bulk_create(objects)
            self.stdout.write(".", ending="")

    def flush(self):
        """Flush the queue after creating the remaining model instances."""
        for objects in self.queue.values():
            self._bulk_create(objects)


class Timeit:
    """A utility context manager/method decorator to time execution."""

    total_time = 0

    def __init__(self, stdout, sentence=None):
        """Set the sentence to be displayed for timing information."""
        self.sentence = sentence
        self.start = None
        self.stdout = stdout

    def __call__(self, func):
        """Behavior on call for use as a method decorator."""

        def timeit_wrapper(*args, **kwargs):
            """wrapper to trigger/stop the timer before/after function call."""
            self.__enter__()
            result = func(*args, **kwargs)
            self.__exit__(None, None, None)
            return result

        return timeit_wrapper

    def __enter__(self):
        """Start timer upon entering context manager."""
        self.start = time.perf_counter()
        if self.sentence:
            self.stdout.write(self.sentence, ending=".")

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Stop timer and display result upon leaving context manager."""
        if exc_type is not None:
            raise exc_type(exc_value)
        end = time.perf_counter()
        elapsed_time = end - self.start
        if self.sentence:
            self.stdout.write(f" Took {elapsed_time:g} seconds")

        self.__class__.total_time += elapsed_time
        return elapsed_time


def create_oidc_people_idp_client():
    """Configure the OIDC client for the People Identity Provider if missing."""
    try:
        Application.objects.get(client_id="people-idp")
    except Application.DoesNotExist:
        application = Application(
            client_id="people-idp",
            client_secret="local-tests-only",
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            name="People Identity Provider",
            algorithm=Application.RS256_ALGORITHM,
            redirect_uris="http://localhost:8083/realms/people/broker/oidc-people-local/endpoint",
            skip_authorization=True,
        )
        application.clean()
        application.save()


def create_oidc_people_idp_client_user():
    """Provide a user for the People Identity Provider OIDC client."""
    organization, _created = models.Organization.objects.get_or_create(
        name="13002526500013",
        registration_id_list=["13002526500013"],
    )
    mail_domain, _created = mailbox_models.MailDomain.objects.get_or_create(
        name="example.com",
        organization=organization,
        status=MailDomainStatusChoices.ENABLED,
        support_email="support@example.com",
    )
    _mailbox, _created = mailbox_models.Mailbox.objects.get_or_create(
        first_name="IdP User",
        last_name="E2E",
        domain=mail_domain,
        local_part="user-e2e",
        status=MailboxStatusChoices.ENABLED,
        password=make_password("password-user-e2e"),
        secondary_email="not-used@example.com",
    )


def create_demo(stdout):  # pylint: disable=too-many-locals
    """
    Create a database with demo data for developers to work in a realistic environment.
    The code is engineered to create a huge number of objects fast.
    """

    queue = BulkQueue(stdout)

    with Timeit(stdout, "Creating users"):
        for i in range(defaults.NB_OBJECTS["users"]):
            queue.push(
                models.User(
                    sub=uuid4(),
                    email=f"user{i:d}@example.com" if random.random() < 0.97 else None,
                    name=fake.name() if random.random() < 0.97 else None,
                    password="!",
                    is_superuser=False,
                    is_active=True,
                    is_staff=False,
                    language=random.choice(settings.LANGUAGES)[0],
                )
            )
        # this is a quick fix to fix e2e tests
        # tests needs some no random data
        organization, _created = models.Organization.objects.get_or_create(
            name="13002526500013",
            registration_id_list=["13002526500013"],
        )
        queue.push(
            models.User(
                sub=uuid4(),
                email="monique.test@example.com",
                name="Monique Test",
                password="!",
                is_superuser=False,
                is_active=True,
                is_staff=False,
                organization=organization,
                language=random.choice(settings.LANGUAGES)[0],
            )
        )
        queue.push(
            models.User(
                sub=uuid4(),
                email="jeanne.test@example.com",
                name="Jean Test",
                password="!",
                is_superuser=False,
                is_active=True,
                is_staff=False,
                organization=organization,
                language=random.choice(settings.LANGUAGES)[0],
            )
        )
        queue.push(
            models.User(
                sub=uuid4(),
                email="jean.somethingelse@example.com",
                name="Jean Something",
                password="!",
                is_superuser=False,
                is_active=True,
                is_staff=False,
                language=random.choice(settings.LANGUAGES)[0],
            )
        )

        queue.flush()

    with Timeit(stdout, "Creating teams"):
        for i in range(defaults.NB_OBJECTS["teams"]):
            queue.push(
                models.Team(
                    name=f"Team {i:d}",
                )
            )
        queue.flush()

    with Timeit(stdout, "Creating team accesses"):
        teams_ids = list(models.Team.objects.values_list("id", flat=True))
        users_ids = list(models.User.objects.values_list("id", flat=True))
        for team_id in teams_ids:
            for user_id in random.sample(
                users_ids,
                random.randint(1, defaults.NB_OBJECTS["max_users_per_team"]),
            ):
                role = random.choice(models.RoleChoices.choices)
                queue.push(
                    models.TeamAccess(team_id=team_id, user_id=user_id, role=role[0])
                )
        queue.flush()

    with Timeit(stdout, "Creating domains"):
        for i in range(defaults.NB_OBJECTS["domains"]):
            name = fake.domain_name().replace(".", f"-i{i:d}.")

            queue.push(
                mailbox_models.MailDomain(
                    name=name,
                    # slug should be automatic but bulk_create doesn't use save
                    slug=slugify(name),
                    status=random.choice(MailDomainStatusChoices.values),
                    support_email="support@example.com",
                )
            )
        queue.flush()

    with Timeit(stdout, "Creating accesses to domains"):
        domains_ids = list(
            mailbox_models.MailDomain.objects.values_list("id", flat=True)
        )
        for domain_id in domains_ids:
            queue.push(
                mailbox_models.MailDomainAccess(
                    domain_id=domain_id,
                    user_id=random.choice(users_ids),
                    role=models.RoleChoices.OWNER,
                )
            )

        queue.flush()

    with Timeit(stdout, "Creating specific users"):
        # ⚠️ Warning: this users also need to be created in the keycloak
        # realm.json AND the OIDC setting to fallback on user email
        # should be set to True, because we don't pilot the sub.
        for role in models.RoleChoices.values:
            team_user = models.User(
                sub=uuid4(),
                email=f"e2e.team-{role}@example.com",
                name=f"E2E Group {role.capitalize()}",
                password="!",
                is_superuser=False,
                is_active=True,
                is_staff=False,
                language=random.choice(settings.LANGUAGES)[0],
            )
            queue.push(team_user)
            queue.push(
                models.TeamAccess(team_id=teams_ids[0], user_id=team_user.pk, role=role)
            )

        for role in models.RoleChoices.values:
            user_with_mail = models.User(
                sub=uuid4(),
                email=f"e2e.mail-{role}@example.com",
                name=f"E2E Mail {role.capitalize()}",
                password="!",
                is_superuser=False,
                is_active=True,
                is_staff=False,
                language=random.choice(settings.LANGUAGES)[0],
            )
            queue.push(user_with_mail)
            queue.push(
                mailbox_models.MailDomainAccess(
                    domain_id=domains_ids[0],
                    user_id=user_with_mail.pk,
                    role=role,
                )
            )

        for team_role in models.RoleChoices.values:
            for domain_role in models.RoleChoices.values:
                team_mail_user = models.User(
                    sub=uuid4(),
                    email=f"e2e.team-{team_role}-mail-{domain_role}@example.com",
                    name=f"E2E Group {team_role.capitalize()} Mail {domain_role.capitalize()}",
                    password="!",
                    is_superuser=False,
                    is_active=True,
                    is_staff=False,
                    language=random.choice(settings.LANGUAGES)[0],
                )
                queue.push(team_mail_user)
                queue.push(
                    models.TeamAccess(
                        team_id=teams_ids[0], user_id=team_mail_user.pk, role=team_role
                    )
                )
                queue.push(
                    mailbox_models.MailDomainAccess(
                        domain_id=domains_ids[0],
                        user_id=team_mail_user.pk,
                        role=domain_role,
                    )
                )

        queue.flush()

        # Enabled domain for 2E2 tests
        enabled_domain, _created = mailbox_models.MailDomain.objects.get_or_create(
            name="enabled-domain.com",
            status=MailDomainStatusChoices.ENABLED,
            support_email="support@enabled-domain.com",
        )
        domain_owner = models.User.objects.get(email="e2e.mail-owner@example.com")
        mailbox_models.MailDomainAccess.objects.get_or_create(
            domain=enabled_domain,
            user=domain_owner,
            role=MailDomainRoleChoices.OWNER,
        )

    # OIDC configuration
    if settings.OAUTH2_PROVIDER.get("OIDC_ENABLED", False):
        stdout.write("Creating OIDC client for People Identity Provider")
        create_oidc_people_idp_client()
        create_oidc_people_idp_client_user()


class Command(BaseCommand):
    """A management command to create a demo database."""

    help = __doc__

    def add_arguments(self, parser):
        """Add argument to require forcing execution when not in debug mode."""
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            default=False,
            help="Force command execution despite DEBUG is set to False",
        )

    def handle(self, *args, **options):
        """Handling of the management command."""
        if not settings.DEBUG and not options["force"]:
            raise CommandError(
                (
                    "This command is not meant to be used in production environment "
                    "except you know what you are doing, if so use --force parameter"
                )
            )

        create_demo(self.stdout)
