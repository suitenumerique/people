"""
Mailbox manager application factories
"""

import factory.fuzzy
from faker import Faker

from core import factories as core_factories
from core import models as core_models

from mailbox_manager import models

fake = Faker()


class MailDomainFactory(factory.django.DjangoModelFactory):
    """A factory to create mail domain."""

    class Meta:
        model = models.MailDomain
        django_get_or_create = ("name",)
        skip_postgeneration_save = True

    name = factory.Faker("domain_name")

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


class MailDomainAccessFactory(factory.django.DjangoModelFactory):
    """A factory to create mail domain accesses."""

    class Meta:
        model = models.MailDomainAccess

    user = factory.SubFactory(core_factories.UserFactory)
    domain = factory.SubFactory(MailDomainFactory)
    role = factory.fuzzy.FuzzyChoice([r[0] for r in core_models.RoleChoices.choices])


class MailboxFactory(factory.django.DjangoModelFactory):
    """A factory to create mailboxes for mail domain members."""

    class Meta:
        model = models.Mailbox

    class Params:
        """Parameters for fields."""

        full_name = factory.Faker("name")

    local_part = factory.LazyAttribute(lambda a: a.full_name.lower().replace(" ", "."))
    domain = factory.SubFactory(MailDomainFactory)
    secondary_email = factory.Faker("email")
