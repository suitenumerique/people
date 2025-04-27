"""Factories for the la suite plugin."""

from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from core import factories as core_factories

from plugins.la_suite import models


class OrganizationOneTimeTokenFactory(DjangoModelFactory):
    """Factory for the OrganizationOneTimeToken model."""

    organization = SubFactory(
        core_factories.OrganizationFactory, with_registration_id=True
    )
    key = Faker("uuid4")

    class Meta:
        model = models.OrganizationOneTimeToken
