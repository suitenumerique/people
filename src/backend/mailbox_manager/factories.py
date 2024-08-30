"""
Mailbox manager application factories
"""

import re

from django.utils.text import slugify

import factory.fuzzy
import responses
from faker import Faker
from rest_framework import status

from core import factories as core_factories
from core import models as core_models

from mailbox_manager import enums, models

fake = Faker()


class MailDomainFactory(factory.django.DjangoModelFactory):
    """A factory to create mail domain. Please not this is a factory to create mail domain with
    default values. So the status is pending and no mailbox can be created from it,
    until the mail domain is enabled."""

    class Meta:
        model = models.MailDomain
        django_get_or_create = ("name",)
        skip_postgeneration_save = True

    name = factory.Faker("domain_name")
    slug = factory.LazyAttribute(lambda o: slugify(o.name))

    @factory.post_generation
    def users(self, create, extracted, **kwargs):
        """Add users to domain from a given list of users with or without roles."""
        if not create or not extracted:
            return
        for user_entry in extracted:
            if isinstance(user_entry, core_models.User):
                MailDomainAccessFactory(domain=self, user=user_entry)
            else:
                MailDomainAccessFactory(
                    domain=self, user=user_entry[0], role=user_entry[1]
                )


class MailDomainEnabledFactory(MailDomainFactory):
    """A factory to create mail domain enabled."""

    status = enums.MailDomainStatusChoices.ENABLED


class MailDomainAccessFactory(factory.django.DjangoModelFactory):
    """A factory to create mail domain accesses."""

    class Meta:
        model = models.MailDomainAccess

    user = factory.SubFactory(core_factories.UserFactory)
    domain = factory.SubFactory(MailDomainEnabledFactory)
    role = factory.fuzzy.FuzzyChoice(
        [r[0] for r in enums.MailDomainRoleChoices.choices]
    )


class MailboxFactory(factory.django.DjangoModelFactory):
    """A factory to create mailboxes for a mail domain."""

    class Meta:
        model = models.Mailbox

    first_name = factory.Faker("first_name", locale="fr_FR")
    last_name = factory.Faker("last_name", locale="de_DE")

    local_part = factory.LazyAttribute(
        lambda a: f"{slugify(a.first_name)}.{slugify(a.last_name)}"
    )
    domain = factory.SubFactory(MailDomainEnabledFactory)
    secondary_email = factory.Faker("email")

    @classmethod
    def _create(cls, model_class, *args, use_mock=True, **kwargs):
        domain = kwargs["domain"]
        if use_mock and isinstance(domain, models.MailDomain):
            with responses.RequestsMock() as rsps:
                # Ensure successful response using "responses":
                rsps.add(
                    rsps.GET,
                    re.compile(r".*/token/"),
                    body='{"access_token": "domain_owner_token"}',
                    status=status.HTTP_200_OK,
                    content_type="application/json",
                )
                rsps.add(
                    rsps.POST,
                    re.compile(
                        rf".*/domains/{domain.name}/mailboxes/{kwargs['local_part']}"
                    ),
                    body=str(
                        {
                            "email": f"{kwargs['local_part']}@{domain.name}",
                            "password": "newpass",
                            "uuid": "uuid",
                        }
                    ),
                    status=status.HTTP_201_CREATED,
                    content_type="application/json",
                )

                result = super()._create(model_class, *args, **kwargs)
        else:
            result = super()._create(model_class, *args, **kwargs)
        return result
