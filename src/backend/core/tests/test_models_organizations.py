"""
Unit tests for the Organization model
"""

from django.core.exceptions import ValidationError

import pytest

from core import factories, models

pytestmark = pytest.mark.django_db


def test_models_organization_str():
    """The str representation should be the organization's name."""
    organization = factories.OrganizationFactory(
        name="HAL 9000", registration_id_list=["12345678901234"]
    )
    assert str(organization) == f"HAL 9000 (# {organization.pk})"


def test_models_organization_constraints():
    """It should not be possible to create an organization."""
    organization = factories.OrganizationFactory(
        registration_id_list=["12345678901234"], domain_list=["hal9000.com"]
    )

    with pytest.raises(ValidationError):
        models.Organization.objects.create(name="HAL 9000")

    with pytest.raises(ValidationError):
        models.Organization.objects.create(
            name="HAL 9000",
            registration_id_list=[
                organization.registration_id_list[0],
                "12345678901235",
            ],
        )

    with pytest.raises(ValidationError):
        models.Organization.objects.create(
            name="HAL 9000", domain_list=[organization.domain_list[0], "hal9001.com"]
        )


def test_models_organization_get_or_create_from_user_claims_no_kwargs():
    """It should fail."""
    with pytest.raises(ValueError):
        models.Organization.objects.get_or_create_from_user_claims()


def test_models_organization_get_or_create_from_user_claims_with_registration_id():
    """It should create an organization with a registration ID number."""
    organization, created = models.Organization.objects.get_or_create_from_user_claims(
        registration_id="12345678901234"
    )
    assert created is True
    assert organization.registration_id_list == ["12345678901234"]
    assert organization.domain_list == []

    same_organization, created = (
        models.Organization.objects.get_or_create_from_user_claims(
            registration_id="12345678901234"
        )
    )
    assert created is False
    assert organization == same_organization
    assert same_organization.registration_id_list == ["12345678901234"]
    assert same_organization.domain_list == []


def test_models_organization_get_or_create_from_user_claims_with_domain():
    """It should create an organization with a domain."""
    organization, created = models.Organization.objects.get_or_create_from_user_claims(
        domain="hal9000.com"
    )
    assert created is True
    assert organization.registration_id_list == []
    assert organization.domain_list == ["hal9000.com"]

    same_organization, created = (
        models.Organization.objects.get_or_create_from_user_claims(domain="hal9000.com")
    )
    assert created is False
    assert organization == same_organization
    assert same_organization.registration_id_list == []
    assert same_organization.domain_list == ["hal9000.com"]


def test_models_organization_get_or_create_from_user_claims_with_registration_id_and_domain():
    """It should create an organization with a registration ID number."""
    organization, created = models.Organization.objects.get_or_create_from_user_claims(
        registration_id="12345678901234", domain="hal9000.com"
    )
    assert created is True
    assert organization.registration_id_list == ["12345678901234"]
    assert organization.domain_list == []

    same_organization, created = (
        models.Organization.objects.get_or_create_from_user_claims(
            registration_id="12345678901234", domain="hal9000.com"
        )
    )
    assert created is False
    assert organization == same_organization
    assert same_organization.registration_id_list == ["12345678901234"]
    assert same_organization.domain_list == []


def test_models_organization_registration_id_validators():
    """
    Test the registration ID validators.

    This cannot be tested dynamically because the validators are set at model loading
    and this is not possible to reload the models on the fly. We therefore enforce the
    setting in Test environment.
    """
    models.Organization.objects.create(
        name="hu",
        registration_id_list=["12345678901234"],
    )

    with pytest.raises(ValidationError):
        models.Organization.objects.create(
            name="hi",
            registration_id_list=["a12345678912345"],
        )
