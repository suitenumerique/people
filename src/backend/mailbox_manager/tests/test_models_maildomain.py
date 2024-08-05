"""
Unit tests for the MailDomain model
"""

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.utils.text import slugify

import pytest

from core import factories as core_factories

from mailbox_manager import enums, factories

pytestmark = pytest.mark.django_db

# NAME FIELD


def test_models_mail_domain__domain_name_should_not_be_empty():
    """The domain name field should not be empty."""
    with pytest.raises(ValidationError, match="This field cannot be blank"):
        factories.MailDomainFactory(name="")


def test_models_mail_domain__domain_name_should_not_be_null():
    """The domain name field should not be null."""
    with pytest.raises(ValidationError, match="This field cannot be null."):
        factories.MailDomainFactory(name=None)


def test_models_mail_domain__slug_inferred_from_name():
    """Passed slug is ignored. Slug is automatically generated from name."""

    name = "N3w_D0main-Name$.com"
    domain = factories.MailDomainFactory(name=name, slug="something else")
    assert domain.slug == slugify(name)


# get_abilities


def test_models_maildomains_get_abilities_anonymous():
    """Check abilities returned for an anonymous user."""
    maildomain = factories.MailDomainFactory()
    abilities = maildomain.get_abilities(AnonymousUser())
    assert abilities == {
        "delete": False,
        "get": False,
        "patch": False,
        "put": False,
        "post": False,
        "manage_accesses": False,
    }


def test_models_maildomains_get_abilities_authenticated():
    """Check abilities returned for an authenticated user."""
    maildomain = factories.MailDomainFactory()
    abilities = maildomain.get_abilities(core_factories.UserFactory())
    assert abilities == {
        "delete": False,
        "get": False,
        "patch": False,
        "put": False,
        "post": False,
        "manage_accesses": False,
    }


def test_models_maildomains_get_abilities_owner():
    """Check abilities returned for the owner of a maildomain."""
    access = factories.MailDomainAccessFactory(role=enums.MailDomainRoleChoices.OWNER)
    abilities = access.domain.get_abilities(access.user)
    assert abilities == {
        "delete": True,
        "get": True,
        "patch": True,
        "put": True,
        "post": True,
        "manage_accesses": True,
    }


def test_models_maildomains_get_abilities_administrator():
    """Check abilities returned for the administrator of a maildomain."""
    access = factories.MailDomainAccessFactory(role=enums.MailDomainRoleChoices.ADMIN)
    abilities = access.domain.get_abilities(access.user)
    assert abilities == {
        "delete": False,
        "get": True,
        "patch": True,
        "put": True,
        "post": True,
        "manage_accesses": True,
    }


def test_models_maildomains_get_abilities_viewer():
    """Check abilities returned for the member of a mail domain. It's a viewer role."""
    access = factories.MailDomainAccessFactory(role=enums.MailDomainRoleChoices.VIEWER)
    abilities = access.domain.get_abilities(access.user)
    assert abilities == {
        "delete": False,
        "get": True,
        "patch": False,
        "put": False,
        "post": False,
        "manage_accesses": False,
    }
