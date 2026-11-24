"""
Core application factories
"""

from django.conf import settings
from django.contrib.auth.hashers import make_password

import factory.fuzzy
from faker import Faker

from core import models

fake = Faker()


class OrganizationFactory(factory.django.DjangoModelFactory):
    """Factory to create organizations for testing purposes."""

    name = factory.Faker("company")

    class Meta:
        model = models.Organization

    class Params:  # pylint: disable=missing-class-docstring
        with_registration_id = factory.Trait(
            registration_id_list=factory.List(
                [factory.Sequence(lambda n: f"{n:014d}")]
            ),
        )
        with_domain = factory.Trait(
            domain_list=factory.List([factory.Faker("domain_name")]),
        )


class OrganizationAccessFactory(factory.django.DjangoModelFactory):
    """Factory to create organization accesses for testing purposes."""

    class Meta:
        model = models.OrganizationAccess

    user = factory.SubFactory(
        "core.factories.UserFactory",
        organization=factory.SelfAttribute("..organization"),
    )
    organization = factory.SubFactory(
        "core.factories.OrganizationFactory", with_registration_id=True
    )
    role = factory.fuzzy.FuzzyChoice(models.OrganizationRoleChoices.values)


class UserFactory(factory.django.DjangoModelFactory):
    """A factory to create random users for testing purposes."""

    class Meta:
        model = models.User
        django_get_or_create = ("sub",)

    class Params:
        with_organization = factory.Trait(
            organization=factory.SubFactory(
                OrganizationFactory, with_registration_id=True
            ),
        )

    sub = factory.Sequence(lambda n: f"user{n!s}")
    email = factory.Faker("email")
    name = factory.Faker("name")
    language = factory.fuzzy.FuzzyChoice([lang[0] for lang in settings.LANGUAGES])
    password = make_password("password")


class ServiceProviderFactory(factory.django.DjangoModelFactory):
    """A factory to create service providers for testing purposes."""

    class Meta:
        model = models.ServiceProvider
        skip_postgeneration_save = True

    audience_id = factory.Faker("uuid4")

    @factory.post_generation
    def organizations(self, create, extracted, **kwargs):
        """Add organization to service provider from a given list."""
        if not create or not extracted:
            return
        self.organizations.set(extracted)


class AccountServiceFactory(factory.django.DjangoModelFactory):
    """A factory to create account services for testing purposes."""

    class Meta:
        model = models.AccountService

    name = factory.Sequence(lambda n: f"Account Service {n!s}")
    api_key = factory.Faker("uuid4")
