"""
Mailbox manager application factories
"""

from django.contrib.auth.hashers import make_password
from django.utils.text import slugify

import factory.fuzzy
from faker import Faker

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
    support_email = factory.Faker("email")

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
    password = make_password("password")


class MailboxEnabledFactory(MailboxFactory):
    """A factory to create mailbox enabled."""

    status = enums.MailboxStatusChoices.ENABLED


class MailDomainInvitationFactory(factory.django.DjangoModelFactory):
    """A factory to create invitations for a user"""

    class Meta:
        model = models.MailDomainInvitation

    domain = factory.SubFactory(MailDomainEnabledFactory)
    email = factory.Faker("email")
    role = factory.fuzzy.FuzzyChoice(
        [role[0] for role in enums.MailDomainRoleChoices.choices]
    )
    issuer = factory.SubFactory(core_factories.UserFactory)
