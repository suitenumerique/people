"""Factories for creating token exchange related model instances for testing."""

import factory.fuzzy
from faker import Faker
from pytz import UTC

from . import models

fake = Faker()


class ExchangedTokenFactory(factory.django.DjangoModelFactory):
    """A factory to create ExchangedToken instances for testing."""

    class Meta:
        model = models.ExchangedToken

    token = factory.LazyFunction(lambda: fake.uuid4())
    token_type = factory.fuzzy.FuzzyChoice(models.TokenTypeChoices.values)
    jwt_kid = None
    subject_sub = factory.LazyFunction(lambda: fake.uuid4())
    subject_email = factory.LazyFunction(lambda: fake.email())
    audiences = factory.LazyFunction(lambda: [fake.domain_word() for _ in range(3)])
    scope = "openid email profile"
    grants = None
    expires_at = factory.LazyFunction(
        lambda: fake.date_time_between(start_date="+1d", end_date="+30d", tzinfo=UTC)
    )
    subject_token_jti = factory.LazyFunction(lambda: fake.uuid4())
    subject_token_scope = "openid email profile"  # noqa: S105


class ExpiredExchangedTokenFactory(ExchangedTokenFactory):
    """A factory to create expired ExchangedToken instances for testing."""

    expires_at = factory.LazyFunction(
        lambda: fake.date_time_between(start_date="-30d", end_date="-1d", tzinfo=UTC)
    )


class ServiceProviderCredentialsFactory(factory.django.DjangoModelFactory):
    """Allow a ServiceProvider to authenticate against the token exchange endpoint."""

    class Meta:
        model = models.ServiceProviderCredentials

    service_provider = factory.SubFactory("core.factories.ServiceProviderFactory")
    client_id = factory.LazyFunction(lambda: fake.uuid4())
    client_secret = factory.LazyFunction(lambda: fake.uuid4())


class TokenExchangeRuleFactory(factory.django.DjangoModelFactory):
    """Factory for creating TokenExchangeRule instances."""

    class Meta:
        model = models.TokenExchangeRule

    source_service = factory.SubFactory("core.factories.ServiceProviderFactory")
    target_service = factory.SubFactory("core.factories.ServiceProviderFactory")
    is_active = True


class ScopeGrantFactory(factory.django.DjangoModelFactory):
    """Factory for creating ScopeGrant instances."""

    class Meta:
        model = models.ScopeGrant

    rule = factory.SubFactory(TokenExchangeRuleFactory)
    source_scope = factory.LazyFunction(lambda: fake.word())
    granted_scope = factory.LazyFunction(lambda: fake.word())
    throttle_rate = None


class ActionScopeFactory(factory.django.DjangoModelFactory):
    """Factory for creating ActionScope instances."""

    class Meta:
        model = models.ActionScope

    name = factory.Sequence(lambda n: f"action_{n}")
    description = factory.LazyFunction(lambda: fake.sentence())


class ActionScopeGrantFactory(factory.django.DjangoModelFactory):
    """Factory for creating ActionScopeGrant instances."""

    class Meta:
        model = models.ActionScopeGrant

    action = factory.SubFactory(ActionScopeFactory)
    target_service = factory.SubFactory("core.factories.ServiceProviderFactory")
    granted_scope = factory.LazyFunction(lambda: fake.word())
    throttle_rate = None


class TokenExchangeActionPermissionFactory(factory.django.DjangoModelFactory):
    """Factory for creating TokenExchangeActionPermission instances."""

    class Meta:
        model = models.TokenExchangeActionPermission

    rule = factory.SubFactory(TokenExchangeRuleFactory)
    action = factory.SubFactory(ActionScopeFactory)
    required_source_scope = ""
