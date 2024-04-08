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

    name = factory.Faker("domain_name")


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
