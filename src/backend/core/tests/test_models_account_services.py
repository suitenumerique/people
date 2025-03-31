"""
Unit tests for the Team model
"""

from django.core.exceptions import ValidationError
from django.test import override_settings

import pytest

from core import factories, models

pytestmark = pytest.mark.django_db


@override_settings(ACCOUNT_SERVICE_SCOPES=["la-suite-list-organizations-siret"])
def test_models_account_services_validate_scope():
    """Test that account service scopes are validated."""
    # Valid scope from settings.ACCOUNT_SERVICE_SCOPES
    account_service = factories.AccountServiceFactory(
        scopes=["la-suite-list-organizations-siret"]
    )
    assert account_service.scopes == ["la-suite-list-organizations-siret"]

    # Invalid scope
    with pytest.raises(ValidationError, match="Invalid scope: invalid-scope"):
        factories.AccountServiceFactory(scopes=["invalid-scope"])

    # Multiple scopes with one invalid
    with pytest.raises(ValidationError, match="Invalid scope: invalid-scope"):
        factories.AccountServiceFactory(
            scopes=["la-suite-list-organizations-siret", "invalid-scope"]
        )


@override_settings(ACCOUNT_SERVICE_SCOPES=["la-suite-list-organizations-siret"])
def test_models_account_services_name_null():
    """The "name" field should not be null."""
    with pytest.raises(ValidationError, match="This field cannot be null."):
        models.AccountService.objects.create(name=None)


@override_settings(ACCOUNT_SERVICE_SCOPES=["la-suite-list-organizations-siret"])
def test_models_account_services_name_empty():
    """The "name" field should not be empty."""
    with pytest.raises(ValidationError, match="This field cannot be blank."):
        models.AccountService.objects.create(name="")
