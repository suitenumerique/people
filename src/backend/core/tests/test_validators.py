"""
Test cases for core.validators module.
"""

from django.core.exceptions import ImproperlyConfigured
from django.core.validators import EmailValidator, RegexValidator

import pytest

from core.validators import get_field_validators_from_setting


def test_get_field_validators_from_setting_without_option(settings):
    """Test get_field_validators_from_setting without options."""
    settings.VALIDATOR_NO_OPTION = [
        {
            "NAME": "django.core.validators.EmailValidator",
        },
    ]

    validators = get_field_validators_from_setting("VALIDATOR_NO_OPTION")
    assert len(validators) == 1
    assert isinstance(validators[0], EmailValidator)


def test_get_field_validators_from_setting_with_option(settings):
    """Test get_field_validators_from_setting with options."""
    settings.REGEX_WITH_OPTIONS = [
        {
            "NAME": "django.core.validators.RegexValidator",
            "OPTIONS": {
                "regex": "[a-z][0-9]{14}",
            },
        },
    ]

    validators = get_field_validators_from_setting("REGEX_WITH_OPTIONS")
    assert len(validators) == 1
    assert isinstance(validators[0], RegexValidator)
    assert validators[0].regex.pattern == "[a-z][0-9]{14}"


def test_get_field_validators_from_setting_invalid_class_name(settings):
    """Test get_field_validators_from_setting with an invalid class name."""
    settings.INVALID_VALIDATORS = [
        {
            "NAME": "non.existent.Validator",
        },
    ]
    with pytest.raises(ImproperlyConfigured):
        get_field_validators_from_setting("INVALID_VALIDATORS")


def test_get_field_validators_from_setting_empty_setting(settings):
    """Test get_field_validators_from_setting with an empty setting."""
    settings.EMPTY_VALIDATORS = []
    validators = get_field_validators_from_setting("EMPTY_VALIDATORS")
    assert not validators
